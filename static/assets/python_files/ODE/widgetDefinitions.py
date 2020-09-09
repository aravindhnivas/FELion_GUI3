from pathlib import Path as pt
from ipywidgets import widgets, interact_manual, Layout
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np

class createWidgets:
    
    def __init__(self, filetype, locationValue="", multiselect=True, fig=None, save_options=True, update_label="update location"):
        
        if fig != None: self.fig = fig
        self.filetype = filetype
        
        self.location = widgets.Text(locationValue, description=f"{filetype} location", layout=Layout(width='70%'), style = {'description_width': 'initial'})

        if multiselect:
            
            self.files= widgets.SelectMultiple(description=f'{filetype} files',
                layout=Layout(width='70%'), style = {'description_width': 'initial'})
        
        else:
            self.files= widgets.Select(description=f'{filetype} files',
                layout=Layout(width='70%'), style = {'description_width': 'initial'})
        
        self.update_files_button = widgets.Button(description=update_label,button_style="success", layout=Layout(width='20%'), style = {'description_width': 'initial'})
        
        self.update_files_button.on_click(self.get_files)
        
        self.output = widgets.Output()
        self.get_files(None)
        
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