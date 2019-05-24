__doc__="""
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""


from daetools.pyDAE import *
from pyUnits import m, kg, s, K, Pa, J, W, rad

try:
    from models.pipe import Pipe
    from models.external_film_condensation import ExternalFilmCondensation
except:
    from .pipe import Pipe
    from .external_film_condensation import ExternalFilmCondensation


class ExternalFilmCondensationPipe(ExternalFilmCondensation, Pipe):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):
        Pipe.__init__(self, Name, Parent=Parent, Description=Description, data=data, node_tree=node_tree)


    def define_parameters(self):

        Pipe.define_parameters(self)
        ExternalFilmCondensation.define_parameters(self)


    def define_variables(self):

        Pipe.define_variables(self)
        ExternalFilmCondensation.define_variables(self)


    def DeclareEquations(self):

        Pipe.DeclareEquations(self)
        ExternalFilmCondensation.DeclareEquations(self)
