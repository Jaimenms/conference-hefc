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

        self.A = daeParameter("A", Pa/((kg/s)**2), self, "Pump coefficient A")
        self.B = daeParameter("B", Pa/(kg/s), self, "Pump coefficient B")
        self.C = daeParameter("C", Pa, self, "Pump coefficient C")


    def eq_momentum_balance(self):
        """
        This method writes the pump curve
        :return:
        """

        # Instantiate equation
        eq = self.CreateEquation("pump_equation")
        eq.Residual = self.P() - self.A() * self.w() ** 2 - self.B() * self.w() - self.C()


    def DeclareEquations(self):
        """
        This Method is called by the DaeTools. Here is where all the equations are defined
        :return:
        """

        Source.DeclareEquations(self)
