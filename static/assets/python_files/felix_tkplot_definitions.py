from pathlib import Path as pt
# from ipywidgets import widgets, interact_manual, Layout
# from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np

class createWidgets:
    
    def __init__(self, filetype, multiselect=True, fig=None, save_options=True, update_label="update location"):
        
        if fig != None: self.fig = fig
        self.filetype = filetype
        
        self.location = widgets.Text(r"", description=f"{filetype} location", layout=Layout(width='70%'), style = {'description_width': 'initial'})

        if multiselect:
            
            self.files= widgets.SelectMultiple(description=f'{filetype} files',
                layout=Layout(width='70%'), style = {'description_width': 'initial'})
        
        else:
            self.files= widgets.Select(description=f'{filetype} files',
                layout=Layout(width='70%'), style = {'description_width': 'initial'})
        
        self.update_files_button = widgets.Button(description=update_label,button_style="success", layout=Layout(width='20%'), style = {'description_width': 'initial'})
        self.update_files_button.on_click(self.get_files)

        self.output = widgets.Output()
        
        if save_options:
            
            self.savefilename = widgets.Text("", description="savefilename")
            self.savedpi = widgets.IntText(140, min=70, step=2, description="savedpi")

            self.savebutton = widgets.Button(description="Save",button_style="success")
            self.savebutton.on_click(self.savefig)

            self.closebutton =  widgets.Button(description="Clear",button_style="danger")
            self.closebutton.on_click(self.clearLog)

    def get_files(self, e):
        with self.output:
            if len(self.location.value)<1: return print("Location not set")
            print(f"Getting {self.filetype} from {self.location.value}")
            filelist = [i.name for i in pt(f"{self.location.value}").glob(f"*.{self.filetype}")]
            self.files.options = filelist

    def savefig(self, e):
        with self.output:
            try:
                if self.fig != None:
                    print(f"Saving file: {self.savefilename.value}")
                    if self.savefilename.value == "": self.savefilename.value = "_0"
                    savefile = pt(self.location.value) / f"{self.savefilename.value}"
                    self.fig.savefig(f"{savefile}.pdf", dpi=self.savedpi.value)
                    self.fig.savefig(f"{savefile}.png", dpi=self.savedpi.value)
                    print(f"Saved as {savefile}.pdf")

                    #plt.close()
            except Exception as error:
                print(f"Error occured while saving: {error}")

            return "File is already opened so cannot save now"

    def clearLog(self, e):
        return self.output.clear_output()
    
class figure_widgets:
    
    def __init__(self):
        
        self.figcaption = self.get_text("", "figcaption")
        
        self.titles = self.get_text("", "Enter two titles")
        self.plot_ratio = self.get_text("1", "Plot ratio")
        
        self.legend_labels = self.get_text("", "Legend labels")
        self.legend_labels1 = self.get_text("", "Legend labels1")
        self.legend_labels2 = self.get_text("", "Legend labels2")
        
        self.normMethod = self.get_normMethod()
        self.normMethod1 = self.get_normMethod()
        self.normMethod2 = self.get_normMethod()
        

        self.dpi = self.get_boundInt(100, "dpi", _min=70, step=2)
        self.majorTickInterval = self.get_boundInt(100, "Tick Interval", _min=1, step=10)
        self.figwidth = self.get_boundInt(7, "figwidth")
        self.figheight = self.get_boundInt(7, "figheight")
        self.Nplots = self.get_boundInt(1, "# Plots")
        
        self.gridalpha = self.get_boundFloat(0, "gridAlpha", 0, 1, 0.1)
        self.freqScale = self.get_boundFloat(1, "freqScale", 0, 1, 0.01)
        self.theorysigma = self.get_boundFloat(5, "theorysigma")
        
        self.hspace = self.get_boundFloat(0.05, "hspace", 0, 1, 0.01)
        self.wspace = self.get_boundFloat(0.05, "wspace", 0, 1, 0.01)
        
    def get_normMethod(self): return widgets.Dropdown(options=["addedFile", "Relative", "IntensityPerPhoton", "Log"], description="normMethod")
    def get_textarea(self, value="", description="title"): return widgets.Textarea(value, description=description, layout=Layout(width='70%', height="50px"), style = {'description_width': 'initial'})
    def get_text(self, value="", description=""): return widgets.Text(value, description=description, layout=Layout(width='70%', height="50px"), style = {'description_width': 'initial'})
    def get_boundInt(self, value=1, description="", _min=1, _max=20, step=1): return widgets.IntText(value, min=_min, max=_max, step=step, description=description)
    def get_boundFloat(self, value=1, description="", _min=1, _max=20, step=1): return widgets.FloatText(value, min=_min, max=_max, step=step, description=description)

def generateNGaussian(N):

    gaussfn = lambda n: f"A{n}*(np.exp((-1.0/2.0)*(((x-cen{n})/sigma{n})**2)))+"
    _gfn, _args = "", "x, "
    for i in range(int(N)): 
        _gfn += gaussfn(i)
        _args += f"cen{i}, A{i}, sigma{i}, "
    exec(f"gfn_ = lambda {_args.strip()[:-1]}: {_gfn.strip()[:-1]}")
    
    return locals()["gfn_"]

def computeNGaussian(wn, inten, sigma=5):
    
    _args = {}
    N = len(wn)
    gfn = generateNGaussian(N)
    
    i = 0
    for x, y in zip(wn, inten):
        _args[f"cen{i}"] = x
        _args[f"A{i}"] = y
        _args[f"sigma{i}"] = sigma

        i += 1
    
    full_wn = np.linspace(wn.min()-100, wn.max()+100, 5000)
    
    full_inten = gfn(full_wn, **_args)

    return full_wn, full_inten

def read_dat_file(filename, normMethod):
    
    read_data = np.genfromtxt(filename).T
    xs = read_data[0]
    
    if normMethod == "Log": ys = read_data[1]
    
    elif normMethod == "Relative": ys = read_data[2]
    else: ys = read_data[3]
        
    return xs, ys


def theoryplot(theoryfile, ax, freqScale=1, colorIndex=1, theorysigma=5):

    try:
    
        # Getting legend info from theoryfile
        with open(theoryfile, "r") as f:
            readfile = f.readlines()
        legendName = readfile[1].split(" ")[-1].split("\n")[0]
    except: legendName = ""

    # Reading theoryfile
    freq_t, inten_t = np.genfromtxt(theoryfile).T[:2]
    
    if type(freq_t) != np.ndarray:
        freq_t = np.array([freq_t])
        inten_t = np.array([inten_t])
  
    # Frequnecy scaling
    freq_t *= freqScale

    # theory plotting
    freq_tsim, inten_tsim = computeNGaussian(freq_t, inten_t, theorysigma)
    theory_lines = ax.plot(freq_tsim, inten_tsim, f"C{colorIndex}", label=legendName)
    
    return ax


def felix_plot(filename, ax, lg, normMethod="IntensityPerPhoton", color=0, sameColor=True):
    
    for i, f in enumerate(filename):
        
        if not sameColor: color += i
            
        if normMethod == "addedFile":
            data = np.genfromtxt(f).T
            wn = data[0]
            inten = data[2]*1e3
            ax.fill_between(wn, inten, color=f"C{color}", step="pre", alpha=0.4)
        else:
            freq_exp, inten_exp = read_dat_file(f, normMethod)
            ax.fill_between(freq_exp, inten_exp, color=f"C{color}",step="pre", alpha=0.4)
            
        fullfit_file = f.parent / f"{f.stem}_{normMethod}.fullfit"
        freq_sim, inten_sim = np.genfromtxt(fullfit_file).T
        try:
            ax.plot(freq_sim, inten_sim, f"C{color}", zorder=2, label=lg[i])
        except:
            ax.plot(freq_sim, inten_sim, f"C{color}", zorder=2)
        
    return ax

def fitted_vlines(ax, filename, loc, normMethod, color):
    filename = (f"{filename.stem}_Log.expfit", f"{filename.stem}_addedFile.expfit")[normMethod=="addedFile"]
    expfit = loc / filename

    data = np.genfromtxt(expfit).T
    y0, y1 = ax.get_ylim()
    
    args = dict(color=f"C{color}", alpha=0.5, ls="--")
    if type(data[0]) is np.ndarray:
        for f in data[0]: 
            ax.vlines(f, y0, y1 , **args)
    else: 
        ax.vlines(data[0], y0, y1, **args)

    return ax



def find_closest_value(arr, val):
    abs_val = np.abs(arr-val)
    min_val_ind = abs_val.argmin()
    closest_element = arr[min_val_ind]
    return closest_element

def find_closest_ind(arr, val):
    
    abs_val = np.abs(arr-val)
    min_val_ind = abs_val.argmin()
    return min_val_ind

class Marker:
    
    def __init__(self, fig, ax_theory, ax_exp, txt_array=[], txt_value = ["1", "2", "3"]):

        self.txt_counter = 0
        
        self.txt_value = txt_value
        self.txt_value_original = txt_value
        self.txt_array = txt_array
        
        self.fig = fig
        self.ax_theory =  ax_theory
        self.ax_exp =  ax_exp
        
        self.start = False
        
        self.theory = True
        self.ax = ax_theory
        
        
        self.fig.canvas.mpl_connect('button_release_event', self.onclick)
        self.fig.canvas.mpl_connect('key_press_event', self.keypress)
        
        self.output = widgets.Output()
        
        self.color_ = True
        self.color="C1"
        
        
    def keypress(self, event):
        if event.key == "w":
            print("Key Pressed")
            self.start = not self.start
            
            if self.start: self.figtext("Click to add/remove annotation")
            else: self.figtext("")
    
        if event.key == "t":
            self.theory = not self.theory
            
            if self.theory: self.figtext("Theory marker") 
            else: self.figtext("Experiment marker")
                
            self.ax = (self.ax_exp, self.ax_theory)[self.theory]
            
        if event.key == "c":
            
            self.color_ = not self.color_
            
            if self.color_: self.figtext("color1") 
            else: self.figtext("color2") 
                
            self.color = ("C2", "C1")[self.color_]
            
        if event.key == "z":
            
            if len(self.txt_array) == 0: return
            else: self.remove_annotation(-1)
    
    def remove_annotation(self, ind):
        txt_widget = self.txt_array[ind]
        txt_widget["txt"].remove()
        deleted_value = txt_widget["value"]
        self.txt_array = np.delete(self.txt_array, ind)
        self.txt_value = np.insert(self.txt_value, 0, deleted_value)
        
    def figtext(self, title):
        #self.figtext = self.fig.text(0.5, 0.01, figcaption, wrap=True, horizontalalignment='center', fontsize=12)
        return self.ax_exp.set_title(title)
    
    def onclick(self, event):
        
        with self.output:
            if self.start:
                
                xdata = event.xdata
                
                    
                if event.button==1:
                    if len(self.txt_value) > 0:
                        value = self.txt_value[0]
                        
                        txt_widget = self.ax.annotate(value, (event.xdata, event.ydata), color=self.color, fontsize=12)
                        txt_widget.draggable()
                        
                        txt = {"txt":txt_widget, "data":xdata, "value": value}
                        self.txt_array = np.append(self.txt_array, txt)

                        self.txt_value = np.delete(self.txt_value, 0)

                else:
                    
                    if len(self.txt_array) >0:

                        arr = list(map(lambda d: d["data"], self.txt_array))
                        ind = find_closest_ind(arr, xdata)
                        self.remove_annotation(ind)
                    else:
                        self.txt_value = self.txt_value_original
                        return

                self.fig.canvas.draw()