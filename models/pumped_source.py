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



class PumpedSource(Source):

    def __init__(self, Name, Parent=None, Description=""):
        """
        Model for the source
        :param Name: name of the model
        :param Parent: parent model
        :param Description: description of the model
        :param data: parameters and other required data
        """

        # Instantiate the Node
        Source.__init__(self, Name, Parent=Parent, Description=Description)


    def define_parameters(self):

        Source.define_parameters(self)

        self.a0 = daeParameter("a0", Pa, self, "Pump a coefficient 0th order")
        self.a1 = daeParameter("a1", Pa/(kg/s), self, "Pump a coefficient 1st order")
        self.a2 = daeParameter("a2", Pa/(kg**2/s**2), self, "Pump a coefficient 2nd order")


    def eq_pump_curve(self):
        """
        This method writes the pump curve
        :return:
        """
        eq = self.CreateEquation("pump_equation")
        eq.Residual = self.P() - self.a0() - self.a1() * self.w() - self.a2() * self.w() ** 2

    def DeclareEquations(self):
        """
        This Method is called by the DaeTools. Here is where all the equations are defined
        :return:
        """

        self.eq_pump_curve()
        Source.DeclareEquations(self)
