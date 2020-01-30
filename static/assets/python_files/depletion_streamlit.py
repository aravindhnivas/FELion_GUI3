# Built-In Modules
import os, sys
from pathlib import Path as pt

# DATA Analysis
import numpy as np
from scipy.optimize import curve_fit
from uncertainties import ufloat as uf
from uncertainties import unumpy as unp

from plotly.subplots import make_subplots
import plotly.graph_objects as go


try: import streamlit as st
except:

    filename = pt(__file__)
    pipFolder = filename.parent.parent / "pipPackages"
    if pipFolder.exists():
        packageName = "streamlit-0.51.0-py2.py3-none-any.whl"
        package = os.path.join(pipFolder, packageName)
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        import streamlit as st

from timescan import timescanplot
from FELion_constants import colors

from io import StringIO
import contextlib

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

class depletionplot:

    def __init__(self, location):
        
        location = st.text_input("Current Location", location)
        self.location = pt(location)

        self.initialise()
        self.fig = make_subplots(rows=1, cols=2)

        try: 

            self.get_timescan_data()
            Koff, N = self.resOff_fit()

            Na0, Nn0, Kon = self.resOn_fit(Koff, N)
            self.make_slider(Koff, Kon, N, Na0, Nn0)

            Koff = self.koff_slider
            Kon = self.kon_slider
            N = self.n_slider
            Na0 = self.na_slider
            Nn0 = self.nn_slider

            self.runFit(Koff, Kon, N, Na0, Nn0)

            layout = go.Layout(
                xaxis={"title":self.xaxis_title},
                yaxis={"title":"Counts"},
                xaxis2={"title":self.xaxis_title},
                yaxis2={"title":"Relative depletion of active isomer"}
            )
            self.fig.update_layout(layout)
            st.plotly_chart(self.fig, height=700)
            
            pycode = st.text_area("pyCode")
            with stdoutIO() as result:
                exec(pycode)
                st.write(result.getvalue())


        except Exception as error:
            
            st.title("Choose proper ResOn and ResOff file from the sidebar")
            st.subheader("Error details")
            st.write(error)
    
    def initialise(self):
        self.method = st.sidebar.selectbox("Method", ("Power dependence", "Time dependece"))

        pwidget = st.sidebar.empty()
        scanfiles = list(self.location.glob("*.scan"))
        scanfiles = [i.name for i in scanfiles]
        if st.sidebar.button("Refresh"):
            scanfiles = list(self.location.glob("*.scan"))
            scanfiles = [i.name for i in scanfiles]
        self.resON_select = st.sidebar.selectbox("Res ON:", scanfiles)
        self.resOFF_select = st.sidebar.selectbox("Res OFF:", scanfiles)

        self.resOnFile = self.location/self.resON_select
        self.resOffFile = self.location/self.resOFF_select

        self.nshots = st.sidebar.radio("FELIX (Hz)", (10, 5))
        self.massIndex = st.sidebar.number_input("MassIndex", 0, value=1)
        self.timeStart = st.sidebar.number_input("TimeStartIndex", 0, value=1)
        
        if self.method == "Power dependence":
            powerWidget = pwidget.text_input("Power (ON, OFF)", "12, 12")

            power_values = np.asarray(powerWidget.split(","), dtype=np.float)

            self.powerOn = power_values[0]
            self.powerOff = power_values[1]
            self.power = {"resOn": power_values[0]/1000, "resOff": power_values[1]/1000} # mJ to J

            self.xaxis_title = "n*t*E (J)"
        
        else:
            self.powerOn = "-"
            self.powerOff = "-"
            self.power = {"resOn": 1, "resOff": 1}
            self.nshots = 1
            self.xaxis_title = "Time (s)"

    def make_slider(self, Koff, Kon, N, Na0, Nn0):

        self.koff_slider = st.sidebar.slider("Koff", 0.0, np.float(Koff*10), np.float(Koff))
        self.kon_slider = st.sidebar.slider("Kon", 0.0, np.float(Kon*10), np.float(Kon))
        self.n_slider = st.sidebar.slider("N", 0.0, np.float(N*10), np.float(N))
        self.na_slider = st.sidebar.slider("Na0", 0.0, np.float(Na0*10), np.float(Na0))
        self.nn_slider = st.sidebar.slider("Nn0", 0.0, np.float(Nn0*10), np.float(Nn0))
        
    def runFit(self, Koff, Kon, N, Na0, Nn0, plot=True):

        uKoff = uf(Koff, self.Koff_err)
        uN = uf(N, self.N_err)
        uNa0 = uf(Na0, self.Na0_err)
        uNn0 = uf(Nn0, self.Nn0_err)
        uKon = uf(Kon, self.Kon_err)

        lg1 = f"Kon: {uKon:.2uP}, Na: {uNa0:.2uP}, Nn: {uNn0:.2uP}"
        lg2 = f"Koff: {uKoff:.2uP}, N: {uN:.2uP}"

        self.get_depletion_fit(Koff, N, uKoff, uN, Na0, Nn0, Kon, uNa0, uNn0, uKon, plot)
        self.get_relative_abundance_fit(plot)

        self.fig.update_layout(title_text=f"ON: {self.resOnFile.stem}[{self.powerOn}mJ], OFF: {self.resOffFile.stem}[{self.powerOff}mJ];\
            A: {self.uA*100:.2uP}%; [Kon: {uKon:.2uP}, Koff: {uKoff:.2uP}]")

    def get_timescan_data(self):

        self.data1 = {"resOn":{}, "resOff": {}}
        self.time = {"resOn":[], "resOff": []}
        self.counts = {"resOn":[], "resOff": []}
        self.error = {"resOn":[], "resOff": []}

        self.ax0_plot = {}
        for index, scanfile, i in zip(["resOn", "resOff"], [self.resOnFile, self.resOffFile], [0, 2]):

            time, counts, error, self.mass, self.t_res, self.t_b0 = timescanplot(scanfile).get_data()

            time = time/1000 # ms to s

            self.time[index] = np.array(time[self.timeStart:])
            self.counts[index] = np.array(counts[self.massIndex][self.timeStart:])
            self.error[index] = np.array(error[self.massIndex][self.timeStart:])

            self.power[index] = np.array((self.power[index] * self.nshots * self.time[index]))
            # self.ax0.errorbar(self.power[index], self.counts[index], yerr=self.error[index], fmt=f"C{i}.")

            error_data = dict(type="data", array=self.error[index], visible=True)
            trace = go.Scatter(x=self.power[index], y=self.counts[index], error_y=error_data, name=index, mode="markers", marker=dict(color=f"rgb{colors[i]}"))
            self.fig.add_trace(trace, row=1, col=1)
        
    def N_OFF(self, x, K_OFF, N): return (N)*np.exp(-K_OFF*x)

    def resOff_fit(self, auto_plot=True):
        K_OFF_init = 0
        N_init = self.counts["resOff"].max()

        pop_off, popc_off = curve_fit(
            self.N_OFF, self.power["resOff"], self.counts["resOff"],
            sigma=self.error["resOff"],
            absolute_sigma=True,
            p0=[K_OFF_init, N_init],
            bounds=[(-np.inf, 0), (np.inf, N_init*2)]
        )

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
        pop_on, popc_on = curve_fit(
            self.N_ON, self.power["resOn"], self.counts["resOn"],
            sigma=self.error["resOn"],
            absolute_sigma=True,
            p0=[Na0_init, Nn0_init, K_ON_init],
            bounds=[(0, 0, -np.inf), (N , N*2, np.inf)]
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

        self.fitX = np.linspace(0, maxPower, 20)
        ufitX = unp.uarray(self.fitX, np.zeros(len(self.fitX)))

        self.fitOn = self.N_ON(self.fitX, Na0, Nn0, self.Kon)
        self.fitOff = self.N_OFF(self.fitX, Koff, N)

        self.fitOn_with_err = self.uN_ON(ufitX, uNa0, uNn0, uKoff, uKon)
        self.fitOff_with_err = self.uN_OFF(ufitX, uKoff, uN)
        
        self.fitted_counts_error = {"resOn": unp.std_devs(self.fitOn_with_err), "resOff": unp.std_devs(self.fitOff_with_err)}
        print(f"Exp counts error: {self.error}\nFitted counts error: {self.fitted_counts_error}\n")

        self.fitted_counts = {"resOn":np.array(self.fitOn), "resOff": np.array(self.fitOff)}
        print(f"Counts: {self.counts}\nFitted: {self.fitted_counts}\n")

        if plot:
            for index, fitY, i in zip(["resOn", "resOff"], [self.fitOn, self.fitOff], [0, 2]):
                trace = go.Scatter(x=self.fitX, y=fitY, mode="lines", marker=dict(color=f"rgb{colors[i]}"), showlegend=False)
                self.fig.add_trace(trace, row=1, col=1)
            lg1 = f"Kon: {uKon:.2uP}, Na: {uNa0:.2uP}, Nn: {uNn0:.2uP}"
            lg2 = f"Koff: {uKoff:.2uP}, N: {uN:.2uP}"

            st.subheader(lg1)
            st.subheader(lg2)

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
            error_data = dict(type="data", array=self.depletion_exp_err, visible=True)
            trace1 = go.Scatter(x=self.power["resOn"], y=self.depletion_exp, mode="markers", marker=dict(color=f"black"), name="Exp", error_y=error_data)
            trace2 = go.Scatter(x=self.fitX, y=self.depletion_fitted, mode="lines+markers", marker=dict(color=f"rgb{colors[0]}"), name="Fitted")
            trace3 = go.Scatter(x=self.fitX, y=self.relative_abundance, mode="lines+markers", marker=dict(color=f"rgb{colors[2]}"), name="Relative")
            self.fig.add_trace(trace1, row=1, col=2)
            self.fig.add_trace(trace2, row=1, col=2)
            self.fig.add_trace(trace3, row=1, col=2)
            st.subheader(f"Relative abundance: {self.uA*100:.3uP} %")

if __name__ == "__main__":

    args = sys.argv[1:]
    location = args[0]
    scanfiles = args[1:]

    if location == "undefined":
        st.title("Location is undefined. Please close this and browse location containing timescan files")
    
    elif len(scanfiles)<1: st.title("This location doesn't have any timescan files")
    else: 
        if st.checkbox("Graph is not properly scaled ?"): st.title("Click top right corner: Settings --> Show app in wide mode")
        depletionplot(location)