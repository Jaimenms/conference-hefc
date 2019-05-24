__doc__ = """
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""

from daetools.pyDAE import *
from pyUnits import m, kg, s, K, Pa, J, W, rad

import pandas as pd


try:
    from models.external_film_condensation_tube_arrange import ExternalFilmCondensationTubeArrange
    from models.carbfilm import Carbfilm
except:
    from .external_film_condensation_tube_arrange import ExternalFilmCondensationTubeArrange
    from .carbfilm import Carbfilm

from daetools_extended.tools import daeVariable_wrapper, distribute_on_domains


class CarbfilmedExternalFilmCondensationTubeArrange(Carbfilm, ExternalFilmCondensationTubeArrange):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):
        ExternalFilmCondensationTubeArrange.__init__(self, Name, Parent=Parent, Description=Description, data=data,
                                             node_tree=node_tree)

    def define_constants(self):
        ExternalFilmCondensationTubeArrange.define_constants(self)
        Carbfilm.define_constants(self)

    def define_parameters(self):
        ExternalFilmCondensationTubeArrange.define_parameters(self)
        Carbfilm.define_parameters(self)

    def define_variables(self):
        ExternalFilmCondensationTubeArrange.define_variables(self)

        Carbfilm.define_variables(self)


    def define_parameters(self):
        ExternalFilmCondensationTubeArrange.define_parameters(self)

        Carbfilm.define_parameters(self)


    def eq_total_he(self):

        eq = self.CreateEquation("TotalHeat", "Heat balance - Qout")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        Text = self.Text()
        T = daeVariable_wrapper(self.T, domains)
        Qout = daeVariable_wrapper(self.Qout, domains)
        hext = daeVariable_wrapper(self.hext, domains)
        hint = daeVariable_wrapper(self.hint, domains)
        D = daeVariable_wrapper(self.D, domains)
        Rf = daeVariable_wrapper(self.Rf, domains)

        kwall = self.kwall()
        Do = self.Do()
        Di = self.Di()
        pi = self.pi

        Resext = 1 / (pi * Do * hext)
        Resint = 1 / (pi * D * hint)
        Reswall = Log(Do / Di) / (2 * pi * kwall)

        eq.Residual = Qout * (Resint + Reswall + Resext + Rf/(Di * pi)) - (Text - T )


    def DeclareEquations(self):

        ExternalFilmCondensationTubeArrange.DeclareEquations(self)
        Carbfilm.DeclareEquations(self)
