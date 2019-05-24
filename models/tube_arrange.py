__doc__ = """
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""

from daetools.pyDAE import *

# These are methods and constants imported from daeTools C++ code
daeVariable = daeVariable
daeVariableType = daeVariableType
daeDomain = daeDomain
Constant = Constant
daeParameter = daeParameter
eClosedClosed = eClosedClosed
eOpenClosed = eOpenClosed
unit = unit
Abs = Abs
Log = Log
Log10 = Log10
Exp = Exp
Sin = Sin
Sum = Sum
eUpperBound = eUpperBound
eLowerBound = eLowerBound
eCFDM = eCFDM
dt = dt
d = d
from pyUnits import m, kg, s, K, Pa, J, W, rad

try:
    from models.pipe import Pipe
except:
    from .pipe import Pipe

from water_properties import density, viscosity, conductivity, heat_capacity


class TubeArrange(Pipe):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):
        Pipe.__init__(self, Name, Parent=Parent, Description=Description, data=data, node_tree=node_tree)

    def define_domains(self):
        Pipe.define_domains(self)

        self.y = daeDomain("y", self, unit(), "Y tube position")

    def DeclareEquations(self):
        Pipe.DeclareEquations(self)
