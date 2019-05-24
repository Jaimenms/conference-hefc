__doc__="""
DaetTools model that describes the behavior of a condenser.
"""


from daetools.pyDAE import *
from daetools_extended.daemodel_extended import daeModelExtended

from pyUnits import m, kg, s, K, Pa, mol, J, W, rad

from water_at_saturation_properties import saturation_temperature, vapour_density, vapour_total_compressibility


class Shell(daeModelExtended):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):

        daeModelExtended.__init__(self, Name, Parent=Parent, Description=Description, data=data, node_tree=node_tree)

        # Domains
        self.define_domains()

        # Defining Constants
        self.define_constants()

        # Defining Parameters
        self.define_parameters()

        # Defining Variables
        self.define_variables()

    def define_domains(self):
        pass

    def define_constants(self):
        pass

    def define_parameters(self):

        self.Vshell = daeParameter("Vshell", m**3, self, "Shell Volume")
        self.Pshell0 = daeParameter("Pshell0", Pa, self, "Shell Initial Pressure")
        self.PshellSP = daeParameter("PshellSP", Pa, self, "Shell Setpoint Pressure")
        self.PshellH = daeParameter("PshellH", Pa, self, "Shell High Pressure")


    def define_variables(self):

        pressure_t = daeVariableType("pressure_t", (Pa ** (1)), 0.1e+5, 50.0e+5, 1.0e+5, 1e-05, eValueGT)
        self.Pshell = daeVariable("Pshell", pressure_t, self)
        self.Pshell.Description = "Shell Pressure"

        temperature_t = daeVariableType("temperature_t", (K ** (1)), 0, 400.0, 300, 0.01, eValueGT)
        self.Tshell = daeVariable("Tshell", temperature_t, self)
        self.Tshell.Description = "Shell Temperature"

        mass_flowrate_t = daeVariableType("mass_flowrate_t", (kg ** (1)) * (s ** (-1)), 0., 200.0, 1.0, 1e-05,
                                          eValueGT)
        self.wVin = daeVariable("wVin", mass_flowrate_t, self)
        self.wVin.Description = "Vapour Mass Flowrate inlet"

        mass_flowrate_t = daeVariableType("mass_flowrate_t", (kg ** (1)) * (s ** (-1)), 0., 200.0, 1.0, 1e-05,
                                          eValueGT)
        self.wVout = daeVariable("wVout", mass_flowrate_t, self)
        self.wVout.Description = "Vapour Mass Flowrate outlet"

        mass_flowrate_t = daeVariableType("mass_flowrate_t", (kg ** (1)) * (s ** (-1)), 0., 200.0, 1.0, 1e-05,
                                          eValueGT)
        self.wLout = daeVariable("wLout", mass_flowrate_t, self)
        self.wLout.Description = "Condensate Mass Flowrate"


    def eq_shell_relief(self):

        self.stnRegulator = self.STN("Regulator")

        self.STATE("Closed")

        eq = self.CreateEquation("ReliefSystemClosed", "ReliefSystemClosed")
        wVout = self.wVout()
        eq.Residual =  wVout

        self.ON_CONDITION(self.Pshell() > self.PshellH(), switchToStates     = [ ('Regulator', 'Open') ],
                                                      setVariableValues  = [],
                                                      triggerEvents      = [],
                                                      userDefinedActions = [] )

        self.STATE("Open")

        eq = self.CreateEquation("ShellPressureRelief", "ShellPressureRelief")
        wVout = self.wVout()
        wVin = self.wVin()
        wLout = self.wLout()
        eq.Residual = wVout - (wVin - wLout)

        self.ON_CONDITION(self.Pshell() < self.PshellSP(), switchToStates     = [ ('Regulator', 'Closed') ],
                                                      setVariableValues  = [],
                                                      triggerEvents      = [],
                                                      userDefinedActions = [] )

        self.END_STN()


    def eq_shell_pressure(self):

        self.IF(Time() == Constant(0*s), eventTolerance=1E-5)

        eq = self.CreateEquation("ShellPressureStartup", "ShellPressureStartup")
        Pshell = self.Pshell()
        Pshell0 = self.Pshell0()
        eq.Residual =  Pshell - Pshell0


        self.ELSE()

        eq = self.CreateEquation("ShellPressure", "ShellPressure")
        Pshell = self.Pshell()
        wVin = self.wVin()
        wVout = self.wVout()
        wLout = self.wLout()
        Vshell = self.Vshell()
        Past = Pshell / Constant(1 * Pa)
        drhodPshell = vapour_total_compressibility(Past) * Constant(1 * kg * (m**-3) * (Pa**-1) )
        eq.Residual =  self.dt_day(Pshell) - (wVin - wVout - wLout) / (Vshell * drhodPshell)

        self.END_IF()


    def eq_shell_temperature(self):

        eq = self.CreateEquation("ShellTemperature", "ShellTemperature")
        Pshell = self.Pshell()
        Tshell = self.Tshell()
        Past = Pshell / Constant(1 * Pa)
        eq.Residual = Tshell - saturation_temperature(Past, simplified=True) * Constant(1 * K)


    def DeclareEquations(self):

        self.eq_shell_temperature()
        self.eq_shell_pressure()
        self.eq_shell_relief()
