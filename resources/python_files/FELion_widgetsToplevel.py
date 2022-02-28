
# Built-In modules
import os, sys, time, traceback
from os.path import isfile
from pathlib import Path as pt
from io import StringIO
import contextlib

# Tkinter
from tkinter import StringVar, BooleanVar, DoubleVar, Toplevel, END, Text, MULTIPLE, Listbox, Canvas, Frame
from tkinter.ttk import Button, Checkbutton, Label, Entry, Scale, Scrollbar, OptionMenu
from tkinter.messagebox import showerror, showinfo, showwarning, askokcancel

# Matplotlib
from matplotlib import style
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

constants = {
    'relwidth': 0.3,
    'relheight': 0.04,
    "anchor": "w",
    "slider_orient": "horizontal"
}

def var_check(kw):
    
    for i in constants:
        if not i in kw: kw[i] = constants[i]
    return kw


class FELion_TkToplevel(Toplevel):

    def __init__(self, title="Figure widget", location=".", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.location = pt(location)
        os.chdir(self.location)

        self.wm_title(title)
        self.wm_geometry("1000x600")
        
        self.canvas_frame = Frame(self, bg='white')
        self.canvas_frame.place(relx=0, rely=0, relwidth=0.8, relheight=1)

        widget_frame_container = Frame(self)
        widget_frame_canvasContainer = Canvas(widget_frame_container)

        widget_frame_canvasContainer.config(takefocus=True)
        scrollbar = Scrollbar(widget_frame_container, orient="vertical", command=widget_frame_canvasContainer.yview)

        self.widget_frame = Frame(widget_frame_canvasContainer)
        self.widget_frame.config(takefocus=False)
        self.widget_frame.bind( "<Configure>", lambda e: widget_frame_canvasContainer.configure(
                scrollregion=widget_frame_canvasContainer.bbox("all") ))

        widget_frame_canvasContainer.create_window((0, 0), window=self.widget_frame)
        widget_frame_canvasContainer.configure(yscrollcommand=scrollbar.set)

        widget_frame_container.place(relx=0.8, rely=0, relwidth=0.2, relheight=1)
        widget_frame_canvasContainer.place(relx=0, rely=0, relwidth=0.9, relheight=1)

        scrollbar.place(relx=0.9, rely=0, relwidth=0.1, relheight=1)
        
        self.widget_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        def focusCanvas(event):
        
            if event.keycode == 27: 
                self.canvas._tkcanvas.focus_set()

        self.bind('<KeyRelease>', focusCanvas)

    def Labels(self, txt, x, y, **kw):
        kw = var_check(kw)
        
        self.widget_frame.txt = Label(self.widget_frame, text=txt)
        self.widget_frame.txt.place(
            relx=x, rely=y, anchor=kw['anchor'], relwidth=kw['relwidth'], relheight=kw['relheight'])
        return self.widget_frame.txt

    def Sliders(self, txt, value, x, y, bind_func, **kw):
        kw = var_check(kw)

        self.Labels(txt, x, y, relwidth=0.2)
        self.widget_frame.value = DoubleVar()
        self.widget_frame.value.set(value)

        self.widget_frame.scale = Scale(
            self.widget_frame, variable=self.widget_frame.value, from_=0, to=value*10, orient=kw["slider_orient"])

        self.widget_frame.scale.bind("<B1-Motion>", bind_func)
        self.widget_frame.scale.place(
            relx=x+0.2, rely=y, anchor=kw['anchor'], relwidth=kw['relwidth'], relheight=kw['relheight'])

        return self.widget_frame.value

    def Buttons(self, btn_txt, x, y, *args, **kw):

        kw = var_check(kw)

        if len(args) == 1:

            func = args[0]
            self.widget_frame.btn_txt = Button(
                self.widget_frame, text=btn_txt, command=lambda: func())
        elif len(args) > 1:
            func = args[0]
            func_parameters = args[1:]

            print(func, func_parameters)
            self.widget_frame.btn_txt = Button(
                self.widget_frame, text=btn_txt, command=lambda: func(*func_parameters))

        else:
            self.widget_frame.btn_txt = Button(
                self.widget_frame, text=btn_txt, command=lambda: print("No function set"))

        self.widget_frame.btn_txt.place(
            relx=x, rely=y, relwidth=kw['relwidth'], relheight=kw['relheight'])

        return self.widget_frame.btn_txt

    def Entries(self, method, txt, x, y, bind_return=False, bind_key=False, bind_btn=False, **kw):

        kw = var_check(kw)

        if method == 'Entry':

            if isinstance(txt, str):
                self.widget_frame.txt = StringVar()
            else:
                self.widget_frame.txt = DoubleVar()

            self.widget_frame.txt.set(txt)

            self.widget_frame.entry = Entry(
                self.widget_frame, textvariable=self.widget_frame.txt)

            if bind_return:
                self.widget_frame.entry.bind("<Return>", kw["bind_func"])
            if bind_key:
                self.widget_frame.entry.bind("<Key>", kw["bind_func"])

            self.widget_frame.entry.place(
                relx=x, rely=y, anchor=kw['anchor'], relwidth=kw['relwidth'], relheight=kw['relheight'])

            return self.widget_frame.txt

        elif method == 'Check':

            self.widget_frame.txt = BooleanVar()

            if 'default' in kw:
                self.widget_frame.txt.set(kw['default'])
            else:
                self.widget_frame.txt.set(False)

            self.widget_frame.Check = Checkbutton(
                self.widget_frame, text=txt, variable=self.widget_frame.txt)
            if bind_btn:
                self.widget_frame.Check.bind(
                    "<ButtonRelease-1>", kw["bind_func"])
            self.widget_frame.Check.place(
                relx=x, rely=y, relwidth=kw['relwidth'], relheight=kw['relheight'])

            return self.widget_frame.txt

    def TextBox(self, txt, x, y, w, h, **kw):

        # Scrollbar
        self.widget_frame.scrollbar = Scrollbar(self.widget_frame)

        # Textbox
        self.widget_frame.txt = Text(self.widget_frame)
        self.widget_frame.scrollbar.config(command=self.widget_frame.txt.yview)

        if "bind_func" in kw: self.widget_frame.txt.bind("<Alt-Up>", kw["bind_func"])
        self.widget_frame.txt.config(yscrollcommand=self.widget_frame.scrollbar.set)
        self.widget_frame.txt.insert(END, txt)

        self.widget_frame.scrollbar.place(relx=x, rely=y, anchor="w", relheight=h)
        self.widget_frame.txt.place(relx=x, rely=y, anchor="e", relwidth=w, relheight=h)
        return self.widget_frame.txt

    def Dropdown(self, options, x, y, value=None, **kw):
        kw = var_check(kw)

        if value is not None: value1 = value
        else: value1 = options[0]
        if isinstance(value1, str): self.widget_frame.value1 = StringVar()
        else: self.widget_frame.value1 = DoubleVar()
        self.widget_frame.value1.set(value1)

        self.widget_frame.dropdown_options = OptionMenu(self.widget_frame, self.widget_frame.value1, *options)
        self.widget_frame.dropdown_options.place(relx=x, rely=y, anchor=kw['anchor'], relwidth=kw['relwidth'], relheight=kw['relheight'])

        return self.widget_frame.value1

    def Listbox(self, lists, x, y, **kw):

        kw = var_check(kw)

        self.widget_frame.listbox = Listbox(self.widget_frame, listvariable=lists, selectmode=MULTIPLE)
        self.widget_frame.listbox.place(relx=x, rely=y, anchor=kw['anchor'], relwidth=kw['relwidth'], relheight=kw['relheight'])

        # listNodes = Listbox(frame, width=20, height=20, font=("Helvetica", 12))
        # listNodes.pack(side="left", fill="y")

        scrollbar = Scrollbar(self.widget_frame, orient="vertical")
        scrollbar.config(command=self.widget_frame.listbox.yview)
        scrollbar.place(relx=0.9-x, rely=y-0.05, relheight=kw['relheight'])

        self.widget_frame.listbox.config(yscrollcommand=scrollbar.set)

        for item in lists: self.widget_frame.listbox.insert(END, item)


        return self.widget_frame.listbox

    def Figure(self, connect=True, dpi=None, default_widget=True, default_save_widget=True, executeCodeWidget = True, **kw):

        self.default_widget = default_widget

        self.default_save_widget = default_save_widget

        self.executeCodeWidget = executeCodeWidget

        self.make_figure_widgets()
        if dpi is not None: self.dpi_value.set(dpi)

        self.fig = Figure(dpi=self.dpi_value.get())
        self.fig.subplots_adjust(top=0.95, bottom=0.2, left=0.1, right=0.9)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)

        self.fig_tkcanvas = self.canvas.get_tk_widget()
        self.fig_tkcanvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()

        def on_key_press(event): 
            key_press_handler(event, self.canvas, self.toolbar)

            self.canvas._tkcanvas.focus_set()

        if connect: 
            
            self.canvas.mpl_connect("key_press_event", on_key_press)
            self.canvas.mpl_connect("button_release_event", lambda event: self.canvas._tkcanvas.focus_set())

        return self.fig, self.canvas
    
    def make_figure_widgets(self):

        # Position
        x0, self.x_diff = 0.1, 0.4
        y, self.y_diff = 0, 0.05

        # Row 1
        y += self.y_diff
        self.label_dpi = self.Labels("DPI", x0, y)
        self.dpi_value = self.Entries("Entry", 120, x0+self.x_diff, y, bind_return=True, bind_func=self.set_figureLabel)

        # Row 2
        y += self.y_diff
        self.name = self.Entries("Entry", "savefile_name", x0, y, bind_return=True, bind_func=self.save_fig, relwidth=0.7)
        self.last_y = y

        if self.default_widget:

            # Row 3
            y += self.y_diff
            self.plotTitle = self.Entries("Entry", "Title", x0, y, bind_key=True, bind_func=self.set_figureLabel, relwidth=0.5)
            self.titleSz = self.Entries("Entry", 12, x0+self.x_diff+0.1, y, bind_return=True, bind_func=self.set_figureLabel, relwidth=0.2)

            # Row 4
            y += self.y_diff
            self.plotXlabel = self.Entries("Entry", "X-axis", x0, y, bind_key=True, bind_func=self.set_figureLabel, relwidth=0.5)
            self.xlabelSz = self.Entries("Entry", 10, x0+self.x_diff+0.1, y, bind_return=True, bind_func=self.set_figureLabel, relwidth=0.2)

            # Row 5
            y += self.y_diff
            self.plotYlabel = self.Entries("Entry", "Y-axis", x0, y, bind_key=True, bind_func=self.set_figureLabel, relwidth=0.5)
            self.ylabelSz = self.Entries("Entry", 10, x0+self.x_diff+0.1, y, bind_return=True, bind_func=self.set_figureLabel, relwidth=0.2)

            # Row 6
            y += self.y_diff
            self.plotFigText = self.Entries("Entry", "Figure 1", x0, y, bind_key=True, bind_func=self.set_figureLabel, relwidth=0.5)
            self.figtextFont = self.Entries("Entry", 12, x0+self.x_diff+0.1, y, bind_return=True, bind_func=self.set_figureLabel, relwidth=0.2)

            # Row 7
            y += self.y_diff
            self.plotGrid = self.Entries("Check", "Grid", x0, y, default=True, bind_btn=True, bind_func=self.set_figureLabel)
            self.plotLegend = self.Entries("Check", "Lg", x0+self.x_diff, y, default=True, bind_btn=True, bind_func=self.set_figureLabel)

            # Row 8
            y += self.y_diff
            self.plotYscale = self.Entries("Check", "Ylog", x0+self.x_diff, y, default=False, bind_btn=True, bind_func=self.set_figureLabel)
            # self.latex = self.Entries("Check", "LaTex", x0, y, default=False)

            self.last_y = y

        if self.default_save_widget:

            # Row 9
            
            y += self.y_diff
            self.save_fmt = self.Entries("Entry", "png", x0, y+0.02)
            self.save_btn = self.Buttons("Save", x0+self.x_diff, y, self.save_fig)

            # Row 10
            # y += self.y_diff
            # self.onlyAvg = self.Entries("Check", "only avg.", x0, y+0.02)
            self.last_y = y
        
        if self.executeCodeWidget:

            #  Row 11
            y = 0.7
            txt = "Write valid any python expression"
            self.code = self.TextBox(txt, 0.8, y, w=0.7, h=0.1, bind_func=self.python_exp) 

            #  Row 12

            y += self.y_diff
            self.runCode = self.Buttons("RunCode", x0, y, self.python_exp)
            self.codeResult = self.TextBox("Result", 0.8, y+self.y_diff+0.04, w=0.7, h=0.09)
            self.x0 = x0


    def python_exp(self, event=None):
        with stdoutIO() as result:

            try:
                self.codeResult.delete('1.0', END)
                expr = self.code.get('1.0', END).split("\n")
                for i in expr[:-1]:
                    
                    self.codeResult.insert(END, f"DONE: {i}\n")

                    # Running the expression from input textbox
                    exec(i)
                    output = result.getvalue().split("\n")[:-1]

                    if not len(output)<1: self.codeResult.insert(END, f"Result: {output[-1]}\n")
                
                self.canvas.draw()

            except Exception as error:
                self.codeResult.delete('1.0', END)
                self.codeResult.insert(END, f"Error Occured:\n{error}")
                print(f"Error occured while evaluating above code:\n{error}")

    def set_figureLabel(self, event=None):

        if event is not None:

            widget_name = str(event.widget).split("!")[-1]

            print(widget_name)

            if widget_name == "entry":  # DPI

                self.fig.set_dpi(self.dpi_value.get())

                width = self.canvas_frame.winfo_width()/self.dpi_value.get()
                height = self.canvas_frame.winfo_height()/self.dpi_value.get()
                self.fig.set_size_inches(width, height)

            if widget_name == "entry3":  # Title
                self.entry_value = self.plotTitle.get() + event.char
                self.ax.set(title=self.entry_value.strip())
            
            if widget_name == "entry4":  # Title size
                self.ax.set_title(self.plotTitle.get(), fontsize=self.titleSz.get())

            if widget_name == "entry5":  # Xlabel
                self.entry_value = self.plotXlabel.get() + event.char
                self.ax.set(xlabel=self.entry_value.strip())

            if widget_name == "entry6":  # Xalbel fontsize
                self.ax.xaxis.label.set_size(self.xlabelSz.get())

            if widget_name == "entry7":  # Ylabel
                self.entry_value = self.plotYlabel.get() + event.char
                self.ax.set(ylabel=self.entry_value.strip())
            
            if widget_name == "entry8":  # Ylabel fontsize
                self.ax.yaxis.label.set_size(self.ylabelSz.get())

            if widget_name == "entry9":  # Figtext label
                self.entry_value = self.plotFigText.get() + event.char
                self.figtext.set_text(self.entry_value.strip())
            
            if widget_name == "entry10":  # Figtext fontsize
                self.figtext.set_fontsize(self.figtextFont.get())

            if widget_name == "checkbutton":  # Grid
                self.ax.grid(not self.plotGrid.get())

            if widget_name == "checkbutton2":  # Legend
                self.plot_legend.set_visible(not self.plotLegend.get())
            
            if widget_name == "checkbutton3":  # Yscale
                if self.plotYscale.get(): scale = "linear"
                else: scale = "log"
                self.ax.set(yscale=scale)
     
        
        self.canvas.draw()
        self.fig.tight_layout()
        self.canvas.draw()


    def make_figure_layout(self, ax=None, savename=None,
        title="Title", xaxis="X-axis", yaxis="Y-axis", fig_caption="", 
        xdata=None, ydata=None, label="", fmt=".-", yscale="linear", **kw):

        if savename is not None: self.name.set(savename)

        # Making subplot
        self.ax = ax
        if ax is None: self.ax = self.fig.add_subplot(111)

        # Plotting data if any:
        if xdata is not None: plot, = self.ax.plot(xdata, ydata, fmt, label=label, **kw)

        # Setting default title, xlabel and ylabel entries
        self.plotTitle.set(title)
        self.plotYlabel.set(yaxis)
        self.plotXlabel.set(xaxis)
        self.plotFigText.set(fig_caption)

        # Yscale
        self.ax.set(yscale=yscale)
        if yscale == "log": self.plotYscale.set(True)

        # Setting title
        self.ax.set_title(title, fontsize=self.titleSz.get())

        # Setting X and Y label
        self.ax.set(ylabel=yaxis, xlabel=xaxis)

        # Xlabel and Ylabel fontsize
        self.ax.xaxis.label.set_size(self.xlabelSz.get())
        self.ax.yaxis.label.set_size(self.ylabelSz.get())
        self.ax.tick_params(axis='x', which='major', labelsize=self.xlabelSz.get())
        self.ax.tick_params(axis='y', which='major', labelsize=self.ylabelSz.get())

        # Autominor locator
        self.set_minor = lambda x: self.ax.xaxis.set_minor_locator(AutoMinorLocator(x))
        self.set_minor(10)
        
        # self.ax.tick_params(which='minor', length=4, width=2, color='C1')
        # self.ax.tick_params(which='major', length=10, width=2)

        # Making axis available for modification
        self.xaxis = self.ax.xaxis
        self.yaxis = self.ax.yaxis
        self.grid = self.ax.grid
        self.legend = self.ax.legend

        # Grid
        self.ax.grid(self.plotGrid.get())

        # Figure caption
        self.figtext = self.fig.text(0.5, 0.07, self.plotFigText.get(), ha="center", wrap=True, fontsize=self.figtextFont.get())

        if xdata is not None: 
            print("Returning created plot for ax")
            self.plot_legend = self.ax.legend()

            return plot
        else:
            print("Returning created ax")

            return self.ax 
        
    def save_fig(self, event=None):
        save_fname = f"{self.name.get()}.{self.save_fmt.get()}"

        print(f"Saving filename: {save_fname}")
        save_filename = self.location / save_fname
        print(f"Saving file: {save_filename}")

        def savefig_latex():
            style_path = pt(__file__).parent / "matplolib_styles/styles/science.mplstyle"
            with style.context([f"{style_path}"]):
                self.fig2, self.ax2 = plt.subplots()
                for i, line in enumerate(self.ax.lines):
                    
                    x = line.get_xdata()
                    y = line.get_ydata()
                    lg = line.get_label().replace("_", "\_")
                    
                    if lg.endswith("felix"): ls = f"C{i}."
                    elif lg.startswith("Binned"): ls="k."
                    else: ls = f"C{i}-"

                    if lg.startswith("Averaged") or lg.startswith("Fitted"): self.ax2.plot(x, y, "k-", label=lg, zorder=100)
                    elif not self.onlyAvg.get(): self.ax2.plot(x, y, ls, ms=2, label=lg)
                
                self.ax2.grid()
                # self.ax2.set(xlim=[0, 40])
                legend = self.ax2.legend(bbox_to_anchor=[1, 1], fontsize=self.xlabelSz.get()/2)
                legend.set_visible(self.plotLegend.get())

                # Setting title
                self.ax2.set_title(self.plotTitle.get().replace("_", "\_"), fontsize=self.titleSz.get())

                # Setting X and Y label
                if self.plotYscale.get(): scale = "log"
                else: scale = "linear"
                self.ax2.set(yscale=scale)
                self.ax2.set(
                    ylabel=self.plotYlabel.get().replace("%", "\%"), 
                    xlabel=self.plotXlabel.get(),
                    xlim=self.ax.get_xlim(),
                    ylim=self.ax.get_ylim()
                )

                # Xlabel and Ylabel fontsize
                self.ax2.xaxis.label.set_size(self.xlabelSz.get())
                self.ax2.yaxis.label.set_size(self.ylabelSz.get())
                self.ax2.tick_params(axis='x', which='major', labelsize=self.xlabelSz.get())
                self.ax2.tick_params(axis='y', which='major', labelsize=self.ylabelSz.get())

                self.fig2.savefig(save_filename, dpi=self.dpi_value.get()*2)

        def saved():
            # if self.latex.get(): savefig_latex()
            # else: self.fig.savefig(save_filename)

            self.fig.savefig(save_filename)
            time.sleep(0.01)
            if askokcancel('Open savedfile?', f'File: {save_fname}\nsaved in directory: {self.location}'):
                print("Opening file: ", save_filename)
                # os.system(f"{save_filename}")
        
        try:
            print(f"Figure saving in {self.location}")
            if isfile(save_filename):
                if askokcancel('Overwrite?', f'File: {save_fname} already present. \nDo you want to Overwrite the file?'):
                    saved()
            else: saved()
            print(f'Filename saved: {save_fname}\nLocation: {self.location}\n')
    
        except: showerror("Error", traceback.format_exc(5))
