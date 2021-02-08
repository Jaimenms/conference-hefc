__doc__="""
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""

from daetools.pyDAE import *
from models.tube_arrange import TubeArrange
from models.external_film_condensation import ExternalFilmCondensation


class ExternalFilmCondensationTubeArrange(ExternalFilmCondensation, TubeArrange):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):
        TubeArrange.__init__(self, Name, Parent=Parent, Description=Description)


    def define_parameters(self):
        TubeArrange.define_parameters(self)
        ExternalFilmCondensation.define_parameters(self)


    def define_variables(self):
        TubeArrange.define_variables(self)
        ExternalFilmCondensation.define_variables(self)


    def DeclareEquations(self):
        TubeArrange.DeclareEquations(self)
        ExternalFilmCondensation.DeclareEquations(self)
