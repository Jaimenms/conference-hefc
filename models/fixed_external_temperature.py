__doc__="""
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""

from daetools.pyDAE import *
from daetools_extended.daemodel_extended import daeModelExtended

from pyUnits import m, kg, s, K, Pa, J, W, rad

from water_properties import density, viscosity, conductivity, heat_capacity
from daetools_extended.tools import daeVariable_wrapper, distribute_on_domains

class FixedExternalTemperature(daeModelExtended):

    def __init__(self, Name, Parent=None, Description=""):

        daeModel.__init__(self, Name, Parent=Parent, Description=Description)

    def define_parameters(self):

        self.Do = daeParameter("Do", m, self, "Outside pipe diameter")
        self.kwall = daeParameter("kwall", (K ** (-1))*(J ** (1))*(s ** (-1))*(m ** (-1)), self, "Wall conductivity")
        self.ResF = daeParameter("ResF", (K ** (1))*(W ** (-1)), self, "Fouling Resistance")


    def define_variables(self):

        # Variable types
        water_temperature_t = daeVariableType("temperature_t", (K ** (1)), 273.0, 400.0, 300.0, 0.01)
        heat_per_length_t = daeVariableType("heat_per_length_t", (J ** (1)) * (m ** (-1)) * (s ** (-1)), -1e+10, 1e+10, 0.1, 1e-05)
        thermal_resistance_t = daeVariableType("thermal_resistance_t", (K ** (1)) * (W ** (-1)) * (m ** (1)), 1e-6,
                                               100., 1e-6, 1e-05)
        heat_transfer_coefficient_t = daeVariableType("heat_transfer_coefficient_t",
                                                      (K ** (-1)) * (W ** (1)) * (m ** (-2)), 0.01,
                                                      1000000, 10000, 1e-01)

        self.To = daeVariable("To", water_temperature_t, self, "Outside Wall Temperature", self.Domains)

        self.Ti = daeVariable("Ti", water_temperature_t, self, "Internal Wall Temperature", self.Domains)

        self.hint = daeVariable("hint", heat_transfer_coefficient_t, self, "Internal convection coefficient", self.Domains)


    def eq_calculate_hint(self):

        eq = self.CreateEquation("InternalConvection", "Internal convection - hint")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        fD = daeVariable_wrapper(self.fD, domains)
        hint = daeVariable_wrapper(self.hint, domains)
        D = daeVariable_wrapper(self.D, domains)
        v = daeVariable_wrapper(self.v, domains)

        # Calculates the Nussel dimensionless number using Petukhov correlation modified by Gnielinski. See Incropera 4th Edition [8.63]
        mu = viscosity( T / Constant(1 * K) , P / Constant(1 * Pa), simplified = True)
        kappa = conductivity( T / Constant(1 * K), P / Constant(1 * Pa), simplified = True)
        cp = heat_capacity( T / Constant(1 * K), P / Constant(1 * Pa), simplified = True)
        rho = density( T / Constant(1 * K), P / Constant(1 * Pa), simplified = True)

        Dast = D / Constant(1 * m )
        vast = v / Constant(1 * m * s ** -1)

        Re = Dast * Abs(vast) * rho / mu
        prandtl = cp * mu / kappa
        nusselt = (fD / 8.) * (Re - 1000.) * prandtl / (
                1. + 12.7 * Sqrt(fD / 8.) * (prandtl ** (2 / 3)) - 1.)
        eq.Residual = hint - nusselt * kappa / Dast * Constant(1 * W/(K * m**2))


    def eq_total_he(self):

        eq = self.CreateEquation("TotalHeat", "Heat balance - Qout")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)
        T = daeVariable_wrapper(self.T, domains)
        To = daeVariable_wrapper(self.To, domains)
        Qout = daeVariable_wrapper(self.Qout, domains)
        hint = daeVariable_wrapper(self.hint, domains)
        D = daeVariable_wrapper(self.D, domains)

        Resint = 1 / (self.pi * D * hint) # mK/W
        Reswall = Log(self.Do() / self.Di()) / (2 * self.pi * self.kwall())  # mK/W
        # TODO - Lembrar de colocar o Refilme no caso com Biofilme
        #Resfilm = Log(self.Di() / self.D()) / (2 * self.pi * self.kappa())
        Resistance = (Resint + Reswall + self.ResF() * self.pi * D) # mK/W

        eq.Residual = Qout * Resistance - ( To - T)


    def eq_calculate_Ti(self):

        eq = self.CreateEquation("WallHeat", "Heat balance - wall")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)
        Qout = daeVariable_wrapper(self.Qout, domains)
        To = daeVariable_wrapper(self.To, domains)
        Ti = daeVariable_wrapper(self.Ti, domains)
        Reswall = Log(self.Do() / self.Di()) / (2 * self.pi * self.kwall())
        eq.Residual = Qout - (To - Ti ) / Reswall


    def DeclareEquations(self):
        self.eq_calculate_Ti()
        self.eq_calculate_hint()
        #self.eq_calculate_resistance()
        #self.eq_total_he()
