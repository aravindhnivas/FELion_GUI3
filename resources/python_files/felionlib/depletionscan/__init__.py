# Built-In modules
from dataclasses import dataclass, field
import traceback
from pathlib import Path as pt
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
import numpy as np
from scipy.optimize import curve_fit
from uncertainties import ufloat as uf, unumpy as unp
from felionlib.utils.felionQt import felionQtWindow, QtWidgets, Qt
from felionlib.timescan import timescanplot
from felionlib.utils.felionQt.utils.blit import BlitManager


np.seterr(all="ignore")


@dataclass
class depletionplot:
    # def __init__(
    # self,
    location: str
    resOnFile: pt
    resOffFile: pt
    power: np.ndarray
    nshots: int = 10
    massIndex: int = 0
    timestartIndex: int = 1
    saveOutputDepletion: bool = True
    depletionplot_figure_kwargs: dict = field(default=dict)
    depletion_exp = None
    widget = felionQtWindow
    # ):

    def __post_init__(self):

        try:

            self.location = pt(self.location).resolve()
            self.scanfiles = list(self.location.glob("*.scan"))

            # self.resOnFile = resOnFile
            # self.resOffFile = resOffFile

            print(self.depletionplot_figure_kwargs, flush=True)
            self.power = {"resOn": self.power[0] / 1000, "resOff": self.power[1] / 1000}  # mJ to J
            self.powerStr = f"{self.power['resOn']}, {self.power['resOn']}"

            # self.nshots = nshots
            # self.massIndex = massIndex
            # self.timestartIndex = timestartIndex

            self.widget = felionQtWindow(
                title=f"Depletion Plot: ON ({self.resOnFile.name}), OFF ({self.resOffFile.name})",
                location=self.location,
                createControlLayout=False,
                figDPI=150,
            )

            self.create_figure()
            # self.depletion_exp = None

            self.startPlotting()
            if self.saveOutputDepletion and self.depletion_exp is not None:
                self.saveFile(show=False)
            # self.widget.attachControlLayout()

            self.widget.optimize_figure()
            self.widget.updatecanvas()
            self.widget.qapp.exec()

        except Exception:
            self.widget.showdialog("Error", traceback.format_exc(5), "critical")

    def create_figure(self):

        rows, cols = self.depletionplot_figure_kwargs["rows_cols"].split(",")
        axes: tuple[Axes, Axes] = self.widget.fig.subplots(int(rows), int(cols), sharex=True)
        self.widget.createControlLayout(axes)
        self.ax0, self.ax1 = axes

    def depletion_widgets(self, Koff, Kon, N, Na0, Nn0):

        slider_layout_vbox = QtWidgets.QVBoxLayout()

        slider_layout_Koff, self.Koff_slider = self.widget.makeSlider("Koff", float(Koff), callback=self.update)
        slider_layout_N, self.N_slider = self.widget.makeSlider("N", int(N), callback=self.update)
        slider_layout_Kon, self.Kon_slider = self.widget.makeSlider("Kon", float(Kon), callback=self.update)
        slider_layout_Na, self.Na_slider = self.widget.makeSlider("Na", int(Na0), callback=self.update)
        slider_layout_Nn, self.Nn_slider = self.widget.makeSlider("Nn", int(Nn0), callback=self.update)

        # self.Koff_slider.mouseReleaseEvent = lambda e: self.widget.draw()
        # self.Kon_slider.mouseReleaseEvent = lambda e: self.widget.draw()

        self.params = {
            "Koff": slider_layout_Koff,
            "N": slider_layout_N,
            "Kon": slider_layout_Kon,
            "Na": slider_layout_Na,
            "Nn": slider_layout_Nn,
        }
        # self.slider_koff_err_label = QtWidgets.QLabel()

        self.error_labels_widgets: list[QtWidgets.QLabel] = []

        for param in self.params.values():
            self.error_labels_widgets.append(QtWidgets.QLabel())
            param.addWidget(self.error_labels_widgets[-1])

        slider_layout_vbox.addLayout(slider_layout_Koff)
        slider_layout_vbox.addLayout(slider_layout_N)
        slider_layout_vbox.addLayout(slider_layout_Kon)
        slider_layout_vbox.addLayout(slider_layout_Na)
        slider_layout_vbox.addLayout(slider_layout_Nn)

        self.depletion_output_label = QtWidgets.QLabel("")
        slider_layout_vbox.addWidget(self.depletion_output_label)

        slider_layout_vbox.setAlignment(self.depletion_output_label, Qt.AlignmentFlag.AlignCenter)

        update_buttons_layout = QtWidgets.QHBoxLayout()

        update_legend_button = QtWidgets.QPushButton("Update label")

        def update_legend_ax0():
            self.ax1.legend([self.depletion_output_label.text(), "Experiment"])
            self.widget.draw()

        update_legend_button.clicked.connect(update_legend_ax0)

        refit_button = QtWidgets.QPushButton("Re-fit")
        refit_button.clicked.connect(self.set_slider_values)

        update_buttons_layout.addWidget(update_legend_button)
        update_buttons_layout.addWidget(refit_button)

        write_file_layout = QtWidgets.QHBoxLayout()

        # self.write_filename_input = QtWidgets.QLineEdit("depletion_output")
        # self.write_filename_input.setToolTip("save directory")

        write_file_button = QtWidgets.QPushButton("Write to file")
        write_file_button.clicked.connect(self.saveFile)

        # write_file_layout.addWidget(self.write_filename_input)
        write_file_layout.addWidget(write_file_button)

        additional_widgets_group = QtWidgets.QGroupBox()
        additional_widgets_layout = QtWidgets.QVBoxLayout()
        additional_widgets_layout.addLayout(slider_layout_vbox)
        additional_widgets_layout.addLayout(update_buttons_layout)
        additional_widgets_layout.addLayout(write_file_layout)
        additional_widgets_layout.addStretch()
        additional_widgets_group.setLayout(additional_widgets_layout)

        controllerDock = QtWidgets.QDockWidget("Fitting controller", self.widget)

        controllerDock.setWidget(additional_widgets_group)
        controllerDock.setMaximumHeight(500)
        controllerDock.setMinimumWidth(300)
        controllerDock.setMaximumWidth(500)
        controllerDock.setFloating(True)
        # make controllerDock not closable
        controllerDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.widget.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, controllerDock)

    def saveFile(self, event=None, show=True):

        depletion_dir = self.location / "depletion_output"

        if not depletion_dir.exists():
            depletion_dir.mkdir()

        timescanfile_reduced = depletion_dir / f"{self.resOnFile.stem}__{self.resOffFile.stem}.rscan"
        timescanfile_fitted = depletion_dir / f"{self.resOnFile.stem}__{self.resOffFile.stem}.fscan"

        with open(timescanfile_reduced, "w+") as f:
            f.write(
                "# time(s)\tpowerOn(J)\tcountsOn\terrOn\t\
                powerOff(J)\tcountsOff\terroff\tDep_exp\tDep_exp_err\t\n"
            )

            for time, powerOn, powerOff, countsOn, countsOff, errOn, errOff, dep_exp, dep_exp_err in zip(
                self.time["resOn"],
                self.power["resOn"],
                self.power["resOff"],
                self.counts["resOn"],
                self.counts["resOff"],
                self.error["resOn"],
                self.error["resOff"],
                self.depletion_exp,
                self.depletion_exp_err,
            ):

                f.write(
                    f"{time:.4f}\t{powerOn:.4f}\t{countsOn:.4f}\t\
                        {errOn:.4f}\t{powerOff:.4f}\t{countsOff:.4f}\t\
                            {errOff:.4f}\t{dep_exp:.4f}\t{dep_exp_err:.4f}\n"
                )

            print(f"File saved: {f.name} in {self.location}")

        with open(timescanfile_fitted, "w+") as f:
            self.uA = self.uA * 100
            f.write("####################################### \n")
            f.write(f"# A={self.uA.nominal_value:.2f}({self.uA.std_dev:.2f}) %\n")

            f.write(f"# {self.write_lg0}\n# {self.write_lg1}\n")
            f.write(f"# FELIX_Shots={self.nshots}\n")
            f.write(f"# Power (mJ)[On, Off]=[{self.powerStr}]\n")
            f.write(f"# ResOn File:{self.resOnFile.name}, ResOff File:{self.resOffFile.name}\n")
            f.write(f"{self.fileInfo}\n")

            f.write("####################################### \n")

            f.write("# fitX(J)\tfitOn\tfitOff\t(1-fitOff/fitOn)\tDepl_fit\n")

            for fitX, fitOn, fitOff, dep_fit, rel_abun in zip(
                self.fitX, self.fitOn, self.fitOff, self.depletion_fitted, self.relative_abundance
            ):
                f.write(f"{fitX:.4f}\t{fitOn:.4f}\t{fitOff:.4f}\t{dep_fit:.4f}\t{rel_abun:.4f}\n")

            if show:
                self.widget.showdialog("File saved", f"{timescanfile_fitted.name} file saved\nin {self.location}")
            print(f"File saved: {f.name} in {self.location}")

    def set_slider_err_values(self):
        self.error_labels_widgets[0].setText(f"({self.Koff_err:.2f})")
        self.error_labels_widgets[1].setText(f"({self.N_err:.2f})")
        self.error_labels_widgets[2].setText(f"({self.Kon_err:.2f})")
        self.error_labels_widgets[3].setText(f"({self.Na0_err:.2f})")
        self.error_labels_widgets[4].setText(f"({self.Nn0_err:.2f})")

    def set_slider_values(self, on=None, off=None):
        Koff, N = off or self.resOff_fit()
        Na0, Nn0, Kon = on or self.resOn_fit(Koff, N)
        self.Koff_slider.setValue(float(Koff))
        self.N_slider.setValue(int(N))
        self.Kon_slider.setValue(float(Kon))
        self.Na_slider.setValue(int(Na0))
        self.Nn_slider.setValue(int(Nn0))

        self.set_slider_err_values()

    def startPlotting(self, make_slider_widget=True):

        self.get_timescan_data()
        self.fileInfo = (
            f"\nMass: {self.timescan_data.mass[0]}u, Res: {self.timescan_data.t_res}V, B0: {self.timescan_data.t_b0}ms"
        )

        title = f"ON:{self.resOnFile.name}. OFF:{self.resOffFile.name}"
        title += self.fileInfo
        # self.widget.fig.suptitle(title, fontsize=7)
        self.ax0.set(ylabel="Counts")

        self.ax1.set(
            # title="$D(t)=A \cdot (1-e^{-K_{ON} \cdot E})$",
            ylabel="A: Active isomer",
        )
        self.widget.fig.supxlabel("Total energy E (J)", y=0.02)
        Koff, N = self.resOff_fit()
        Na0, Nn0, Kon = self.resOn_fit(Koff, N)

        if make_slider_widget:
            self.depletion_widgets(Koff, Kon, N, Na0, Nn0)
        else:
            self.set_slider_values(on=(Na0, Nn0, Kon), off=(Koff, N))
        self.set_slider_err_values()

        self.runFit(Koff, Kon, N, Na0, Nn0)

    def runFit(self, Koff, Kon, N, Na0, Nn0, plot=True):

        uKoff = uf(Koff, self.Koff_err)
        uN = uf(N, self.N_err)

        uNa0 = uf(Na0, self.Na0_err)
        uNn0 = uf(Nn0, self.Nn0_err)
        uKon = uf(Kon, self.Kon_err)

        self.lg0 = "Radiation ON"

        self.write_lg0 = "K$_{ON}$: " + f"{uKon:.2uP}"
        self.write_lg0 += f"\nNn: {Nn0:.0f}({self.Nn0_err:.0f})"
        self.write_lg0 += f"\nNa: {Na0:.0f}({self.Na0_err:.0f})"

        self.lg1 = "Radiation OFF"

        self.write_lg1 = "K$_{OFF}$: " + f"{uKoff:.1uP}"
        self.write_lg1 = f"\nN: {N:.0f}({self.N_err:.0f})"

        self.get_depletion_fit(Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon, plot)
        self.get_relative_abundance_fit(plot)

        if plot:
            self.ax0.legend([self.lg0, self.lg1])
            self.ax1.legend([self.depletion_output_label.text(), "Experiment"])
            # self.ax0.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
            animated_artist = (
                self.ax0_plot["resOn"],
                self.ax0_plot["resOff"],
                self.relativeFit_plot,
            )
            self.blit = BlitManager(self.widget.canvas, animated_artist)

    def update(self, event=None):
        if self.N_slider.value() == 0:
            return
        Koff = self.Koff_slider.value()
        Kon = self.Kon_slider.value()
        N = self.N_slider.value()
        Na0 = self.Na_slider.value()
        Nn0 = self.Nn_slider.value()
        self.runFit(Koff, Kon, N, Na0, Nn0, plot=False)
        self.ax0_plot["resOn"].set_ydata(self.fitOn)
        self.ax0_plot["resOff"].set_ydata(self.fitOff)
        self.relativeFit_plot.set_ydata(self.relative_abundance)

        self.blit.update()

    def get_timescan_data(self):

        self.time = {"resOn": [], "resOff": []}
        self.counts = {"resOn": [], "resOff": []}
        self.error = {"resOn": [], "resOff": []}

        self.ax0_plot: dict[str, Line2D] = {}

        for index, scanfile, i in zip(["resOn", "resOff"], [self.resOnFile, self.resOffFile], [0, 1]):

            self.timescan_data = timescanplot(scanfile)
            self.timescan_data.compute_data()
            time = self.timescan_data.time / 1000  # ms to s

            ind = np.where(self.timescan_data.error == 0)
            self.timescan_data.error[ind] = 1e-5

            self.time[index] = np.array(time[self.timestartIndex :])
            self.counts[index] = np.array(self.timescan_data.mean[self.massIndex][self.timestartIndex :])
            self.error[index] = np.array(self.timescan_data.error[self.massIndex][self.timestartIndex :])
            self.power[index] = np.array((self.power[index] * self.nshots * self.time[index]))

            self.ax0.errorbar(self.power[index], self.counts[index], yerr=self.error[index], fmt=f".")

        self.size = len(self.time["resOn"]) * 3

    def N_OFF(self, x, K_OFF, N):
        return (N) * np.exp(-K_OFF * x)

    def resOff_fit(self, auto_plot=True):

        K_OFF_init = 0
        N_init = self.counts["resOff"].max()

        try:
            pop_off, popc_off = curve_fit(
                self.N_OFF,
                self.power["resOff"],
                self.counts["resOff"],
                sigma=self.error["resOff"],
                absolute_sigma=True,
                p0=[K_OFF_init, N_init],
                bounds=[(-np.inf, 0), (np.inf, N_init * 2)],
            )
        except Exception as error:
            print("Error occured in N_OFF fit with sigma error", error, flush=True)
            pop_off, popc_off = curve_fit(
                self.N_OFF,
                self.power["resOff"],
                self.counts["resOff"],
                p0=[K_OFF_init, N_init],
                bounds=[(-np.inf, 0), (np.inf, N_init * 2)],
            )

        perr_off = np.sqrt(np.diag(popc_off))
        Koff, N = pop_off
        self.Koff_err, self.N_err = perr_off

        if auto_plot:
            return Koff, N

    def N_ON(self, x, Na0, Nn0, K_ON):
        K_OFF = self.Koff
        return Na0 * np.exp(-K_ON * x) * np.exp(-K_OFF * x) + Nn0 * np.exp(-K_OFF * x)

    def resOn_fit(self, Koff, N, auto_plot=True):

        self.Koff = Koff
        Na0_init, Nn0_init, K_ON_init = N, N / 2, 0

        try:
            pop_on, popc_on = curve_fit(
                self.N_ON,
                self.power["resOn"],
                self.counts["resOn"],
                sigma=self.error["resOn"],
                absolute_sigma=True,
                p0=[Na0_init, Nn0_init, K_ON_init],
                bounds=[(0, 0, -np.inf), (N, N * 2, np.inf)],
            )
        except Exception as error:
            print("Error occured in N_ON fit with sigma error", error, flush=True)
            pop_on, popc_on = curve_fit(
                self.N_ON,
                self.power["resOn"],
                self.counts["resOn"],
                p0=[Na0_init, Nn0_init, K_ON_init],
                bounds=[(0, 0, -np.inf), (N, N * 2, np.inf)],
            )

        perr_on = np.sqrt(np.diag(popc_on))
        Na0, Nn0, Kon = pop_on
        self.Na0_err, self.Nn0_err, self.Kon_err = perr_on

        if auto_plot:
            return Na0, Nn0, Kon

    def uN_OFF(self, x, uN, uK_OFF):
        return uN * unp.exp(-uK_OFF * x)

    def uN_ON(self, x, uNa0, uNn0, uK_OFF, uK_ON):
        return uNa0 * unp.exp(-uK_ON * x) * unp.exp(-uK_OFF * x) + uNn0 * unp.exp(-uK_OFF * x)

    def get_depletion_fit(self, Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon, plot=True):

        self.Kon = Kon
        self.Koff = Koff

        maxPower = np.append(self.power["resOn"], self.power["resOff"]).max() * 2
        self.fitX = np.linspace(0, maxPower, self.size)
        # print(len(self.fitX))
        ufitX = unp.uarray(self.fitX, np.zeros(len(self.fitX)))

        self.fitOn = self.N_ON(self.fitX, Na0, Nn0, self.Kon)
        self.fitOff = self.N_OFF(self.fitX, Koff, N)

        self.fitOn_with_err = self.uN_ON(ufitX, uNa0, uNn0, uKoff, uKon)
        self.fitOff_with_err = self.uN_OFF(ufitX, uKoff, uN)

        # print(len(self.fitX), len(self.fitOn))

        self.fitted_counts_error = {
            "resOn": unp.std_devs(self.fitOn_with_err),
            "resOff": unp.std_devs(self.fitOff_with_err),
        }
        # print(f"Exp counts error: {self.error}\nFitted counts error: {self.fitted_counts_error}\n")

        self.fitted_counts = {"resOn": np.array(self.fitOn), "resOff": np.array(self.fitOff)}
        # print(f"Counts: {self.counts}\nFitted: {self.fitted_counts}\n")

        if plot:
            # for index, fitY, i in zip(["resOn", "resOff"], [self.fitOn, self.fitOff], [0, 1]):
            (self.ax0_plot["resOn"],) = self.ax0.plot(self.fitX, self.fitOn, f"C0", animated=True, label=self.lg0)
            (self.ax0_plot["resOff"],) = self.ax0.plot(self.fitX, self.fitOff, f"C1", animated=True, label=self.lg1)

    def Depletion(self, x, A):

        K_ON = self.Kon
        return A * (1 - np.exp(-K_ON * x))

    def get_relative_abundance_fit(self, plot=True):

        self.depletion_fitted = 1 - (self.fitted_counts["resOn"] / self.fitted_counts["resOff"])

        fitted_on_data = unp.uarray(self.fitted_counts["resOn"], self.fitted_counts_error["resOn"])
        fitted_off_data = unp.uarray(self.fitted_counts["resOff"], self.fitted_counts_error["resOff"])
        depletion_fitted_with_err = 1 - (fitted_on_data / fitted_off_data)
        self.depletion_fitted_err = unp.std_devs(depletion_fitted_with_err)

        self.depletion_exp = 1 - (self.counts["resOn"] / self.counts["resOff"])

        on_data = unp.uarray(self.counts["resOn"], self.error["resOn"])
        off_data = unp.uarray(self.counts["resOff"], self.error["resOff"])
        depletion_exp_with_err = 1 - (on_data / off_data)

        self.depletion_exp_err = unp.std_devs(depletion_exp_with_err)

        A_init = 0.5

        pop_depletion, popc_depletion = curve_fit(
            self.Depletion,
            self.fitX,
            self.depletion_fitted,
            sigma=self.depletion_fitted_err,
            absolute_sigma=True,
            p0=[A_init],
            bounds=[(0), (1)],
        )

        perr_depletion = np.sqrt(np.diag(popc_depletion))
        A = pop_depletion[0]
        A_err = perr_depletion[0]
        self.uA = uf(A, A_err)
        self.depletion_output_label.setText(f"A = {self.uA:.2f}")
        self.relative_abundance = self.Depletion(self.fitX, A)

        if plot:
            self.ax1.errorbar(
                self.power["resOn"], self.depletion_exp, fmt="k.", yerr=self.depletion_exp_err, label="Experiment"
            )
            (self.relativeFit_plot,) = self.ax1.plot(
                self.fitX,
                self.relative_abundance,
                "-k",
                animated=True,
                label=self.depletion_output_label.text(),
            )


def main(arguments):
    location: str = arguments["currentLocation"]
    resOnFile: pt = pt(location) / arguments["resON_Files"]
    resOffFile: pt = pt(location) / arguments["resOFF_Files"]
    power: np.array = np.asarray(arguments["power"].split(","), dtype=float)
    nshots = int(arguments["nshots"])
    massIndex = int(arguments["massIndex"])
    timestartIndex = int(arguments["timestartIndex"])
    saveOutputDepletion = arguments["saveOutputDepletion"]
    depletionplot_figure_kwargs = arguments["$depletionplot_figure_kwargs"]

    depletionplot(
        location,
        resOnFile,
        resOffFile,
        power,
        nshots,
        massIndex,
        timestartIndex,
        saveOutputDepletion,
        depletionplot_figure_kwargs,
    )
