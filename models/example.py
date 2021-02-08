# Import modules
import json
from daetools.pyDAE import *
from daetools.pyDAE.data_reporters import daeJSONFileDataReporter
from daetools_extended.daesimulation_extended import daeSimulationExtended

class myModel(daeModel):
    def __init__(self, name, Parent = None, Description = ""):
        daeModel.__init__(self, name, Parent, Description)

        self.data = Parent.get_data(name)

        # Declaration/instantiation of domains, parameters, variables, ports, etc:
        self.m     = daeParameter("m",       kg,           self, "Mass of the copper plate")
        self.cp    = daeParameter("c_p",     J/(kg*K),     self, "Specific heat capacity of the plate")
        self.alpha = daeParameter("&alpha;", W/((m**2)*K), self, "Heat transfer coefficient")
        self.A     = daeParameter("A",       m**2,         self, "Area of the plate")
        self.Tsurr = daeParameter("T_surr",  K,            self, "Temperature of the surroundings")

        self.Qin   = daeVariable("Q_in",  power_t,       self, "Power of the heater")
        self.T     = daeVariable("T",     temperature_t, self, "Temperature of the plate")

    def DeclareEquations(self):
        daeModel.DeclareEquations(self)
        # Specification of equations and state transitions:
        eq = self.CreateEquation("HeatBalance", "Integral heat balance equation")
        eq.Residual = self.m() * self.cp() * self.T.dt() - self.Qin() + self.alpha() * self.A() * (self.T() - self.Tsurr())


class mySimulation(daeSimulationExtended):
    def __init__(self):
        daeSimulationExtended.__init__(self)

        # Set the model to simulate:
        self.m = myModel("myModel")

    def SetUpParametersAndDomains(self):
        # Set the parameters values:
        self.m.cp.SetValue(385 * J/(kg*K))
        self.m.m.SetValue(1 * kg)
        self.m.m.SetValue(1)
        self.m.alpha.SetValue(200 * W/((m**2)*K))
        self.m.A.SetValue(0.1 * m**2)
        self.m.Tsurr.SetValue(283 * K)

    def SetUpVariables(self):
        # Set the degrees of freedom, initial conditions, initial guesses, etc.:
        self.m.Qin.AssignValue(1500 * W)
        self.m.T.SetInitialCondition(283 * K)


if __name__ == "__main__":

    filename = "example.json"

    dr = daeJSONFileDataReporter()
    dr.Connect(filename, "tutorial1")

    simulation = mySimulation()

    daeActivity.simulate(simulation, reportingInterval=5, timeHorizon=500, datareporter=dr)

    with open(filename) as f:
        data = json.load(f)

    print(data)
