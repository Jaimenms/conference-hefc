__doc__="""
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""

try:
    from models.tube_arrange import TubeArrange
    from models.fixed_external_temperature import FixedExternalTemperature
except:
    from .tube_arrange import TubeArrange
    from .fixed_external_temperature import FixedExternalTemperature


class FixedExternalTemperatureTubeArrange(FixedExternalTemperature, TubeArrange):

    def __init__(self, Name, Parent=None, Description=""):
        TubeArrange.__init__(self, Name, Parent=Parent, Description=Description)

    def define_parameters(self):
        TubeArrange.define_parameters(self)
        FixedExternalTemperature.define_parameters(self)

    def define_variables(self):
        TubeArrange.define_variables(self)
        FixedExternalTemperature.define_variables(self)

    def DeclareEquations(self):
        TubeArrange.DeclareEquations(self)
        FixedExternalTemperature.DeclareEquations(self)
