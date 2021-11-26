
# Built-In modules
import json, sys, traceback
from pathlib import Path as pt

# DATA analysis modules
import numpy as np
from scipy.optimize import curve_fit
from uncertainties import ufloat as uf, unumpy as unp

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# FELion modules
from FELion_widgets import FELion_Tk
from timescan import timescanplot

from tkinter.messagebox import showerror, showinfo, showwarning, askokcancel

np.seterr(all="ignore")

class depletionplot:
    
    def __init__(self, location, resOnFile=None, resOffFile=None, power=None, nshots=10, massIndex=0, timestartIndex=1, saveOutputDepletion=True):
        self.location = pt(location)
        self.scanfiles = list(self.location.glob("*.scan"))
        self.resOnFile = resOnFile

        self.resOffFile = resOffFile

        self.power = {"resOn": power[0]/1000, "resOff": power[1]/1000} # mJ to J
        self.powerStr = f"{power[0]}, {power[1]}"
        self.nshots = nshots
        self.massIndex = massIndex
        self.timestartIndex = timestartIndex

        self.widget = FELion_Tk(title="Depletion Plot", location=self.location)
        self.create_figure()

        self.startPlotting()
        if saveOutputDepletion: self.saveFile(show=False)
        self.widget.mainloop()
        
    def create_figure(self):
        
        self.fig, self.canvas = self.widget.Figure(default_widget=False, default_save_widget=False, executeCodeWidget=False, dpi=200)
        self.fig.suptitle("Depletion Scan")
        self.fig.subplots_adjust(top=0.86, bottom=0.20, right=0.97, wspace=0.34)
        self.ax0 = self.fig.add_subplot(121)
        self.ax1 = self.fig.add_subplot(122)

    def change_title(self, event=None): 
        self.fig.suptitle(self.widget.plotTitle.get())
        self.canvas.draw()

    def change_grid(self, event=None):
        self.ax0.grid(not self.grid.get())
        self.ax1.grid(not self.grid.get())
        self.canvas.draw()

    def change_legend(self, event=None):

        self.ax0.legend([]).set_visible(not self.plotlegend.get())

        self.ax1.legend([]).set_visible(not self.plotlegend.get())
        if not self.plotlegend.get():

            fontSz = self.legend_slider.get()
            self.ax0.legend(labels=[self.lg1, self.lg2], title=f"Mass: {self.mass[0]}u, Res: {self.t_res}V, B0: {self.t_b0}ms", fontsize=fontSz, title_fontsize=fontSz+2)
            self.ax1.legend(["Fitted", f"A: {self.uA:.3uP}", "Experiment"], fontsize=fontSz+5)

        self.canvas.draw()

    def change_legend_size(self, event=None):
        fontSz = self.legend_slider.get()

        self.ax0.legend(labels=[self.lg1, self.lg2], title=f"Mass: {self.mass[0]}u, Res: {self.t_res}V, B0: {self.t_b0}ms", fontsize=fontSz, title_fontsize=fontSz+2)
        self.ax1.legend(["Fitted", f"A: {self.uA:.3uP}", "Experiment"], fontsize=fontSz+5)
        self.canvas.draw()

    def depletion_widgets(self, Koff, Kon, N, Na0, Nn0):

        # Position
        x0, x_diff = 0.1, 0.4
        y, y_diff = 0.14, 0.05

        # Row 1
        self.widget.plotTitle = self.widget.Entries("Entry", "Depletion Scan", x0, y, bind_key=True, bind_func=self.change_title, relwidth=0.7)

        # Row 2
        y += y_diff
        self.widget.koff_slider = self.widget.Sliders("Koff", Koff, x0, y, self.update, relwidth=0.5)
        self.widget.n_slider = self.widget.Sliders("N", N, x0, y+y_diff, self.update, relwidth=0.5)
        self.widget.kon_slider = self.widget.Sliders("Kon", Kon, x0, y+2*y_diff, self.update, relwidth=0.5)
        self.widget.na_slider = self.widget.Sliders("Na", Na0, x0, y+3*y_diff, self.update, relwidth=0.5)
        self.widget.nn_slider = self.widget.Sliders("Nn", Nn0, x0, y+4*y_diff, self.update, relwidth=0.5)

        # Row 3
        y += 5*y_diff
        self.widget.Labels("ON", x0, y)
        self.widget.Labels("OFF", x0+x_diff, y)

        # Row 4
        y += y_diff
        scanfiles_name = [name.name for name in self.scanfiles]

        self.widget.resOnList = self.widget.Dropdown(scanfiles_name, x0, y)
        self.widget.resOnList.set(self.resOnFile.name)
        self.widget.resOffList = self.widget.Dropdown(scanfiles_name, x0+x_diff, y)
        self.widget.resOffList.set(self.resOffFile.name)

        # Row 5

        y += y_diff
        self.new_power = self.widget.Entries("Entry", self.powerStr, x0, y)
        
        self.new_nshots = self.widget.Entries("Entry", self.nshots, x0+x_diff, y)

        # Row 6
        y += y_diff
        self.widget.Labels("MassIndex", x0, y)
        self.widget.Labels("TimeStartIndex", x0+x_diff, y)

        # Row 7
        y += y_diff
        self.new_massIndex = self.widget.Entries("Entry", self.massIndex, x0, y, bind_return=True, bind_func=self.replot)
        self.new_timeStart = self.widget.Entries("Entry", self.timestartIndex, x0+x_diff, y, bind_return=True, bind_func=self.replot)

        # Row 8
        y += y_diff
        self.submit = self.widget.Buttons("Replot", x0, y, self.replot)
        
        
        
        self.writeFile = self.widget.Buttons("Write", x0+x_diff, y, self.saveFile)

        # Row 9
        y += y_diff

        self.plotlegend = self.widget.Entries("Check", "Legend", x0, y, relwidth=0.2, default=True, bind_btn=True, bind_func = self.change_legend)
        self.legend_slider = self.widget.Sliders("", 5, x0+x_diff/2, y+0.02, self.change_legend_size, relwidth=0.3)

        # Row 10
        y += y_diff
        self.grid = self.widget.Entries("Check", "Grid", x0, y, default=True, bind_btn=True, bind_func = self.change_grid)
        
        # Row 11
        
        y += y_diff
        self.latex = self.widget.Entries("Check", "Latex", x0, y)
        self.save_fig = self.widget.Buttons("Save", x0+x_diff, y, self.savefig)

    def replot(self, event=None):

        self.ax0.clear()
        self.ax1.clear()

        self.resOnFile = self.location / self.widget.resOnList.get()
        self.resOffFile = self.location / self.widget.resOffList.get()
        
        power = np.asarray(self.new_power.get().split(","), dtype=float)
        self.power = {"resOn": power[0]/1000, "resOff": power[1]/1000} # mJ to J

        self.nshots = self.new_nshots.get()
        self.massIndex = int(self.new_massIndex.get())

        self.timestartIndex = int(self.new_timeStart.get())
        
        print(f"ON: {self.resOnFile}\nOFF: {self.resOffFile}\nPower: {self.power}\nMassIndex: {self.massIndex}\nTimeStartIndex: {self.timestartIndex}")
        self.startPlotting(make_slider_widget=False)
        self.canvas.draw()

    def saveFile(self, event=None, show=True):
        depletion_dir = self.location / "depletion_output"

        if not depletion_dir.exists(): depletion_dir.mkdir()
        timescanfile_reduced = depletion_dir / f"{self.resOnFile.stem}__{self.resOffFile.stem}.rscan"
        timescanfile_fitted = depletion_dir / f"{self.resOnFile.stem}__{self.resOffFile.stem}.fscan"

        with open(timescanfile_reduced, "w+") as f:

            f.write("# time(s)\tpowerOn(J)\tcountsOn\terrOn\tpowerOff(J)\tcountsOff\terroff\tDep_exp\tDep_exp_err\t\n")

            for time, powerOn, powerOff, countsOn, countsOff, errOn, errOff, dep_exp, dep_exp_err, in zip(self.time["resOn"], self.power["resOn"], self.power["resOff"], self.counts["resOn"], self.counts["resOff"], self.error["resOn"], self.error["resOff"], self.depletion_exp, self.depletion_exp_err):

                f.write(f"{time:.4f}\t{powerOn:.4f}\t{countsOn:.4f}\t{errOn:.4f}\t{powerOff:.4f}\t{countsOff:.4f}\t{errOff:.4f}\t{dep_exp:.4f}\t{dep_exp_err:.4f}\n")
            #if show: showinfo("File saved", f"File saved: {timescanfile_reduced.name} in {self.location}")
            print(f"File saved: {f.name} in {self.location}")
        with open(timescanfile_fitted, "w+") as f:
            
            self.uA = self.uA*100
            f.write(f"####################################### \n# A={self.uA.nominal_value:.2f}({self.uA.std_dev:.2f}) %\n")
            
            f.write(f"# {self.writelg1}\n# {self.writelg2}\n# FELIX_Shots={self.nshots}\n# Power (mJ)[On, Off]=[{self.powerStr}]\n# ResOn File:{self.resOnFile.name}, ResOff File:{self.resOffFile.name}\n")

            f.write(f"# Mass: {self.mass[0]}u, Res: {self.t_res}V, B0: {self.t_b0}ms\n")
            f.write("####################################### \n")
            f.write("# fitX(J)\tfitOn\tfitOff\t(1-fitOff/fitOn)\tDepl_fit\n")
            
            for fitX, fitOn, fitOff, dep_fit, rel_abun in zip(self.fitX, self.fitOn, self.fitOff, self.depletion_fitted, self.relative_abundance):
                f.write(f"{fitX:.4f}\t{fitOn:.4f}\t{fitOff:.4f}\t{dep_fit:.4f}\t{rel_abun:.4f}\n")
            if show: showinfo("File saved", f"File saved: {f.name} in {self.location}")
            print(f"File saved: {f.name} in {self.location}")
            
    def startPlotting(self, make_slider_widget=True):
        try:

            self.ax0.set(xlabel="n*t*E (J)", ylabel="Counts", title=f"ON:{self.resOnFile.name}\nOFF:{self.resOffFile.name}")
            self.ax1.set(xlabel="n*t*E (J)", ylabel="Relative abundace of active isomer", title="$D(t)=A*(1-e^{-K_{ON}*(ntE)})$")
            for ax in (self.ax0, self.ax1): ax.grid()
            
            # Get timescan details
            self.get_timescan_data()

            # Fitt resOff and resOn
            Koff, N = self.resOff_fit()
            Na0, Nn0, Kon = self.resOn_fit(Koff, N)

            # if make_slider_widget: self.make_slider(Koff, Kon, N, Na0, Nn0)
            if make_slider_widget: self.depletion_widgets(Koff, Kon, N, Na0, Nn0)
            else:
                self.widget.koff_slider.set(Koff)
                self.widget.n_slider.set(N)
                self.widget.kon_slider.set(Kon)
                self.widget.na_slider.set(Na0)
                self.widget.nn_slider.set(Nn0)
            self.runFit(Koff, Kon, N, Na0, Nn0)
        except: showerror("Error occured", traceback.format_exc(5))

    def runFit(self, Koff, Kon, N, Na0, Nn0, plot=True):
        
        uKoff = uf(Koff, self.Koff_err)
        
        uN = uf(N, self.N_err)
        uNa0 = uf(Na0, self.Na0_err)
        uNn0 = uf(Nn0, self.Nn0_err)
        uKon = uf(Kon, self.Kon_err)
        # self.lg1 = f"Kon: {uKon:.3uP}, Na: {uNa0:.2uP}, Nn: {uNn0:.2uP}"

        self.lg1 = self.writelg1 = f"Kon: {Kon:.2f}({self.Kon_err:.2f}), Na: {Na0:.2f}({self.Na0_err:.2f}), Nn: {Nn0:.2f}({self.Nn0_err:.2f})"

        # self.lg2 = f"Koff: {uKoff:.2uP}, N: {uN:.2uP}"

        self.lg2 = self.writelg2 = f"Koff: {Koff:.2f}({self.Koff_err:.2f}), N: {N:.2f}({self.N_err:.2f})"
        print("Legend: ", self.lg1, self.lg2)

        self.ax0.legend(labels=[self.lg1, self.lg2], title=f"Mass: {self.mass[0]}u, Res: {self.t_res}V, B0: {self.t_b0}ms", fontsize=5, title_fontsize=7)
        self.get_depletion_fit(Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon, plot)

        self.get_relative_abundance_fit(plot)

        self.ax1.legend(["Fitted", f"A: {self.uA:.3uP}", "Experiment"], fontsize=5, title_fontsize=7)

    def update(self, event=None):

        Koff = self.widget.koff_slider.get()
        Kon = self.widget.kon_slider.get()
        N = self.widget.n_slider.get()
        Na0 = self.widget.na_slider.get()
        Nn0 = self.widget.nn_slider.get()
        
        self.runFit(Koff, Kon, N, Na0, Nn0, plot=False)
        self.ax0_plot["resOn"].set_ydata(self.fitOn)

        self.ax0_plot["resOff"].set_ydata(self.fitOff)
        self.fit_plot.set_ydata(self.depletion_fitted)
        self.relativeFit_plot.set_ydata(self.relative_abundance)
        self.canvas.draw_idle()

        self.saveFile(show=False)

    def savefig(self):
        try:

            # if not self.latex.get():
            save_name = f"{self.widget.name.get()}.png"
            save_file = self.location / save_name
            self.fig.savefig(save_file, dpi=self.widget.dpi_value.get())
            print(f"File saved: {save_name} in {self.location}")
            showinfo("Saved", f"File saved: {save_name} in {self.location}")
            # else: self.latexPlot()
        except: showerror("Error occured", traceback.format_exc(5))

    # def latexPlot(self):

    #     style_path = pt(__file__).parent / "matplolib_styles/styles/science.mplstyle"
    #     with plt.style.context([f"{style_path}"]):

    #         fig, ax0 = plt.subplots()
    #         fig2, ax1 = plt.subplots()
    #         on = self.resOnFile.name.replace("_", "\_")
    #         off = self.resOffFile.name.replace("_", "\_")
    #         ax0.set(xlabel="n*t*E (mJ)", ylabel="Counts", title=f"ON:{on}\nOFF:{off}")
    #         ax1.set(xlabel="n*t*E (mJ)", ylabel="Relative abundace of active isomer", title="$D(t)=A*(1-e^{-K_{ON}*(ntE)})$")
    #         ax0.grid()

    #         ax1.grid()

    #         for index, fitY, i in zip(["resOn", "resOff"], [self.fitOn, self.fitOff], [0, 1]):
    #             ax0.errorbar(self.power[index], self.counts[index], yerr=self.error[index], fmt=f"C{i}.")
    #             ax0.plot(self.fitX, fitY, f"C{i}")

    #         ax1.errorbar(self.power["resOn"], self.depletion_exp, yerr=self.depletion_exp_err, fmt="k.")
    #         ax1.plot(self.fitX, self.depletion_fitted)
    #         ax1.plot(self.fitX, self.relative_abundance)
    #         ax0.legend(labels=["ResON", "ResOFF"], title=f"Mass: {self.mass[0]}u, Res: {self.t_res}V, B0: {self.t_b0}ms")
    #         ax1.legend(["Fitted", f"A: {self.uA:.3f}", "Experiment"])

    #         save_name = f"{self.widget.name.get()}_timescan.png"
    #         save_name2 = f"{self.widget.name.get()}_depletion.png"
    #         save_file = self.location / save_name
    #         save_file2 = self.location / save_name2

    #         fig.savefig(save_file, dpi=self.widget.dpi_value.get()*3)
    #         fig2.savefig(save_file2, dpi=self.widget.dpi_value.get()*3)

    #         showinfo("Saved", f"File saved: {save_name} and {save_name2} \nin {self.location}")
    
    def get_timescan_data(self):

        self.time = {"resOn":[], "resOff": []}
        self.counts = {"resOn":[], "resOff": []}
        self.error = {"resOn":[], "resOff": []}
        self.ax0_plot = {}

        for index, scanfile, i in zip(["resOn", "resOff"], [self.resOnFile, self.resOffFile], [0, 1]):

            
            time, counts, error, self.mass, self.t_res, self.t_b0 = timescanplot(scanfile).get_data()
            time = time/1000 # ms to s
            ind = np.where(error==0)
            error[ind] = 1e-5

            self.time[index] = np.array(time[self.timestartIndex:])
            self.counts[index] = np.array(counts[self.massIndex][self.timestartIndex:])
            self.error[index] = np.array(error[self.massIndex][self.timestartIndex:])
            self.power[index] = np.array((self.power[index] * self.nshots * self.time[index]))
            self.ax0.errorbar(self.power[index], self.counts[index], yerr=self.error[index], fmt=f"C{i}.")

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
        self.Koff_err, self.N_err= perr_off     
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

    def uN_OFF(self, x, uN, uK_OFF): return uN*unp.exp(-uK_OFF*x)

    def uN_ON(self, x, uNa0, uNn0, uK_OFF, uK_ON): return uNa0 * \
        unp.exp(-uK_ON*x)*unp.exp(-uK_OFF*x) + uNn0*unp.exp(-uK_OFF*x)
        
    def get_depletion_fit(self, Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon, plot=True):
        
        self.Kon = Kon
        self.Koff = Koff

        maxPower = np.append(self.power["resOn"], self.power["resOff"]).max()*2
        self.fitX = np.linspace(0, maxPower, self.size)
        print(len(self.fitX))
        ufitX = unp.uarray(self.fitX, np.zeros(len(self.fitX)))

        self.fitOn = self.N_ON(self.fitX, Na0, Nn0, self.Kon)
        self.fitOff = self.N_OFF(self.fitX, Koff, N)

        self.fitOn_with_err = self.uN_ON(ufitX, uNa0, uNn0, uKoff, uKon)
        self.fitOff_with_err = self.uN_OFF(ufitX, uKoff, uN)

        print(len(self.fitX), len(self.fitOn))
        
        self.fitted_counts_error = {"resOn": unp.std_devs(self.fitOn_with_err), "resOff": unp.std_devs(self.fitOff_with_err)}
        print(f"Exp counts error: {self.error}\nFitted counts error: {self.fitted_counts_error}\n")

        self.fitted_counts = {"resOn":np.array(self.fitOn), "resOff": np.array(self.fitOff)}
        print(f"Counts: {self.counts}\nFitted: {self.fitted_counts}\n")

        if plot:
            for index, fitY, i in zip(["resOn", "resOff"], [self.fitOn, self.fitOff], [0, 1]):
                self.ax0_plot[index], = self.ax0.plot(self.fitX, fitY, f"C{i}")

    def Depletion(self, x, A):
            K_ON = self.Kon
            return A*(1-np.exp(-K_ON*x))

    def get_relative_abundance_fit(self, plot=True):

        self.depletion_fitted = 1 - (self.fitted_counts["resOn"]/self.fitted_counts["resOff"])
        depletion_fitted_with_err = 1 - (unp.uarray(self.fitted_counts["resOn"], self.fitted_counts_error["resOn"])/unp.uarray(self.fitted_counts["resOff"], self.fitted_counts_error["resOff"]))
        self.depletion_fitted_err = unp.std_devs(depletion_fitted_with_err)

        self.depletion_exp = 1 - (self.counts["resOn"]/self.counts["resOff"])
        depletion_exp_with_err = 1 - (unp.uarray(self.counts["resOn"], self.error["resOn"])/unp.uarray(self.counts["resOff"], self.error["resOff"]))
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
        print(f"A: {self.uA:.3uP}")

        self.relative_abundance = self.Depletion(self.fitX, A)

        if plot:
            self.ax1.errorbar(self.power["resOn"], self.depletion_exp, yerr=self.depletion_exp_err, fmt="k.")
            self.fit_plot, = self.ax1.plot(self.fitX, self.depletion_fitted)

            self.relativeFit_plot, = self.ax1.plot(self.fitX, self.relative_abundance)

if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")
    arguments = json.loads(", ".join(args))
    print(f"{arguments=}", flush=True)

    location = arguments["currentLocation"]
    resOnFile = pt(location)/arguments["resON_Files"]
    resOffFile = pt(location)/arguments["resOFF_Files"]
    power = np.asarray(arguments["power"].split(","), dtype=float)
    nshots = int(arguments["nshots"])
    
    massIndex = int(arguments["massIndex"])
    timestartIndex = int(arguments["timestartIndex"])
    saveOutputDepletion = arguments["saveOutputDepletion"]
    depletionplot(location, resOnFile, resOffFile, power, nshots, massIndex, timestartIndex, saveOutputDepletion)
    