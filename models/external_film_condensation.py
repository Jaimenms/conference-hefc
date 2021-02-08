__doc__="""
DaetTools model that describes the behavior of a water flowing in a pipe with the effect of biofim formation.
"""

from daetools.pyDAE import *

from pyUnits import m, kg, s, K, Pa, J, W, rad

from daetools_extended.tools import daeVariable_wrapper, distribute_on_domains

from water_properties import density, viscosity, conductivity, heat_capacity
from water_at_saturation_properties import saturation_temperature, vapour_density, vapour_total_compressibility,vaporization_enthalpy


class ExternalFilmCondensation(daeModel):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):

        daeModel.__init__(self, Name, Parent=Parent, Description=Description)


    def define_parameters(self):

        self.Do = daeParameter("Do", m, self, "Outside pipe diameter")
        self.kwall = daeParameter("kwall", (K ** (-1))*(J ** (1))*(s ** (-1))*(m ** (-1)), self, "Wall conductivity")
        self.Pext0 = daeParameter("Pext0", Pa, self, "Initial External Pressure")
        self.Vext = daeParameter("Vext", m**3, self, "External Volume")
        self.PextSP = daeParameter("PextSP", Pa, self, "External Setpoint Pressure")
        self.PextH = daeParameter("PextH", Pa, self, "External High Pressure")
        self.fNtub = daeParameter("fNtub", unit(), self, "Factor for number of pipes over the actual pipe, including it", self.YDomains)
        self.kvap = daeParameter("kvap", kg/s, self, "Vapour Inlet Flowrate")
        self.ResF = daeParameter("ResF", (K ** (1))*(W ** (-1)), self, "Fouling Resistance")



    def define_variables(self):

        # Variable types
        temperature_t = daeVariableType("temperature_t", (K ** (1)), 273.0, 473.0, 310.0, 1e-5)
        thermal_resistance_t = daeVariableType("thermal_resistance_t", (K ** (1))*(W ** (-1))*(m ** (1)), 1e-6, 1e3, 1e-3, 1e-5)
        heat_transfer_coefficient_t = daeVariableType("heat_transfer_coefficient_t",
                                                      (K ** (-1)) * (W ** (1)) * (m ** (-2)), 1e-3,
                                                      1e6, 1e3, 1e-5)

        flowrate_t = daeVariableType("flowrate_t", (kg ** (1)) * (s ** (-1)), 0., 200.0, 1.0, 1e-09,
                                          eValueGT)

        self.To = daeVariable("To", temperature_t, self, "Outside Wall Temperature", self.Domains)
        self.Ti = daeVariable("Ti", temperature_t, self, "Inside Wall Temperature", self.Domains)
        self.hint = daeVariable("hint", heat_transfer_coefficient_t, self, "Internal Convection coefficient", self.Domains)
        self.hext = daeVariable("hext", heat_transfer_coefficient_t, self, "External Convection coefficient", self.Domains)

        self.Pext = daeVariable("Pext", pressure_t, self, "External Pressure")
        self.Text = daeVariable("Text", temperature_t, self, "External Temperature")

        self.kcond = daeVariable("kcond", flowrate_t, self, "Condensate Outlet Flowrate")
        self.wext = daeVariable("wext", flowrate_t, self, "Vapour Outlet Flowrate")
        #self.Resistance = daeVariable("Resistance", thermal_resistance_t, self, "Overall Thermal Resistance", self.Domains)


    def eq_calculate_kcond(self):

        eq = self.CreateEquation("CondensateFlowrate", "CondensateFlowrate")

        Past = self.Pext() / Constant(1 * Pa)
        hvap = vaporization_enthalpy(Past, simplified = True) * Constant(1 * J * (kg**-1) )

        kcond = self.kcond()
        if self.YDomains:
            Q = Sum(self.Qtotal.array('*'))
        else:
            Q = self.Qtotal()

        eq.Residual = kcond - Q / hvap


    def eq_ext_relief(self):

        self.stnRegulator = self.STN("Regulator")

        self.STATE("Closed")

        eq = self.CreateEquation("ReliefSystem1", "ReliefSystem1")
        wext = self.wext()
        Pext = self.Pext()
        PextH = self.PextH()
        kvap = self.kvap()

        eq.Residual = wext

        #self.ON_CONDITION(self.Pext() >= self.PextSP() , switchToStates=[('Regulator', 'Openned')],
        #                  setVariableValues=[],
        #                  triggerEvents=[],
        #                  userDefinedActions=[])


        self.STATE("Openned")

        eq = self.CreateEquation("ReliefSystem2", "ReliefSystem2")
        wext = self.wext()
        kvap = self.kvap()
        eq.Residual = wext - kvap

        #self.ON_CONDITION(self.Pext() <= self.Pext0() , switchToStates=[('Regulator', 'Closed')],
        #                  setVariableValues=[],
        #                  triggerEvents=[],
        #                  userDefinedActions=[])

        self.END_STN()


    def eq_calculate_Pext(self):

        self.stnShellPressure = self.STN("ShellPressure")

        self.STATE("Fixed")

        eq = self.CreateEquation("ExternalPressureInitial", "ExternalPressureInitial")
        Pext = self.Pext()
        Pext0 = self.Pext0()
        eq.Residual = Pext - Pext0

        self.STATE("PreVariable")

        eq = self.CreateEquation("ExternalPressureInitial", "ExternalPressureInitial")
        Pext = self.Pext()
        Pext0 = self.Pext0()
        eq.Residual = Pext - Pext0

        self.ON_CONDITION(Time() > Constant(0*s), switchToStates     = [ ('ShellPressure', 'Variable') ],
                                                      setVariableValues  = [],
                                                      triggerEvents      = [],
                                                      userDefinedActions = [] )

        self.STATE("Variable")
        eq = self.CreateEquation("ExternalPressure", "ExternalPressure")
        Pext = self.Pext()
        Vext = self.Vext()
        kcond = self.kcond()
        kvap = self.kvap()
        wext = self.wext()
        Past = Pext / Constant(1 * Pa)
        drhodPshell = vapour_total_compressibility(Past) * Constant(1 * kg * (m**-3) * (Pa**-1) )
        eq.Residual =  self.dt_day(Pext)* (Vext * drhodPshell) - (kvap - wext - kcond)

        self.STATE("Constant")
        eq = self.CreateEquation("ExternalPressure", "ExternalPressure")
        eq.Residual =  Pext - self.PextSP()


        self.END_STN()


    def eq_calculate_Text(self):
        eq = self.CreateEquation("ExternalTemperature", "ExternalTemperature")
        Pext = self.Pext()
        Past = Pext / Constant(1 * Pa)
        eq.Residual = self.Text() - saturation_temperature(Past, simplified=True) * Constant(1 * K)


    def eq_calculate_hint(self):

        eq = self.CreateEquation("InternalConvection", "Internal convection - hint")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        T = daeVariable_wrapper(self.T, domains)
        P = daeVariable_wrapper(self.P, domains)
        fD = daeVariable_wrapper(self.fD, domains)
        Re = daeVariable_wrapper(self.Re, domains)
        hint = daeVariable_wrapper(self.hint, domains)
        D = daeVariable_wrapper(self.D, domains)

        # Calculates the Nussel dimensionless number using Petukhov correlation modified by Gnielinski. See Incropera 4th Edition [8.63]
        Tast = T / Constant(1 * K)
        Past = P / Constant(1 * Pa)

        mu = viscosity( Tast, Past, simplified = True)
        kappa = conductivity( Tast, Past, simplified = True)
        cp = heat_capacity( Tast, Past, simplified = True)
        prandtl = cp * mu / kappa
        kappa_i = kappa * Constant(1 * (K ** (-1))*(W ** (1))*(m ** (-1)))

        nusselt = (fD / 8.) * (Re - 1000.) * prandtl / (1. + 12.7 * Sqrt(fD / 8.) * (prandtl ** (2 / 3)) - 1.)
        hint_calc = nusselt * kappa_i / D

        eq.Residual = hint - hint_calc


    def eq_calculate_hext(self):

        eq = self.CreateEquation("Hext", "Heat balance - Hext")
        xdomains = distribute_on_domains(self.XDomains, eq, eClosedClosed)
        ydomains = distribute_on_domains(self.YDomains, eq, eClosedClosed)
        domains = xdomains + ydomains

        g = self.g
        Text = self.Text()
        Do = self.Do()

        To = daeVariable_wrapper(self.To, domains)
        hext = daeVariable_wrapper(self.hext, domains)
        fNtub = daeVariable_wrapper(self.fNtub, ydomains)

        Tast = 0.5 * (Text + To) / Constant(1 * K)
        Past = self.Pext() / Constant(1 * Pa)

        hvap = vaporization_enthalpy(Past, simplified = True) * Constant(1 * J * (kg**-1) )

        rhov = vapour_density( Past, simplified = True) * Constant(1 * (kg ** (1))*(m ** (-3)))
        rho_o = density( Tast, Past, simplified = True) * Constant(1 * (kg ** (1))*(m ** (-3)))
        mu_o = viscosity( Tast, Past, simplified = True) * Constant(1 * (Pa ** (1))*(s ** (1)))
        kappa_o = conductivity( Tast, Past, simplified = True)  * Constant(1 * (K ** (-1))*(W ** (1))*(m ** (-1)))

        num = (g * rho_o * (rho_o - rhov) * kappa_o ** 3 * hvap)

        den = mu_o * Abs(Text - To) * Do

        hd1 = (0.729 * (num / den) ** 0.25)

        eq.Residual = hext - fNtub * hd1


    def eq_total_he(self):

        eq = self.CreateEquation("TotalHeat", "Heat balance - Qout")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        Text = self.Text()
        T = daeVariable_wrapper(self.T, domains)
        Qout = daeVariable_wrapper(self.Qout, domains)
        hint = daeVariable_wrapper(self.hint, domains)
        hext = daeVariable_wrapper(self.hext, domains)
        D = daeVariable_wrapper(self.D, domains)
        Resint = 1 / (self.pi * self.Di() * hint)
        Reswall = Log(self.Do() / self.Di()) / (2 * self.pi * self.kwall())
        Resext = 1 / (self.pi * self.Do() * hext)
        ResFouling = self.ResF() * self.L() # Jaime - Corrigido!

        Resistance = (Resint + Reswall + Resext + ResFouling)

        eq.Residual = Qout * Resistance - (Text - T )


    def eq_calculate_To(self):

        eq = self.CreateEquation("WallHeat1", "Heat balance - wall")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        Do = self.Do()
        Text = self.Text()
        pi = self.pi

        To = daeVariable_wrapper(self.To, domains)
        hext = daeVariable_wrapper(self.hext, domains)
        Qout = daeVariable_wrapper(self.Qout, domains)

        eq.Residual = Qout - (Text - To) * (pi * Do * hext)


    def eq_calculate_Ti(self):

        eq = self.CreateEquation("WallHeat2", "Heat balance - wall")
        domains = distribute_on_domains(self.Domains, eq, eClosedClosed)

        kwall = self.kwall()
        Do = self.Do()
        Di = self.Di()
        pi = self.pi

        Ti = daeVariable_wrapper(self.Ti, domains)
        To = daeVariable_wrapper(self.To, domains)
        Qout = daeVariable_wrapper(self.Qout, domains)

        eq.Residual = Qout *  Log(Do / Di) - (To - Ti) * (2 * pi * kwall)


    def DeclareEquations(self):

        daeModel.DeclareEquations(self)

        self.eq_calculate_Pext()
        self.eq_calculate_Text()
        self.eq_calculate_To()
        self.eq_calculate_Ti()
        self.eq_calculate_hint()
        self.eq_calculate_hext()
        self.eq_calculate_kcond()
        self.eq_ext_relief()
