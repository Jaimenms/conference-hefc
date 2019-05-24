__doc__ = """
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""

from daetools.pyDAE import *
from pyUnits import m, kg, s, K, Pa, J, W, rad

try:
    from models.fixed_external_convection_pipe import FixedExternalConvectionPipe
    from models.carbfilm import Carbfilm
except:
    from .fixed_external_convection_pipe import FixedExternalConvectionPipe
    from .carbfilm import Carbfilm


class CarbfilmedFixedExternalConvectionPipe(Carbfilm, FixedExternalConvectionPipe):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):
        FixedExternalConvectionPipe.__init__(self, Name, Parent=Parent, Description=Description, data=data,
                                             node_tree=node_tree)


    def define_constants(self):
        FixedExternalConvectionPipe.define_constants(self)
        Carbfilm.define_constants(self)

    def define_parameters(self):
        FixedExternalConvectionPipe.define_parameters(self)
        Carbfilm.define_parameters(self)


    def define_variables(self):
        FixedExternalConvectionPipe.define_variables(self)

        Carbfilm.define_variables(self)


    def define_parameters(self):
        FixedExternalConvectionPipe.define_parameters(self)

        Carbfilm.define_parameters(self)


    def DeclareEquations(self):
        FixedExternalConvectionPipe.DeclareEquations(self)
        Carbfilm.DeclareEquations(self)