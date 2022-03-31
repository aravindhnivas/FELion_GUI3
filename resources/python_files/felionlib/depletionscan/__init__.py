
# Built-In modules
import traceback
from pathlib import Path as pt
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
import numpy as np
from scipy.optimize import curve_fit
from uncertainties import ufloat as uf, unumpy as unp
from felionlib.utils.felionQt import felionQtWindow, QApplication, QtWidgets
from felionlib.timescan import timescanplot
from felionlib.utils.felionQt.utils.blit import BlitManager


np.seterr(all="ignore")


class depletionplot:
    
    def __init__(
        self, location: str, resOnFile: pt, resOffFile: pt,
        power: np.ndarray, nshots: int = 10, massIndex: int =0, timestartIndex: int =1,
        saveOutputDepletion: bool =True
    ):
        try:
            
            self.location = pt(location).resolve()
            self.scanfiles = list(self.location.glob("*.scan"))

            self.resOnFile = resOnFile
            self.resOffFile = resOffFile
            
            self.power: dict[str, float] = {"resOn": power[0]/1000, "resOff": power[1]/1000} # mJ to J
            self.powerStr = f"{power[0]}, {power[1]}"
            self.nshots = nshots
            self.massIndex = massIndex
            self.timestartIndex = timestartIndex

            qapp = QApplication([])
            self.widget = felionQtWindow(
                title=f"Depletion Plot: ON ({self.resOnFile.name}), OFF ({self.resOffFile.name})", location=self.location, createControlLayout=False, figDPI=150
            )
            
            self.create_figure()
            self.depletion_exp = None            
            
            self.startPlotting()
            if saveOutputDepletion and self.depletion_exp is not None: 
                self.saveFile(show=False)
            self.widget.attachControlLayout()
            # self.widget.toggle_controller_layout()
            self.widget.optimize_figure()
            self.widget.updatecanvas()
            qapp.exec()

        except Exception:
            self.widget.showdialog("Error", traceback.format_exc(5), "critical")

    def create_figure(self):

        # self.widget.fig.suptitle("Depletion Scan")
        axes: tuple[Axes, Axes] = self.widget.fig.subplots(1, 2)
        self.widget.createControlLayout(axes)
        self.ax0, self.ax1 = axes

    def depletion_widgets(self, Koff, Kon, N, Na0, Nn0):

        slider_layout_vbox =  QtWidgets.QVBoxLayout()

        slider_layout_Koff, self.Koff_slider = self.widget.makeSlider("Koff", Koff, callback=self.update)
        slider_layout_N, self.N_slider = self.widget.makeSlider("N", int(N), callback=self.update)
        slider_layout_Kon, self.Kon_slider = self.widget.makeSlider("Kon", Kon, callback=self.update)
        slider_layout_Na, self.Na_slider = self.widget.makeSlider("Na", int(Na0), callback=self.update)
        slider_layout_Nn, self.Nn_slider = self.widget.makeSlider("Nn", int(Nn0), callback=self.update)
        

        self.Koff_slider.mouseReleaseEvent = lambda e: self.widget.draw()
        self.Kon_slider.mouseReleaseEvent = lambda e: self.widget.draw()

        slider_layout_vbox.addLayout(slider_layout_Koff)
        slider_layout_vbox.addLayout(slider_layout_N)
        slider_layout_vbox.addLayout(slider_layout_Kon)
        slider_layout_vbox.addLayout(slider_layout_Na)
        slider_layout_vbox.addLayout(slider_layout_Nn)

        refit_button = QtWidgets.QPushButton("Re-fit")
        refit_button.clicked.connect(self.set_slider_values)

        write_file_layout = QtWidgets.QHBoxLayout()

        self.write_filename_input = QtWidgets.QLineEdit("depletion_output")
        self.write_filename_input.setToolTip("save data filename")

        write_file_button = QtWidgets.QPushButton("Write")
        write_file_button.clicked.connect(self.saveFile)
        
        write_file_layout.addWidget(self.write_filename_input)
        write_file_layout.addWidget(write_file_button)

        self.widget.controlLayout.addLayout(slider_layout_vbox)
        self.widget.controlLayout.addWidget(refit_button)
        self.widget.controlLayout.addLayout(write_file_layout)

    def saveFile(self, event=None, show=True):

        depletion_dir = self.location / self.write_filename_input.text()

        if not depletion_dir.exists():
            depletion_dir.mkdir()
        
        timescanfile_reduced = depletion_dir / f"{self.resOnFile.stem}__{self.resOffFile.stem}.rscan"
        timescanfile_fitted = depletion_dir / f"{self.resOnFile.stem}__{self.resOffFile.stem}.fscan"


        with open(timescanfile_reduced, "w+") as f:
            f.write(
                "# time(s)\tpowerOn(J)\tcountsOn\terrOn\t\
                powerOff(J)\tcountsOff\terroff\tDep_exp\tDep_exp_err\t\n"
            )

            for time, powerOn, powerOff, countsOn, countsOff, \
                errOn, errOff, dep_exp, dep_exp_err \
                    in zip(
                        self.time["resOn"], self.power["resOn"],
                        self.power["resOff"], self.counts["resOn"], 
                        self.counts["resOff"], self.error["resOn"], 
                        self.error["resOff"], self.depletion_exp, 
                        self.depletion_exp_err
                    ):

                f.write(
                    f"{time:.4f}\t{powerOn:.4f}\t{countsOn:.4f}\t\
                        {errOn:.4f}\t{powerOff:.4f}\t{countsOff:.4f}\t\
                            {errOff:.4f}\t{dep_exp:.4f}\t{dep_exp_err:.4f}\n"
                )

            print(f"File saved: {f.name} in {self.location}")

        with open(timescanfile_fitted, "w+") as f:
            self.uA = self.uA*100
            f.write("####################################### \n")
            f.write(f"# A={self.uA.nominal_value:.2f}({self.uA.std_dev:.2f}) %\n")
            f.write(f"# {self.lg0}\n# {self.lg1}\n")
            f.write(f"# FELIX_Shots={self.nshots}\n")
            f.write(f"# Power (mJ)[On, Off]=[{self.powerStr}]\n")
            f.write(f"# ResOn File:{self.resOnFile.name}, ResOff File:{self.resOffFile.name}\n")
            f.write(f"{self.fileInfo}\n")

            f.write("####################################### \n")

            f.write("# fitX(J)\tfitOn\tfitOff\t(1-fitOff/fitOn)\tDepl_fit\n")
            
            for fitX, fitOn, fitOff, dep_fit, rel_abun in zip(self.fitX, self.fitOn, self.fitOff, self.depletion_fitted, self.relative_abundance):
                f.write(f"{fitX:.4f}\t{fitOn:.4f}\t{fitOff:.4f}\t{dep_fit:.4f}\t{rel_abun:.4f}\n")
            if show: self.widget.showdialog("File saved", f"File saved: {f.name} in {self.location}")
            print(f"File saved: {f.name} in {self.location}")
            
    def set_slider_values(self, on=None, off=None):
        Koff, N = off or self.resOff_fit()
        Na0, Nn0, Kon = on or self.resOn_fit(Koff, N)

        self.Koff_slider.setValue(Koff)
        self.N_slider.setValue(N)
        self.Kon_slider.setValue(Kon)
        self.Na_slider.setValue(Na0)
        self.Nn_slider.setValue(Nn0)
    def startPlotting(self, make_slider_widget=True):

        self.get_timescan_data()
        self.fileInfo = f"\nMass: {self.timescan_data.mass[0]}u, Res: {self.timescan_data.t_res}V, B0: {self.timescan_data.t_b0}ms"
        title = f"ON:{self.resOnFile.name}. OFF:{self.resOffFile.name}"
        title += self.fileInfo
        # self.widget.fig.suptitle(title, fontsize=7)
        self.ax0.set(xlabel="Total energy (J)", ylabel="Counts")
        
        self.ax1.set(
            xlabel="Total energy (J)", 
            # title="$D(t)=A*(1-e^{-K_{ON}*(ntE)})$",
            ylabel="A: Relative abundace of active isomer",
        )

        Koff, N = self.resOff_fit()
        Na0, Nn0, Kon = self.resOn_fit(Koff, N)

        if make_slider_widget: 
            self.depletion_widgets(Koff, Kon, N, Na0, Nn0)
        else:
            self.set_slider_values(on=(Na0, Nn0, Kon), off=(Koff, N))

        self.runFit(Koff, Kon, N, Na0, Nn0)

    def runFit(self, Koff, Kon, N, Na0, Nn0, plot=True):
        
        uKoff = uf(Koff, self.Koff_err)
        
        uN = uf(N, self.N_err)
        uNa0 = uf(Na0, self.Na0_err)
        uNn0 = uf(Nn0, self.Nn0_err)
        uKon = uf(Kon, self.Kon_err)
        
        self.lg0 = "K$_{ON}$: " + f"{uKon:.2uP}"
        # self.lg0 += f"\nNa: {Na0:.0f}({self.Na0_err:.0f})"
        # self.lg0 += f"\nNn: {Nn0:.0f}({self.Nn0_err:.0f})"

        self.lg1 = "K$_{OFF}$: " + f"{uKoff:.1uP}"
        # self.lg1 = f"\nN: {N:.0f}({self.N_err:.0f})"

        self.get_depletion_fit(Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon, plot)
        self.get_relative_abundance_fit(plot)

        self.ax0.legend([self.lg0, self.lg1])
        self.ax1.legend([f"A: {self.uA:.1uP}", "Experiment"], title="$D(t)=A*(1-e^{-K_{ON}*(E)})$")
        
        if plot:
            self.ax0.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
            animated_artist = (
                self.ax0_plot["resOn"], self.ax0_plot["resOff"],
                self.relativeFit_plot,
            )
            self.blit = BlitManager(self.widget.canvas, animated_artist)

    def update(self, event=None):

        Koff = self.Koff_slider.value()
        Kon = self.Kon_slider.value()
        N = self.N_slider.value()
        Na0 = self.Na_slider.value()
        Nn0 = self.Nn_slider.value()

        self.runFit(Koff, Kon, N, Na0, Nn0, plot=False)
        self.ax0_plot["resOn"].set_ydata(self.fitOn)
        self.ax0_plot["resOff"].set_ydata(self.fitOff)
        # self.fit_plot.set_ydata(self.depletion_fitted)
        self.relativeFit_plot.set_ydata(self.relative_abundance)
        self.blit.update()
        # self.saveFile(show=False)
    
    def get_timescan_data(self):

        self.time = {"resOn":[], "resOff": []}
        self.counts = {"resOn":[], "resOff": []}

        self.error = {"resOn":[], "resOff": []}

        self.ax0_plot: dict[str, Line2D] = {}

        for index, scanfile, i in zip(["resOn", "resOff"], [self.resOnFile, self.resOffFile], [0, 1]):
            
            self.timescan_data = timescanplot(scanfile)
            self.timescan_data.compute_data()

            time = self.timescan_data.time/1000 # ms to s
            ind = np.where(self.timescan_data.error==0)
            self.timescan_data.error[ind] = 1e-5
            self.time[index] = np.array(time[self.timestartIndex:])
            self.counts[index] = np.array(self.timescan_data.mean[self.massIndex][self.timestartIndex:])
            self.error[index] = np.array(self.timescan_data.error[self.massIndex][self.timestartIndex:])
            self.power[index] = np.array((self.power[index] * self.nshots * self.time[index]))
            self.ax0.errorbar(self.power[index], self.counts[index], yerr=self.error[index], fmt=f".k")

        self.size = len(self.time["resOn"])*3
        
    def N_OFF(self, x, K_OFF, N): return (N)*np.exp(-K_OFF*x)

    def resOff_fit(self, auto_plot=True):
        
        K_OFF_init = 0
        N_init = self.counts["resOff"].max()

        try:
            pop_off, popc_off = curve_fit( self.N_OFF, self.power["resOff"], self.counts["resOff"],
                sigma=self.error["resOff"], absolute_sigma=True,
                p0=[K_OFF_init, N_init], bounds=[(-np.inf, 0), (np.inf, N_init*2)]
            )
        except Exception as error:

            print("Error occured in N_OFF fit with sigma error", error)

            pop_off, popc_off = curve_fit( self.N_OFF, self.power["resOff"], self.counts["resOff"], p0=[K_OFF_init, N_init], bounds=[(-np.inf, 0), (np.inf, N_init*2)])


        perr_off = np.sqrt(np.diag(popc_off))
        Koff, N= pop_off

        self.Koff_err, self.N_err = perr_off
        if auto_plot: return Koff, N
    
    def N_ON(self, x, Na0, Nn0, K_ON):
            K_OFF = self.Koff
            return Na0*np.exp(-K_ON*x)*np.exp(-K_OFF*x) + Nn0*np.exp(-K_OFF*x)

    def resOn_fit(self, Koff, N, auto_plot=True):

        self.Koff = Koff
        Na0_init, Nn0_init, K_ON_init = N, N/2, 0
        
        try:
            pop_on, popc_on = curve_fit( self.N_ON, self.power["resOn"], self.counts["resOn"],
                sigma=self.error["resOn"], absolute_sigma=True,
                p0=[Na0_init, Nn0_init, K_ON_init], bounds=[(0, 0, -np.inf), (N , N*2, np.inf)]
            )
        except Exception as error:
            print("Error occured in N_ON fit with sigma error", error)
            pop_on, popc_on = curve_fit( self.N_ON, self.power["resOn"], self.counts["resOn"],
                p0=[Na0_init, Nn0_init, K_ON_init], bounds=[(0, 0, -np.inf), (N , N*2, np.inf)]
            )

        perr_on = np.sqrt(np.diag(popc_on))
        Na0, Nn0, Kon = pop_on
        self.Na0_err, self.Nn0_err, self.Kon_err = perr_on
        
        if auto_plot: return Na0, Nn0, Kon

    def uN_OFF(self, x, uN, uK_OFF): 
        return uN*unp.exp(-uK_OFF*x)

    def uN_ON(self, x, uNa0, uNn0, uK_OFF, uK_ON): 
        return uNa0 * unp.exp(-uK_ON*x)*unp.exp(-uK_OFF*x) + uNn0*unp.exp(-uK_OFF*x)
        
    def get_depletion_fit(self, Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon, plot=True):
        
        self.Kon = Kon
        self.Koff = Koff

        maxPower = np.append(self.power["resOn"], self.power["resOff"]).max()*2
        self.fitX = np.linspace(0, maxPower, self.size)
        # print(len(self.fitX))
        ufitX = unp.uarray(self.fitX, np.zeros(len(self.fitX)))

        self.fitOn = self.N_ON(self.fitX, Na0, Nn0, self.Kon)
        self.fitOff = self.N_OFF(self.fitX, Koff, N)

        self.fitOn_with_err = self.uN_ON(ufitX, uNa0, uNn0, uKoff, uKon)
        self.fitOff_with_err = self.uN_OFF(ufitX, uKoff, uN)

        # print(len(self.fitX), len(self.fitOn))
        
        self.fitted_counts_error = {"resOn": unp.std_devs(self.fitOn_with_err), "resOff": unp.std_devs(self.fitOff_with_err)}
        # print(f"Exp counts error: {self.error}\nFitted counts error: {self.fitted_counts_error}\n")

        self.fitted_counts = {"resOn":np.array(self.fitOn), "resOff": np.array(self.fitOff)}
        # print(f"Counts: {self.counts}\nFitted: {self.fitted_counts}\n")

        if plot:
            # for index, fitY, i in zip(["resOn", "resOff"], [self.fitOn, self.fitOff], [0, 1]):
            (self.ax0_plot["resOn"],) = self.ax0.plot(self.fitX, self.fitOn, f"-k", animated=True, label=self.lg0)
            (self.ax0_plot["resOff"],) = self.ax0.plot(self.fitX, self.fitOff, f"--k", animated=True, label=self.lg1)

    def Depletion(self, x, A):

        K_ON = self.Kon
        return A*(1-np.exp(-K_ON*x))

    def get_relative_abundance_fit(self, plot=True):

        self.depletion_fitted = 1 - (self.fitted_counts["resOn"] / self.fitted_counts["resOff"])
        
        fitted_on_data = unp.uarray(self.fitted_counts["resOn"], self.fitted_counts_error["resOn"])
        fitted_off_data = unp.uarray(self.fitted_counts["resOff"], self.fitted_counts_error["resOff"])
        depletion_fitted_with_err = 1 - (fitted_on_data / fitted_off_data)
        self.depletion_fitted_err = unp.std_devs(depletion_fitted_with_err)

        self.depletion_exp = 1 - (self.counts["resOn"]/self.counts["resOff"])

        on_data = unp.uarray(self.counts["resOn"], self.error["resOn"])
        off_data = unp.uarray(self.counts["resOff"], self.error["resOff"])
        depletion_exp_with_err = 1 - (on_data/off_data)

        self.depletion_exp_err = unp.std_devs(depletion_exp_with_err)
        
        A_init = 0.5

        pop_depletion, popc_depletion = curve_fit(
            self.Depletion, self.fitX, self.depletion_fitted,
            sigma=self.depletion_fitted_err,
            absolute_sigma=True,
            p0=[A_init],
            bounds=[(0), (1)]
        )

        perr_depletion = np.sqrt(np.diag(popc_depletion))

        A = pop_depletion
        A_err = perr_depletion
        self.uA = uf(A, A_err)
        # print(f"A: {self.uA:.3uP}")

        self.relative_abundance = self.Depletion(self.fitX, A)

        if plot:
            # (["Fitted", f"A: {self.uA:.1uP}", "Experiment"])
            self.ax1.errorbar(
                self.power["resOn"], self.depletion_exp, 
                fmt="k.",
                yerr=self.depletion_exp_err, label="Experiment"
            )

            # self.fit_plot, = self.ax1.plot(self.fitX, self.depletion_fitted, animated=True, label="Fitted")
            self.relativeFit_plot, = self.ax1.plot(
                self.fitX, self.relative_abundance, "-k", animated=True, label=f"A: {self.uA:.1uP}"
            )


def main(arguments):

    location: str = arguments["currentLocation"]
    resOnFile: pt = pt(location)/arguments["resON_Files"]
    resOffFile: pt = pt(location)/arguments["resOFF_Files"]
    power: np.array = np.asarray(arguments["power"].split(","), dtype=float)
    nshots = int(arguments["nshots"])
    massIndex = int(arguments["massIndex"])
    timestartIndex = int(arguments["timestartIndex"])
    saveOutputDepletion = arguments["saveOutputDepletion"]
    
    depletionplot(
        location, resOnFile, resOffFile, 
        power, nshots, massIndex, timestartIndex, saveOutputDepletion
    )
