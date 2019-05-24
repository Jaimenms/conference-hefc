__doc__="""
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""


from daetools.pyDAE import *

from daetools_extended.daemodel_extended import daeModelExtended

from daetools_extended.tools import get_node_tree, execute_recursive_method, get_initialdata_from_reporter, update_initialdata, daeVariable_wrapper, distribute_on_domains

from pyUnits import m, kg, s, K, Pa, J, W, rad, mol

from water_properties import conductivity, density, viscosity


class Carbfilm(daeModelExtended):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):

        daeModelExtended.__init__(self, Name, Parent=Parent, Description=Description, data=data, node_tree=node_tree)

        if not Parent:
            self.define_constants()
            self.define_variables()
            self.define_parameters()

    def define_constants(self):

        self.Rg = Constant(8.31 * J / (K * mol)) # Gas universal constant
        self.cH = Constant(29.5) #CO2 Henry constant
        self.k1 = Constant(4.47e-7) # Calcium carbonate first order dissociation constant
        self.k2 = Constant(4.68e-11) # Calcium carbonate second order dissociation constant
        self.ksp = Constant(4.9e-9) # Calcium solubility product
        self.kf = Constant(2.941 * (W ** (1)) * (m ** (-1)) * (K ** (-1))) # Film thermal conductivity
        self.rhof = Constant(2.71e3 * (kg ** (1)) * (m ** (-3))) # Film density
        self.psi = Constant(0.01)  # Deposition strength factor
        self.conc_H = Constant(10 ** (-9.55)) #Concentration of Hydrogen cation
        self.conc_Ca = Constant(0.0037) #Calcium concentration
        self.pCO2 = Constant(0.0314 / 100) #CO2 partial pressure

    def define_variables(self):

        # Variable types
        mass_film_t = daeVariableType("mass_film_t", (kg ** (1)) * (m ** (-2)), 1e-9, 1e+04, 1e-06, 1e-6)
        rate_t = daeVariableType("rate_t", (kg ** (1)) * (m ** (-2)) * (s ** (-1)), 1e-9, 1e+04, 0.2, 1e-06)
        fouling_factor_t = daeVariableType("fouling_factor_t", (K ** (1)) * (W ** (-1)) * (m ** (2)), 0.0, 1e4,
                                               1e-3, 1e-9)

        self.mf = daeVariable("mf", mass_film_t, self, "Film Mass per Area", self.Domains)
        self.phid = daeVariable("phip", rate_t, self, "Film specific deposit rate", self.Domains)
        self.phir = daeVariable("phir", rate_t, self, "Film specific removal rate", self.Domains)
        self.Rf = daeVariable("Rf", fouling_factor_t, self, "Fouling factor", self.Domains)


    def define_parameters(self):

        lagt = self.data['constants']['lagt']

        self.lagt = Constant(lagt*s)

        self.mfi = daeParameter("mfi", (kg ** (1)) * (m ** (-2)), self, "Initial film density")


    def eq_film(self):

        self.IF(Time() < self.lagt, eventTolerance=1E-5)

        eq = self.CreateEquation("FilmOFF", "Film - OFF")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        mf = daeVariable_wrapper(self.mf, domains)
        eq.Residual = mf - self.mfi()

        self.ELSE()

        eq = self.CreateEquation("FilmON", "Film - ON")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        mf = daeVariable_wrapper(self.mf, domains)
        phid = daeVariable_wrapper(self.phid, domains)
        phir = daeVariable_wrapper(self.phir, domains)

        eq.Residual = self.dt_day(mf) - (phid - phir)

        self.END_IF()


    def eq_phid(self):

        eq = self.CreateEquation("phid", "phid")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        k1 = self.k1
        k2 = self.k2
        cH = self.cH
        ksp = self.ksp
        pCO2 = self.pCO2
        conc_H = self.conc_H
        conc_Ca = self.conc_Ca

        conc_CO2 = pCO2 / cH
        conc_HCO3 = (conc_CO2 * k1) / conc_H
        conc_CO3 = (conc_HCO3 * k2) / conc_H

        phid = daeVariable_wrapper(self.phid, domains)
        D = daeVariable_wrapper(self.D, domains)
        v = daeVariable_wrapper(self.v, domains)
        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        #Tast = 35+273.15
        Tast = T / Constant(1 * K)
        Past = P / Constant(1 * Pa)
        vast = v / Constant(1 * m / s)

        rho = density( Tast, Past, simplified = True) * Constant(1 * (kg ** (1))*(m ** (-3)))
        kappa = conductivity( Tast, Past, simplified = True) * Constant(1 * (K ** (-1))*(W ** (1))*(m ** (-1)))
        muast = viscosity( Tast, Past, simplified = True)
        mu = muast  * Constant(1 * (Pa ** (1))*(s ** (1)))

        Re = D * v * rho / mu

        kr = Exp(38.74 - Constant(20700.0 * 4.184 * J /mol) / (self.Rg * T))

        Dab = Constant( 3.07e-15 * m ** 2 / s) * (Tast / muast)

        Sc = mu / (rho * Dab)

        kd = 0.023 * vast * Re ** -0.17 * Sc ** -0.67

        eq.Residual = phid - Constant(1 * kg * m ** -2 * s ** -1) * kd * \
                      conc_CO3 * (1 - ksp / (conc_Ca * conc_CO3)) / \
                      (1 + kd / (kr * conc_CO3) + conc_CO3 / conc_Ca)


    def eq_phir(self):

        eq = self.CreateEquation("phir", "phir")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)
        phir = daeVariable_wrapper(self.phir, domains)
        phid = daeVariable_wrapper(self.phid, domains)
        D = daeVariable_wrapper(self.D, domains)
        v = daeVariable_wrapper(self.v, domains)


        kf = self.kf
        rhof = self.rhof
        psi = self.psi
        Di = self.Di()

        espes = (Di - D) / 2

        vast = v / Constant(1 * m / s)
        kfast = kf / Constant(1 * (W ** (1)) * (m ** (-1)) * (K ** (-1)))
        espesast = espes / Constant(1 * m)
        rhofast = rhof / Constant(1 * kg / m **3)

        eq.Residual = phir - phid *  0.00212 * vast ** 2 / ( Sqrt(kfast) * psi)


    def eq_internal_diameter(self):

        eq = self.CreateEquation("D", "D_internal_flow_diameter")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        D = daeVariable_wrapper(self.D, domains)
        mf = daeVariable_wrapper(self.mf, domains)
        rhof = self.rhof
        Di = self.Di()

        eq.Residual = D - Sqrt(Di ** 2 - 4 * mf * Di / rhof)


    def eq_Rf(self):

        eq = self.CreateEquation("Rf", "Rf")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        D = daeVariable_wrapper(self.D, domains)
        Rf = daeVariable_wrapper(self.Rf, domains)
        kf = self.kf
        Di = self.Di()

        eq.Residual = Rf - Di * Log(Di / D ) / (2 * kf)


    def eq_ep(self):

        eq = self.CreateEquation("Roughness", "Roughness")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        ep = daeVariable_wrapper(self.ep, domains)
        epw = self.epw()

        eq.Residual = ep - epw


    def DeclareEquations(self):

        daeModelExtended.DeclareEquations(self)

        self.eq_film()
        self.eq_phid()
        self.eq_phir()
        #self.eq_internal_diameter()
        self.eq_Rf()
        #self.eq_ep()