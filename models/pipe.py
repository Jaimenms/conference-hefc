__doc__="""
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""

#TODO include dplb and dpub calculated with Klp and Kup to be used in the pressure boundary conditions

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
eUpperBound = eUpperBound
eLowerBound = eLowerBound
eCFDM = eCFDM
dt = dt
d = d
from pyUnits import m, kg, s, K, Pa, J, W, rad

try:
    from models.edge import Edge
except:
    from .edge import Edge

from water_properties import density, viscosity, conductivity, heat_capacity

from daetools_extended.tools import daeVariable_wrapper, distribute_on_domains

from scipy.constants import g as gravity
from scipy.constants import pi


class Pipe(Edge):

    def __init__(self, Name, Parent=None, Description=""):

        Edge.__init__(self, Name, Parent=Parent, Description=Description)


    def define_domains(self):

        Edge.define_domains(self)

        self.x = daeDomain("x", self, unit(), "X axis domain")


    def define_constants(self):

        Edge.define_constants(self)

        self.pi = Constant( pi )
        self.g = Constant(gravity * m / s ** 2)
        self.PR = Constant(1e5 * Pa) # bar

        y_domain = []
        if hasattr(self,'y') and type(self.y) == pyCore.daeDomain:
            y_domain.append(self.y)
        self.YDomains = y_domain

        x_domain = []
        if hasattr(self,'x') and type(self.x) == pyCore.daeDomain:
            x_domain.append(self.x)
        self.XDomains = x_domain


    def define_parameters(self):

        Edge.define_parameters(self)

        self.tetha = daeParameter("tetha", rad, self, "Angle")
        self.Di = daeParameter("Di", m, self, "Inside pipe diameter")
        self.L = daeParameter("L", m, self, "Length")
        self.epw = daeParameter("epw", m, self, "Wall Roughness")
        self.Kub = daeParameter("Kub", unit(), self, "Upper bound concentrated accident coefficient")
        self.Klb = daeParameter("Klb", unit(), self, "Lower bound concentrated accident coefficient")
        self.Npipes = daeParameter("Npipes", unit(), self, "Number of pipes", self.YDomains)


    def define_variables(self):

        Edge.define_variables(self)

        # Variable types
        diameter_t = daeVariableType("diameter_t", (m ** (1)), 1e-6, 1e1, 0.015, 1e-6)
        darcy_t = daeVariableType("darcy_t", dimless, 0.0001, 5, 0.018, 1e-03)
        water_temperature_t = daeVariableType("water_temperature_t", (K ** (1)), 273.0, 373.0, 310.0, 1e-5)
        mass_flowrate_t = daeVariableType("mass_flowrate_t", (kg ** (1)) * (s ** (-1)), 1e-6, 1e2, 1e-1, 1e-6)
        velocity_t = daeVariableType("velocity_t", (m ** (1)) * (s ** (-1)), 1e-6, 1e2, 1e0, 1e-06)
        heat_per_length_t = daeVariableType("heat_per_length_t", (J ** (1)) * (m ** (-1)) * (s ** (-1)), -1e+10, 1e+10,
                                            0.1, 1e-05)
        pressure_t = daeVariableType("pressure_t", (Pa ** (1)), 1e2, 1e7, 1e5, 1e-5)
        delta_pressure_t = daeVariableType("delta_pressure_t", (Pa ** (1)), -1e7, 1e7, 0, 1e-5)



        # Secondary variables
        self.H = daeVariable("H", power_t, self, "Fluid Entalphy", self.Domains)
        self.fD = daeVariable("fD", darcy_t, self, "Darcy friction factor", self.Domains)
        self.D = daeVariable("D", diameter_t, self, "Internal flow diameter", self.Domains)
        self.v = daeVariable("v", velocity_t, self, "Internal flow velocity", self.Domains)
        self.Qout = daeVariable("Qout", heat_per_length_t, self, "Heat source per length", self.Domains)
        self.Qtotal = daeVariable("Qtotal", power_t, self, "Exchanged energy per time per tube", self.YDomains)

        # State variables
        self.P = daeVariable("P", pressure_t, self, "Fluid Pressure", self.Domains)
        self.T = daeVariable("T", water_temperature_t, self, "Fluid Temperature", self.Domains)

        # Concentrate state variable
        self.k = daeVariable("k", mass_flowrate_t, self, "Mass flowrate", self.Domains)

        # Bounds
        self.klb = daeVariable("klb", mass_flowrate_t, self, "Lower Bound Mass flowrate")
        self.kub = daeVariable("kub", mass_flowrate_t, self, "Upper Bound Mass flowrate")
        self.Hub = daeVariable("Hub", power_t, self, "Upper Bound Fluid Enthalpy")
        self.Hlb = daeVariable("Hlb", power_t, self, "Lower Bound Fluid Enthalpy")
        self.dPlb = daeVariable("dPlb", delta_pressure_t, self, "Lower Bound Concentrated Pressure Loss", self.YDomains)
        self.dPub = daeVariable("dPub", delta_pressure_t, self, "Upper Bound Concentrated Pressure Loss", self.YDomains)


    def eq_velocity(self):

        eq = self.CreateEquation("v", "v_fluid_velocity")
        xdomains = distribute_on_domains(self.XDomains, eq, eClosedClosed)
        ydomains = distribute_on_domains(self.YDomains, eq, eClosedClosed)
        domains = xdomains + ydomains

        k = daeVariable_wrapper(self.k, domains)
        D = daeVariable_wrapper(self.D, domains)
        v = daeVariable_wrapper(self.v, domains)
        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        Tast = T / Constant(1 * K)
        Past = P / Constant(1 * Pa)

        rho = density( Tast, Past, simplified = True) * Constant(1 * (kg ** (1))*(m ** (-3)))

        A = 0.25 * 3.14 * D ** 2
        eq.Residual = v - k / ( rho * A )


    def eq_entalphy(self):

        eq = self.CreateEquation("Entalphy", "Fluid Entalphy")
        xdomains = distribute_on_domains(self.XDomains, eq, eClosedClosed)
        ydomains = distribute_on_domains(self.YDomains, eq, eClosedClosed)
        domains = xdomains + ydomains

        k = daeVariable_wrapper(self.k, domains)

        H = daeVariable_wrapper(self.H, domains)
        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        Tast = T / Constant(1 * K)
        Past = P / Constant(1 * Pa)
        cp = heat_capacity( Tast, Past, simplified = True) * Constant(1 * (J ** (1))*(K ** (-1))*(kg ** (-1)))

        eq.Residual = k * cp * T - H


    def eq_internal_diameter(self):

        eq = self.CreateEquation("D", "D_internal_flow_diameter")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        Di = self.Di()
        D = daeVariable_wrapper(self.D, domains)

        eq.Residual = D - Di


    def eq_fD(self):

        eq = self.CreateEquation("fDturb", "Turbulent darcy factor")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        fD = daeVariable_wrapper(self.fD, domains)

        v = daeVariable_wrapper(self.v, domains)
        D = daeVariable_wrapper(self.D, domains)
        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        Tast = T / Constant(1 * K)
        Past = P / Constant(1 * Pa)

        mu = viscosity( Tast, Past, simplified = True)  * Constant(1 * (Pa ** (1))*(s ** (1)))
        rho = density( Tast, Past, simplified = True) * Constant(1 * (kg ** (1))*(m ** (-3)))

        Re = D * Abs(v) * rho / mu

        A = (2.457 * Log(((7 / Re) ** 0.9 + 0.27 * self.epw() / D) ** -1)) ** 16
        B = (37530 / Re) ** 16
        ff = 2 * ((8 / Re) ** 12 + (A + B) ** -1.5) ** (1 / 12)

        eq.Residual = fD - 4 * ff


    def eq_lowerbound_flowrate(self):

        eq = self.CreateEquation("LowerBoundFlowrate", "Lower Bound Flowrate")

        klb = self.klb()

        if self.YDomains:
            k = self.k.array(0,'*')
            Npipes = self.Npipes.array('*')
            eq.Residual = klb - Sum(k * Npipes)
        else:
            k = self.k(0)
            Npipes = self.Npipes()
            eq.Residual = klb - k * Npipes


    def eq_upperbound_flowrate(self):

        eq = self.CreateEquation("UpperBoundLowrate", "Upper Bound Flowrate")

        kub = self.kub()

        if self.YDomains:
            k = self.k.array(-1,'*')
            Npipes = self.Npipes.array('*')
            eq.Residual = kub - Sum(k * Npipes)
        else:
            k = self.k(-1)
            Npipes = self.Npipes()
            eq.Residual = kub - k * Npipes


    def eq_lowerbound_enthalpy(self):

        eq = self.CreateEquation("LowerBoundEnthalpy", "Lower Bound Enthalpy")

        Hlb = self.Hlb()

        if self.YDomains:
            H = self.H.array(0, '*')
            Npipes = self.Npipes.array('*')
            eq.Residual = Hlb - Sum(H * Npipes)
        else:
            H = self.H(0)
            Npipes = self.Npipes()
            eq.Residual = Hlb - H * Npipes


    def eq_upperbound_enthalpy(self):

        eq = self.CreateEquation("UpperBoundEnthalpy", "Upper Bound Enthalpy")

        Hub = self.Hub()

        if self.YDomains:
            H = self.H.array(-1, '*')
            Npipes = self.Npipes.array('*')
            eq.Residual = Hub - Sum(H * Npipes)
        else:
            H = self.H(-1)
            Npipes = self.Npipes()
            eq.Residual = Hub - H * Npipes


    def eq_lowerbound_pressureloss(self):

        eq = self.CreateEquation("LowerBoundPressureLoss", "Lower Bound Pressure Loss")
        xdomains = distribute_on_domains(self.XDomains, eq, eLowerBound)
        ydomains = distribute_on_domains(self.YDomains, eq, eClosedClosed)
        domains = xdomains + ydomains

        dPlb = daeVariable_wrapper(self.dPlb, ydomains)
        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        v = daeVariable_wrapper(self.v, domains)
        Klb = self.Klb()

        Tast = T / Constant(1 * K)
        Past = P / Constant(1 * Pa)
        rho = density(Tast, Past, simplified=True) * Constant(1 * (kg ** (1)) * (m ** (-3)))
        eq.Residual = dPlb - 0.5 * Klb * rho * v ** 2


    def eq_upperbound_pressureloss(self):

        eq = self.CreateEquation("UpperBoundPressureLoss", "Upper Bound Pressure Loss")
        xdomains = distribute_on_domains(self.XDomains, eq, eUpperBound)
        ydomains = distribute_on_domains(self.YDomains, eq, eClosedClosed)
        domains = xdomains + ydomains

        dPub = daeVariable_wrapper(self.dPub, ydomains)
        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        v = daeVariable_wrapper(self.v, domains)
        Kub = self.Kub()

        Tast = T / Constant(1 * K)
        Past = P / Constant(1 * Pa)
        rho = density(Tast, Past, simplified=True) * Constant(1 * (kg ** (1)) * (m ** (-3)))
        eq.Residual = dPub - 0.5 * Kub * rho * v ** 2


    def eq_mass_balance(self):

        eq = self.CreateEquation("MassBal", "Mass balance")
        ydomains = distribute_on_domains(self.YDomains, eq, eClosedClosed)
        xdomains = distribute_on_domains(self.XDomains, eq, eOpenClosed)
        domains = xdomains + ydomains

        L = self.L()
        k = daeVariable_wrapper(self.k, domains)
        D = daeVariable_wrapper(self.D, domains)
        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        Tast = T / Constant(1 * K)
        Past = P / Constant(1 * Pa)

        rho = density( Tast, Past, simplified = True) * Constant(1 * (kg ** (1))*(m ** (-3)))

        Area = 0.25 * 3.14 * D ** 2

        #eq.Residual =  self.dt(rho * Area ) + 24 * 3600 * d(k, self.x, eCFDM) / L
        eq.Residual =  self.dt(rho * Area ) + d(k, self.x, eCFDM) / L


    def eq_mommentum_balance(self):

        eq = self.CreateEquation("MomBal", "Momentum balance")
        ydomains = distribute_on_domains(self.YDomains, eq, eClosedClosed)
        xdomains = distribute_on_domains(self.XDomains, eq, eOpenClosed)
        domains = xdomains + ydomains

        g = self.g
        L = self.L()
        tetha = self.tetha()
        k = daeVariable_wrapper(self.k, domains)
        fD = daeVariable_wrapper(self.fD, domains)
        v = daeVariable_wrapper(self.v, domains)
        D = daeVariable_wrapper(self.D, domains)
        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        Tast = T / Constant(1 * K)
        Past = P / Constant(1 * Pa)

        rho = density( Tast, Past, simplified = True) * Constant(1 * (kg ** (1))*(m ** (-3)))

        hL = 0.5 * fD * (v ** 2) / ( D * g )

        DeltaP = g * rho * hL

        A = 0.25 * 3.14 * D ** 2

        # eq.Residual = self.dt(A * rho * v) + \
        #               d(k * v, self.x, eCFDM) / L + \
        #               A * d(P, self.x,eCFDM) / L + \
        #               A * DeltaP + A * rho * g * Sin(tetha)

        eq.Residual = d(k * v, self.x, eCFDM) / L + \
                      A * d(P, self.x,eCFDM) / L + \
                      A * DeltaP + A * rho * g * Sin(tetha)

        # eq.Residual = d(k * v, self.x, eCFDM) / L + \
        #               24 * 3600 * A * d(P, self.x,eCFDM) / L + \
        #               24 * 3600 * A * DeltaP + 24 * 3600 * A * rho * g * Sin(tetha)

        #eq.Residual = d(P, self.x, eCFDM) / L +  DeltaP


    def eq_heat_balance(self):

        eq = self.CreateEquation("HeatBal", "Heat balance - T")
        ydomains = distribute_on_domains(self.YDomains, eq, eClosedClosed)
        xdomains = distribute_on_domains(self.XDomains, eq, eOpenClosed)
        domains = xdomains + ydomains

        L = self.L()
        D = daeVariable_wrapper(self.D, domains)
        k = daeVariable_wrapper(self.k, domains)
        Qout = daeVariable_wrapper(self.Qout, domains)
        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        Tast = T / Constant(1 * K)
        Past = P / Constant(1 * Pa)

        cp = heat_capacity( Tast, Past, simplified = True) * Constant(1 * (J ** (1))*(K ** (-1))*(kg ** (-1)))
        rho = density( Tast, Past, simplified = True) * Constant(1 * (kg ** (1))*(m ** (-3)))

        A = 0.25 * 3.14 * D ** 2
        eq.Residual = self.dt(rho * cp * A * T) + \
                      d(k * cp * T, self.x, eCFDM) / L - \
                      Qout
        #eq.Residual = d(k * cp * T, self.x, eCFDM) / L - \
        #              Qout

    def eq_total_he(self):
        eq = self.CreateEquation("TotalHeat", "Heat balance - Qout")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)
        Qout = daeVariable_wrapper(self.Qout, domains)
        eq.Residual = Qout


    def eq_total_Qout(self):
        eq = self.CreateEquation("TotalQ", "TotalQ")

        L = self.L()
        if self.YDomains:
            y = eq.DistributeOnDomain(self.y, eClosedClosed)
            Npipes = self.Npipes(y)
            Qout = self.Qout.array('*',y)
            Qtotal = self.Qtotal(y)
        else:
            Npipes = self.Npipes()
            Qout = self.Qout.array('*')
            Qtotal = self.Qtotal()

        eq.Residual = Qtotal - Integral(Qout)*L*Npipes


    def dt(self, x):
        return dt(x)

    def dt_day(self,x):
        """
        New derivative in terms of day (Daetools dt considers time in seconds)
        :param x:
        :return:
        """

        return dt(x)/(24*3600)

    def DeclareEquations(self):

        Edge.DeclareEquations(self)

        # friction factors
        self.eq_fD() # x * y

        # Nodal Specifications (P1, P2, T1)
        self.eq_pressure_boundaries() # 2 * y
        self.eq_temperature_boundaries() # y

        # Internal Diameter
        self.eq_internal_diameter() # x * y

        # v and Re
        self.eq_velocity() # x * y

        # P
        self.eq_mass_balance() # (x-1) * y
        self.eq_mommentum_balance() # (x-1) * y

        # T, H, and Qout
        self.eq_entalphy() # x * y
        self.eq_heat_balance() # (x-1) * y
        self.eq_total_he()  # x * y

        # Bounds
        self.eq_upperbound_flowrate() # 1
        self.eq_lowerbound_flowrate() # 1

        self.eq_upperbound_enthalpy() # 1
        self.eq_lowerbound_enthalpy() # 1

        self.eq_upperbound_pressureloss()
        self.eq_lowerbound_pressureloss()

        self.eq_total_Qout()
