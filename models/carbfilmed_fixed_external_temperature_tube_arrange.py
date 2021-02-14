__doc__ = """
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""

from daetools.pyDAE import *
from pyUnits import m, kg, s, K, Pa, J, W, rad

try:
    from models.fixed_external_temperature_tube_arrange import FixedExternalTemperatureTubeArrange
    from models.carbfilm import Carbfilm
except:
    from .fixed_external_temperature_tube_arrange import FixedExternalTemperatureTubeArrange
    from .carbfilm import Carbfilm


class CarbfilmedFixedExternalTemperatureTubeArrange(Carbfilm, FixedExternalTemperatureTubeArrange):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):
        FixedExternalTemperatureTubeArrange.__init__(self, Name, Parent=Parent, Description=Description)

    def define_constants(self):
        FixedExternalTemperatureTubeArrange.define_constants(self)
        Carbfilm.define_constants(self)

    def define_parameters(self):
        FixedExternalTemperatureTubeArrange.define_parameters(self)
        Carbfilm.define_parameters(self)

    def define_variables(self):
        FixedExternalTemperatureTubeArrange.define_variables(self)
        Carbfilm.define_variables(self)

    def DeclareEquations(self):
        FixedExternalTemperatureTubeArrange.DeclareEquations(self)
        Carbfilm.DeclareEquations(self)
