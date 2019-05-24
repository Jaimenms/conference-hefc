__doc__="""
DaetTools base node model to be extended by water sink and water source nodes:

* P : pressure in Pa
* T : temperature in K
* w : inlet nodal mass flowrate in kg/s

"""

from daetools.pyDAE import *
from daetools_extended.daemodel_extended import daeModelExtended

from pyUnits import m, kg, s, K, Pa, mol, J, W, rad


class Node(daeModelExtended):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):
        """
        Base Model for the nodal elements
        :param Name: name of the model
        :param Parent: parent model
        :param Description: description of the model
        :param data: parameters and other required data
        """

        daeModelExtended.__init__(self, Name, Parent, Description, data=data, node_tree=node_tree)

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


    def define_parameters(self):
        """
        Define Parameters
        :return:
        """

        self.x = daeParameter("x", m, self, "x Coordinate")
        self.y = daeParameter("y", m, self, "x Coordinate")
        self.z = daeParameter("z", m, self, "x Coordinate")
        self.Pext = daeParameter("Pext", (Pa), self, "Pressure of external source")
        self.Text = daeParameter("Text", K, self, "Temperature of external source")


    def DeclareEquations(self):
        """
        This Methos is called by the DaeTools. Here is where all the equations are defined
        :return:
        """

        daeModelExtended.DeclareEquations(self)




