__doc__="""
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""

try:
    from models.pipe import Pipe
    from models.carbfilm import Carbfilm
except:
    from .pipe import Pipe
    from .carbfilm import Carbfilm

class CarbfilmedPipe(Carbfilm, Pipe):

    def __init__(self, Name, Parent=None, Description=""):

        Pipe.__init__(self, Name, Parent=Parent, Description=Description)

    def define_constants(self):
        Pipe.define_constants(self)
        Carbfilm.define_constants(self)

    def define_variables(self):
        Pipe.define_variables(self)
        Carbfilm.define_variables(self)

    def define_parameters(self):
        Pipe.define_parameters(self)
        Carbfilm.define_parameters(self)

    def DeclareEquations(self):
        Pipe.DeclareEquations(self)
        Carbfilm.DeclareEquations(self)