__doc__="""
DaetTools model that describes the behavior of a water source node without dynamics effects. It has tree state variables:

* P : pressure in Pa
* T : temperature in K
* w : inlet nodal mass flowrate in kg/s

"""


from daetools.pyDAE import *
from daetools_extended.daemodel_extended import daeModelExtended

from pyUnits import m, kg, s, K, Pa, mol, J, W, rad


from water_properties import heat_capacity
from scipy.constants import pi


class RiverSource(daeModelExtended):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):
        """
        Base Model for the nodal elements
        :param Name: name of the model
        :param Parent: parent model
        :param Description: description of the model
        :param data: parameters and other required data
        """

        daeModelExtended.__init__(self, Name, Parent, Description, data=data, node_tree=node_tree)

        self.pi = Constant( pi )

        # Getting variables
        self.define_variables()

        # Getting parameters
        self.define_parameters()


    def define_variables(self):
        """
        Define variables.
        :return:
        """

        pressure_t = daeVariableType("pressure_t", (Pa ** (1)), 0.1e+5, 50.0e+5, 1.0e+5, 1e-05, eValueGT)
        self.P = daeVariable("P", pressure_t, self)
        self.P.Description = "Nodal Pressure"

        temperature_t = daeVariableType("temperature_t", (K ** (1)), 0, 400.0, 300, 0.01, eValueGT)
        self.T = daeVariable("T", temperature_t, self)
        self.T.Description = "Nodal Temperature"

        mass_flowrate_t = daeVariableType("nodal_mass_flowrate_t", (kg ** (1)) * (s ** (-1)), 0., 200.0, 1.0, 1e-05, eValueGT)
        self.w = daeVariable("w", mass_flowrate_t, self)
        self.w.Description = "Nodal Mass Flowrate"

        self.Text = daeVariable("Text", temperature_t, self)
        self.Text.Description = "External temperature"


    def define_parameters(self):
        """
        Define Parameters
        :return:
        """

        self.x = daeParameter("x", m, self, "x Coordinate")
        self.y = daeParameter("y", m, self, "x Coordinate")
        self.z = daeParameter("z", m, self, "x Coordinate")
        self.Pext = daeParameter("Pext", (Pa), self, "Pressure of external source")
        self.Text0 = daeParameter("Text0", K, self, "Text0")
        self.A = daeParameter("A", Pa/((kg/s)**2), self, "Pump coefficient A")
        self.B = daeParameter("B", Pa/(kg/s), self, "Pump coefficient B")
        self.C = daeParameter("C", Pa, self, "Pump coefficient C")

        self.alpha1 = daeParameter("alpha1", K, self, "alpha1")
        self.alpha2 = daeParameter("alpha2", K, self, "alpha2")
        self.tau = daeParameter("tau", s, self, "Days to minimum temperature")


    def eq_mass_balance(self):
        """
        This method writes the mass balance to the correspondent node instance
        :return:
        """

        # Starting with the external mass flow rate
        residual_aux = self.w()


        # Mass to the node inlet
        for edge_name in self.get_inlet():
            residual_aux += self.Parent.submodels[edge_name].kub()

        # Mass to the node outlet
        for edge_name in self.get_outlet():
            residual_aux -= self.Parent.submodels[edge_name].klb()

        # Instantiate equation NMB
        eq = self.CreateEquation("NMB_nodal_mass_balance")
        eq.Residual = residual_aux


    def eq_energy_balance(self):
        """
        This method writes the mass balance to the correspondent node instance
        :return:
        """

        # Starting with the external mass flow rate
        cp_ext = heat_capacity(self.Text()/Constant(1*K), self.data['parameters']['Pext'], simplified=True)
        residual_aux = self.w() * self.Text() * cp_ext * Constant(1 * (J ** (1)) * (K ** (-1)) * (kg ** (-1)))

        for edge_name in self.get_inlet():
            residual_aux += self.Parent.submodels[edge_name].Hub()

        # Mass to the node outlet
        for edge_name in self.get_outlet():
            residual_aux -= self.Parent.submodels[edge_name].Hlb()

        eq = self.CreateEquation("NEB_source_energy_balance_2")
        eq.Residual = residual_aux


    def eq_pump(self):
        """
        This method writes the pump curve
        :return:
        """

        # Instantiate equation
        eq = self.CreateEquation("pump_equation")
        eq.Residual = self.P() - self.A() * self.w() ** 2 - self.B() * self.w() - self.C()


    def eq_river_temperature(self):

        self.stnRiverTemperature = self.STN("RiverTemperature")

        self.STATE("Fixed")

        eq = self.CreateEquation("river_temperature")
        eq.Residual = self.Text() - self.Text0()

        self.STATE("PreVariable")

        eq = self.CreateEquation("river_temperature")
        eq.Residual = self.Text() - self.Text0()

        self.ON_CONDITION(Time() > Constant(0*s), switchToStates     = [ ('RiverTemperature', 'Variable') ],
                                                      setVariableValues  = [],
                                                      triggerEvents      = [],
                                                      userDefinedActions = [] )


        self.STATE("Variable")

        eq = self.CreateEquation("river_temperature")
        eq.Residual = self.Text() - (self.alpha1() + self.alpha2() * Sin(2*self.pi/Constant(365*s) * (Time() + self.tau())))

        self.END_STN()


    def DeclareEquations(self):
        """
        This Methos is called by the DaeTools. Here is where all the equations are defined
        :return:
        """

        daeModelExtended.DeclareEquations(self)
        self.eq_mass_balance()
        self.eq_energy_balance()
        self.eq_pump()
        self.eq_river_temperature()