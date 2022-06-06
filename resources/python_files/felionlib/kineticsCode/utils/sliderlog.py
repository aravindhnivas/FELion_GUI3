from matplotlib.widgets import Slider
# import matplotlib
# matplotlib.use(backend="TkAgg")

class Sliderlog(Slider):

    """Logarithmic slider.
    Takes in every method and function of the matplotlib's slider.
    Set slider to *val* visually so the slider still is lineat but display 10**val next to the slider.
    Return 10**val to the update function (func)"""

    def set_val(self, val):

        xy = self.poly.xy
        if self.orientation == "vertical":
            xy[1] = 0, val
            xy[2] = 1, val
            self._handle.set_ydata([val])
        else:
            xy[2] = val, 1
            xy[3] = val, 0
            self._handle.set_xdata([val])
        self.poly.xy = xy
        self.valtext.set_text(self.valfmt % 10**val)  # Modified to display 10**val instead of val
        if self.drawon:
            self.ax.figure.canvas.draw_idle()
        self.val = val
        
        if self.eventson:
            self._observers.process('changed', val)
    
    @property
    def value(self):
        return 10**self.val
    