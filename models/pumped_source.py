__doc__="""
DaetTools model that describes the behavior of a water source node without dynamics effects. It has tree state variables:

* P : pressure in Pa
* T : temperature in K
* w : inlet nodal mass flowrate in kg/s

"""

from daetools.pyDAE import *
from pyUnits import m, kg, s, K, Pa, J, W, rad

try:
    from models.source import Source
except:
    from .source import Source

from water_properties import heat_capacity


class PumpedSource(Source):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):
        """
        Model for the source
        :param Name: name of the model
        :param Parent: parent model
        :param Description: description of the model
        :param data: parameters and other required data
        """

        # Instantiate the Node
        Source.__init__(self, Name, Parent=Parent, Description=Description, data=data, node_tree=node_tree)


    def define_parameters(self):

        Source.define_parameters(self)

        self.a = daeParameter("a", Pa/(kg/s), self, "Pump a coefficient")
        self.P0 = daeParameter("P0", Pa, self, "Pump pressure at reference")
        self.w0 = daeParameter("w0", kg/s, self, "Pump flowrate at reference")


    def eq_pump(self):
        """
        This method writes the pump curve
        :return:
        """

        # Instantiate equation
        eq = self.CreateEquation("pump_equation")
        eq.Residual = self.P() - self.a() * self.w() - (self.P0() - self.a() * self.w0())


    def DeclareEquations(self):
        """
        This Method is called by the DaeTools. Here is where all the equations are defined
        :return:
        """

        Source.DeclareEquations(self)
        self.eq_pump()