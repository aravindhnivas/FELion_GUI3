# Built-in
import os, json, sys
from pathlib import Path as pt

# DATA Analysis
import numpy as np
import matplotlib.pyplot as plt

# FELion modules
from FELion_widgets import FELion_Tk
# from FELion_definitions import sendData


class felix_plot:
    
    def __init__(self, args):

        self.args = args

        self.felixlocation = pt(self.args["location"])
        self.datlocation = self.felixlocation / "../EXPORT"
        self.outlocation = self.felixlocation / "../OUT"
        self.theorylocation = pt(self.args["theoryLocation"])
        self.freqScale = self.args["scale"]
        self.theorySigma = self.args["sigma"]

        self.widget = FELion_Tk(title="FELIX Plot", location=self.outlocation)

        self.fig, self.canvas = self.widget.Figure(default_widget=False, dpi=120)
        self.fig.suptitle("FELIX Plot")
        self.fig.subplots_adjust(top=0.86, bottom=0.20, right=0.97, wspace=0.34)
        self.ax0 = self.fig.add_subplot(211)
        self.ax1 = self.fig.add_subplot(212)


        self.felix_widgets()
    
        self.widget.mainloop()

    
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
        # if not self.plotlegend.get():

        #     fontSz = self.legend_slider.get()
        #     self.ax0.legend(labels=[self.lg1, self.lg2], title=f"Mass: {self.mass[0]}u, Res: {self.t_res}V, B0: {self.t_b0}ms", fontsize=fontSz, title_fontsize=fontSz+2)
        #     self.ax1.legend(["Fitted", f"A: {self.uA:.3uP}", "Experiment"], fontsize=fontSz+5)

        self.canvas.draw()

    def felix_widgets(self):

        # # Position
        x0, x_diff = 0.1, 0.4
        y, y_diff, y_diff2 = 0.14, 0.05, 0.09

        # Row 1

        self.widget.plotTitle = self.widget.Entries("Entry", "FELIX Plot", x0, y, bind_key=True, bind_func=self.change_title, relwidth=0.7)

        # Row 2
        y += y_diff
        datfiles = [datfile.name for datfile in self.datlocation.glob("*.dat")]
        self.widget.datfile = self.widget.Dropdown(datfiles, x0, y, relwidth=0.7)

        self.widget.datfile.set("averaged.dat")

        # Row 3
        y += y_diff2
        theoryfiles = [theoryfile.name for theoryfile in self.theorylocation.glob("*.*")]

        self.widget.theoryfiles = self.widget.Listbox(theoryfiles, x0, y, relwidth=0.7, relheight=0.1)
        # self.theoryfiles = self.theoryfiles.curselection()

        # Row 4
        y += y_diff2
        self.widget.Labels("Overtones & Combinations", x0, y, relwidth=0.75)
        self.widget.overtonefiles = self.widget.Listbox(theoryfiles, x0, y+y_diff2, relwidth=0.7, relheight=0.1)
        self.widget.combinationfiles = self.widget.Listbox(theoryfiles, x0, y+2.2*y_diff2, relwidth=0.7, relheight=1.2)
        # self.overtonefiles = self.overtonefiles.curselection()
        # self.combinationfiles = self.combinationfiles.curselection()


        # Row5
        y += 5.6*y_diff
        self.widget.Labels("Sigma & scale", x0, y, relwidth=0.7)
        

        # # Row6
        y += y_diff
        self.widget.theorySigma = self.widget.Entries("Entry", self.theorySigma, x0, y)
        self.widget.freqScale = self.widget.Entries("Entry", self.freqScale, x0+x_diff, y)

        # Row7
        y += y_diff
        self.grid = self.widget.Entries("Check", "Grid", x0, y, default=True, bind_btn=True, bind_func = self.change_grid)
        self.plotlegend = self.widget.Entries("Check", "Legend", x0+x_diff, y, default=True, bind_btn=True, bind_func = self.change_legend)

        # Row8
        y += y_diff
        self.invert_ax2 = self.widget.Entries("Check", "invert_ax2", x0, y, default=True)

        self.hide_axis = self.widget.Entries("Check", "hide_axis", x0+x_diff, y, default=False)


        # Row9

        y += y_diff
        self.onlyExp = self.widget.Entries("Check", "onlyExp", x0, y, default=True, bind_btn=False)
        self.hide_axeses = self.widget.Entries("Check", "hide_axeses", x0+x_diff, y, default=False)
        
        
        # # Row 9
        # y += y_diff

        # self.plotlegend = self.widget.Entries("Check", "Legend", x0, y, relwidth=0.2, default=True, bind_btn=True, bind_func = self.change_legend)
        # self.legend_slider = self.widget.Sliders("", 5, x0+x_diff/2, y+0.02, self.change_legend_size, relwidth=0.3)

        # # Row 10
        # y += y_diff
        # self.grid = self.widget.Entries("Check", "Grid", x0, y, default=True, bind_btn=True, bind_func = self.change_grid)
        
        # # Row 11
        
        # y += y_diff
        # self.latex = self.widget.Entries("Check", "Latex", x0, y)
        # self.save_fig = self.widget.Buttons("Save", x0+x_diff, y, self.savefig)

        
        

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))
    print(f"Received args: {args}, {type(args)}\n")
    felix = felix_plot(args)