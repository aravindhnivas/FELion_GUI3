import os
import shutil
from os.path import dirname, isdir, isfile, join
from pathlib import Path as pt
from felionlib.utils.felionQt.utils.blit import BlitManager
from felionlib.utils.felionQt import felionQtWindow, QApplication
from felionlib.utils.FELion_definitions import var_find

from scipy.interpolate import interp1d
import numpy as np

###################################################################################################

def move(pathdir, x):
    shutil.move(join(pathdir, x), join(pathdir, "DATA", x))
    print(f"{x} moved to DATA folder", flush=True)
    return


class Create_Baseline:

    epsilon = 5
    def __init__(self, filename: pt, checkdir=True):

        self.fname = filename.stem
        self.felixfile = filename.name
        location = filename.parent

        attributes = {
            "data": None,
            "baseline": None,
            "redo_index": [],
            "undo_counter": 0,
            "redo_counter": 0,
            "removed_index": [],
            "felix_corrected": False,
            "baseline_corrected": False,
            "redo_datas": np.array([[], [], []]),
            "removed_datas": np.array([[], [], []]),
        }

        for keys, values in attributes.items():
            setattr(self, keys, values)

        self.opo = self.felixfile.endswith("ofelix")
        self.basefile = f"{self.fname}.base"
        if self.opo:
            self.basefile = f"{self.fname}.obase"

        self.powerfile = f"{self.fname}.pow"
        self.cfelix = f"{self.fname}.cfelix"
        folders = ["DATA", "EXPORT", "OUT"]

        if checkdir:
            back_dir = dirname(location)
            if set(folders).issubset(os.listdir(back_dir)):
                self.location = pt(back_dir)
            else:
                self.location = pt(location)

            os.chdir(self.location)

        else:
            self.location = location
            os.chdir(location)

        print(f"Current location: {self.location}")
        for dirs in folders:
            if not isdir(dirs):
                os.mkdir(dirs)
            if isfile(self.felixfile):
                move(self.location, self.felixfile)
            if isfile(self.basefile):
                move(self.location, self.basefile)
            if isfile(self.powerfile):
                move(self.location, self.powerfile)
        self.checkInf()
        self.felix_read_file()

        self.PPS = 5
        self.NUM_POINTS = 10

        if isfile(f"./DATA/{self.basefile}"):
            print(f"Basefile EXISTS: Opening existing basefile for baseline points")
            self.ReadBase()  # Read baseline file if exist else guess it
        else:
            print(f"Basefile doesn't EXISTS: Guessing baseline points")
            self.GuessBaseLine()

    def checkInf(self):

        print(f"Checking for error in {self.felixfile}")

        Inf = False
        with open(f"{self.location}/DATA/{self.felixfile}", "r") as f:
            info = f.readlines()

        info = np.array(info)

        for i, j in enumerate(info):
            if j.startswith("Inf"):
                info[i] = f"# {info[i]}"
                Inf = True

        if not Inf:
            print(f"No error found in {self.felixfile}")

        if Inf:
            print(f"Error found and correcting the error in {self.felixfile}")
            with open(f"./DATA/{self.felixfile}", "w") as f:
                for i in range(len(info)):
                    f.write(info[i])
            print(f"Error corrected in {self.felixfile}")

        print(f"Completed error checking process for {self.felixfile}")

    def felix_read_file(self):

        print(f"Reading {self.felixfile}")

        file = np.genfromtxt(f"./DATA/{self.felixfile}")
        if self.felixfile.endswith(".felix"):
            data = file[:, 0], file[:, 2], file[:, 3]
        elif self.felixfile.endswith(".cfelix"):
            data = file[:, 0], file[:, 1], file[:, 2]
        elif self.felixfile.endswith("ofelix"):
            data = file[:, 0], file[:, 1], file[:, 1]
        with open(f"./DATA/{self.felixfile}") as f:
            self.info = f.readlines()[-50:]
        self.data = np.take(data, data[0].argsort(), 1)

        print(f"{self.felixfile} read and data is taken for further processing")

    def ReadBase(self):

        file = np.genfromtxt(f"./DATA/{self.basefile}")
         
        self.xs, self.ys = file[:, 0], file[:, 1]
        
        with open(f"./DATA/{self.basefile}", "r") as f:
            self.interpol = f.readlines()[1].strip().split("=")[-1]
            print(f"{self.interpol=}", flush=True)
        print(f"{self.basefile} has been read for baseline points")

    def GuessBaseLine(self):
        PPS, NUM_POINTS = self.PPS, self.NUM_POINTS
        max_n = len(self.data[0]) - PPS
        if int(max_n / NUM_POINTS) == 0:
            max_n = NUM_POINTS = 2
        Bx, By = [self.data[0][0] - 0.1], [self.data[1][0]]
        print(f"Guessing baseline points\n max_n: {max_n}, max_n/NUM_POINTS: {int(max_n/NUM_POINTS)}")

        for i in range(0, max_n, int(max_n / NUM_POINTS)):
            x = self.data[0][i : i + PPS].mean()
            y = self.data[1][i : i + PPS].mean()
            Bx.append(x)
            By.append(y)
            
        Bx.append(self.data[0][-1] + 0.1)
        By.append(self.data[1][-1])
        self.interpol = "cubic"
        self.xs, self.ys = Bx, By
        self.xs = np.array(self.xs, dtype=float)
        self.ys = np.array(self.ys, dtype=float)
        print(f"Baseline points are guessed.")

    def InteractivePlots(self, widget: felionQtWindow) -> None:

        self.widget = widget
        
        (self.line,) = self.widget.ax.plot(
            self.xs, self.ys, marker="s", zorder=3, ls="", c=("b", "C1")[self.opo],
            markeredgecolor=("b", "C1")[self.opo], animated=True,
        )

        (self.funcLine,) = self.widget.ax.plot([], [], c=("b", "C1")[self.opo], zorder=3, animated=True)

        if not self.opo:
            res, b0, trap = var_find(f"{self.location}/DATA/{self.felixfile}")
            label = f"{self.felixfile}: Res:{res}; B0: {b0}ms; trap: {trap}ms"
        else:
            label = f"{self.felixfile}"

        (self.baseline_data,) = self.widget.ax.step(
            self.data[0], self.data[1], c="r", where="pre", zorder=2.5, ms=7,
            markeredgecolor="black", label=label, animated=True,
        )
        
        self.widget.canvas.mpl_connect("button_press_event", self.button_press_callback)
        self.widget.canvas.mpl_connect("key_press_event", self.key_press_callback)
        self.widget.canvas.mpl_connect("button_release_event", self.button_release_callback)
        self.widget.canvas.mpl_connect("motion_notify_event", self.motion_notify_callback)
        animated_artists = (self.baseline_data, self.line, self.funcLine)
        self.blit = BlitManager(self.widget.canvas, animated_artists)

        self.redraw_f_line()
        self._ind = None

    def redraw_f_line(self):

        try:
            Bx, By = np.array(self.line.get_data())
            self.inter_xs = np.arange(Bx.min(), Bx.max())
            f = interp1d(Bx, By, kind=self.interpol)
            self.funcLine.set_data((self.inter_xs, f(self.inter_xs)))
            self.blit.update()
        except Exception as err:
            return print(f"Error occured while redrawing baseline, {err}")

    def button_press_callback(self, event):
        "whenever a mouse button is pressed"
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        self._ind = self.get_ind_under_point(event)
        self.widget.canvas.setFocus()

    def key_press_callback(self, event):
        "whenever a key is pressed"

        if not event.inaxes:
            return

        elif event.key == "w":
            ind = self.get_ind_under_point(event)
            if ind is not None:
                xy = np.asarray(self.line.get_data())
                # makes average of few points around the cursor
                i = self.data[0].searchsorted(event.xdata)
                if i + self.PPS > self.data[0].size:
                    i = self.data[0].size - self.PPS
                xy[1][ind] = self.data[1][i : i + self.PPS].mean()
                self.line.set_data((xy[0], xy[1]))

        elif event.key == "d":
            ind = self.get_ind_under_point(event)
            if ind is not None:
                xy = np.asarray(self.line.get_data()).T
                xy = np.array([tup for i, tup in enumerate(xy) if i != ind])
                self.line.set_data((xy[:, 0], xy[:, 1]))

        elif event.key == "a":
            
            xy = np.asarray(self.line.get_data())
            xy = np.append(xy, [[event.xdata], [event.ydata]], axis=1)
            self.line.set_data((xy[0], xy[1]))

        elif event.key == "x":
            "To delete the unncessary points"

            new_data = self.data[:-1]
            index = self.get_index_under_basepoint(new_data, event.x, event.y)

            if index is not None:
                xy = np.asarray(self.data).T
                removed_datas = np.array([tup for i, tup in enumerate(xy) if i == index]).T
                self.removed_datas = np.append(self.removed_datas, removed_datas, axis=1)

                self.data = np.array([tup for i, tup in enumerate(xy) if i != index]).T
                self.undo_counter += 1

                self.removed_index = np.append(self.removed_index, index).astype(np.int64)
                self.felix_corrected = True
                if self.opo:
                    self.cfelix = f"{self.fname}.cofelix"
                print(f"\nRemoved Data: {self.removed_datas}\t{self.removed_datas.shape}\n")
                print(f"\nRemoved Data Index: {self.removed_index}\n")

        elif event.key == "z":
            "To UNDO the deleted point"
            print(
                f"data dim: {self.data.ndim}\t shape: {self.data.shape}\nundo dim: {self.removed_datas.ndim}\tshape: {self.removed_datas.shape}"
            )

            if self.undo_counter == 0:
                self.felix_corrected = False
                return self.widget.showdialog("INFO", "You have reached the end of UNDO")
            else:
                print("\n########## UNDO ##########\n")
                print("Before UNDO")
                print(f"\nRemoved Data: {self.removed_datas}\t{self.removed_datas.shape}\n")
                print(f"\nRemoved Data Index: {self.removed_index}\n")

                self.data = np.insert(self.data, self.removed_index[-1], self.removed_datas[:, -1], axis=1)

                self.redo_datas = np.append(self.redo_datas, self.removed_datas[:, -1].reshape(3, 1), axis=1)
                self.removed_datas = np.delete(self.removed_datas, -1, axis=1)

                self.redo_index = np.append(self.redo_index, self.removed_index[-1]).astype(np.int64)
                self.removed_index = np.delete(self.removed_index, -1)

                self.undo_counter -= 1
                self.redo_counter += 1

                print("After UNDO")
                
                print(f"\nRemoved Data: {self.removed_datas}\t{self.removed_datas.shape}\n")
                print(f"\nRemoved Data Index: {self.removed_index}\n")
                
                print("\n########## END UNDO ##########\n")

        elif event.key == "r":
            "To REDO"
            if self.redo_counter == 0:
                return self.widget.showdialog("INFO", "You have reached the end of REDO")

            print("\n########## REDO ##########\n")
            print("Before REDO")
            print(f"\nRemoved Data: {self.removed_datas}\t{self.removed_datas.shape}\n")
            print(f"\nRemoved Data Index: {self.removed_index}\n")

            self.data = np.delete(self.data, self.redo_index[-1], axis=1)

            self.removed_datas = np.append(self.removed_datas, self.redo_datas[:, -1].reshape(3, 1), axis=1)
            self.redo_datas = np.delete(self.redo_datas, -1, axis=1)

            self.removed_index = np.append(self.removed_index, self.redo_index[-1]).astype(np.int64)
            self.redo_index = np.delete(self.redo_index, -1)

            self.undo_counter += 1
            self.redo_counter -= 1
            self.felix_corrected = True

            print("Before REDO")
            print(f"\nRemoved Data: {self.removed_datas}\t{self.removed_datas.shape}\n")
            print(f"\nRemoved Data Index: {self.removed_index}\n")
            print("\n########## END REDO ##########\n")

        elif event.key == "c":
            "To save cfelix file"
            if not self.felix_corrected:
                self.widget.showdialog("No change", "You have not made any corrected to .felix file.", "warning")
                return

            else:
                self.save_cfelix()

        elif event.key == "b":
            "To save baseline file"
            self.SaveBase()

        if event.key in ("w", "a", "d"):
            return self.redraw_f_line()

        if event.key in ("x", "z", "r"):
            return self.redraw_baseline()

    def button_release_callback(self, event):
        "whenever a mouse button is released"
        if event.button != 1:
            return
        self._ind = None

    def motion_notify_callback(self, event):
        "on mouse movement"
        if self._ind is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        x, y = event.xdata, event.ydata

        xy = np.asarray(self.line.get_data())
        xy[0][self._ind], xy[1][self._ind] = x, y
        self.line.set_data((xy[0], xy[1]))
        self.baseline_corrected = True
        self.redraw_f_line()

    def get_ind_under_point(self, event):
        "get the index of the vertex under point if within epsilon tolerance"

        xy = np.asarray(self.line.get_data()).T
        xyt = self.line.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt - event.x) ** 2 + (yt - event.y) ** 2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]

        if d[ind] >= self.epsilon:
            ind = None

        return ind

    def get_index_under_basepoint(self, new_data, x, y):
        xy = np.asarray(new_data).T
        xyt = self.line.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt - x) ** 2 + (yt - y) ** 2)

        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        index = indseq[0]
        if d[index] >= self.epsilon:
            index = None
        return index

    def redraw_baseline(self):
        self.baseline_data.set_data(self.data[0], self.data[1])
        self.blit.update()

    def save_cfelix(self):

        print(f"Saving corrected felix file as {self.cfelix}")
        try:
            cfelixfile = self.location / f"DATA/{self.cfelix}"

            with open(cfelixfile, "w") as f:

                f.write(f"#Noise/Signal corrected for {self.felixfile} data file!\n")
                f.write(f"#Wavelength(cm-1)\t#Counts\tSA\n")
                if not self.opo:
                    for i in range(len(self.data[0])):
                        f.write(f"{self.data[0][i]}\t{self.data[1][i]}\t{self.data[2][i]}\n")

                else:
                    for i in range(len(self.data[0])):
                        f.write(f"{self.data[0][i]}\t{self.data[1][i]}\n")
                f.write("\n")

                if not self.opo:
                    for i in range(len(self.info)):
                        f.write(self.info[i])

            if isfile(cfelixfile):
                print(f"Corrected felix file: {self.cfelix}")
                self.felix_corrected = False

                return self.widget.showdialog("INFO", f"{self.cfelix} file is saved in /DATA directory")

        except Exception as error:
            self.widget.showdialog(
                "Error", f"Following error has occured while saving {self.cfelix} file\n{error}", "critical"
            )
            return

    def SaveBase(self):

        self.baseline = self.line.get_data()
        b = np.asarray(self.baseline)
        basefile = self.location / f"DATA/{self.basefile}"

        print(f"Saving basefile in {basefile}")

        try:
            with open(basefile, "w") as f:
                f.write(f"#Baseline generated for {self.felixfile} data file!\n")
                f.write("#BTYPE=cubic\n")
                for i in range(len(b[0])):
                    f.write("{:8.3f}\t{:8.2f}\n".format(b[0][i], b[1][i]))
                print(f"Basefile written for {self.felixfile} as {self.basefile}")

            if isfile(basefile):
                print(f"{self.basefile} is SAVED")
                self.widget.fig.savefig(f"{self.location}/OUT/{self.fname}.png")
                self.baseline_corrected = False
                return self.widget.showdialog("INFO", f"{self.basefile} file is saved in /DATA directory")

        except Exception as error:
            self.widget.showdialog(
                "Error", f"Following error has occured while saving {self.basefile} file\n{error}", "critical"
            )
            return

    def get_data(self):
        return np.asarray([self.data[0], self.data[1]]), np.asarray([self.line.get_data()])


def on_closing(event, dialog: felionQtWindow.showYesorNo, cls: Create_Baseline):
    
    def ask(check, change, txt=""):
    
        if not check:
            print(f"[{txt}] No changes have made")
            return
    
        ok = dialog(
            f"Save corrected as {cls.fname}{txt} file?",
            f"You haven't saved the corrected file\nPress 'Yes' to save the {txt} file and quit OR 'No' to just quit.",
        )
        
        if not ok:
            return print(f"[{txt}] Changes haven't saved")
        change()

    ask(cls.felix_corrected, cls.save_cfelix, ".cfelix")
    ask(cls.baseline_corrected, cls.SaveBase, ".base")
    event.accept()


def main(args):
    filename = pt(args["filename"])
    felixfile = filename.name
    
    opomode = felixfile.endswith("ofelix")
    location = filename.parent
    qapp = QApplication([])
    widget = felionQtWindow(
        title=f"{'OPO-mode' if opomode else 'FELIX-mode'}: {felixfile}",
        figXlabel="Wavenumber (cm$^{-1}$)", figYlabel="Counts",
        location=location / "../OUT", savefilename=felixfile,
    )

    baselineClass = Create_Baseline(filename)
    baselineClass.InteractivePlots(widget)
    widget.legend = widget.ax.legend()
    widget.legendToggleCheckWidget.setChecked(True)
    
    widget.closeEvent = lambda event: on_closing(event, widget.showYesorNo, baselineClass)
    
    widget.optimize_figure()
    widget.fig.tight_layout()
    
    qapp.exec()
    