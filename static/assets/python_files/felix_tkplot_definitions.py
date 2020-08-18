from pathlib import Path as pt
import matplotlib.pyplot as plt
import numpy as np


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


def felix_plot(filename, ax, lg, normMethod="IntensityPerPhoton", sameColor=True, color=0,):
    
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


    
    def __init__(self, fig, canvas, ax_theory, ax_exp, txt_array=[], txt_value = ["1", "2", "3"]):

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
        self.canvas = canvas
        
        self.canvas.mpl_connect('button_release_event', self.onclick)
        self.canvas.mpl_connect('key_press_event', self.keypress)
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

        self.canvas.draw()
        
    def remove_annotation(self, ind):
        txt_widget = self.txt_array[ind]
        txt_widget["txt"].remove()
        deleted_value = txt_widget["value"]
        self.txt_array = np.delete(self.txt_array, ind)
        self.txt_value = np.insert(self.txt_value, 0, deleted_value)
        
    def figtext(self, title):
        # self.fig.text(0.5, 0.01, title, wrap=True, horizontalalignment='center', fontsize=12)
        self.ax_exp.set_title(title)
        self.canvas.draw()
    
    def onclick(self, event):
        
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

            self.canvas.draw()