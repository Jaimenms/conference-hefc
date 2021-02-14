from math import pi
from scipy.optimize import root
import numpy as np
from water_properties import density, viscosity, conductivity, heat_capacity
from water_at_saturation_properties import saturation_temperature, vapour_density, vapour_total_compressibility,vaporization_enthalpy


def calculate_int(Tin, Tout, Pin, Pout, m_tube, ep, Df, L, Di):

    g = 9.81

    T = 0.5 * (Tin + Tout)
    P = 0.5 * (Pin + Pout)

    # Calculating properties
    int_film_density =density(T, P, simplified = True)
    int_film_heat_capacity = heat_capacity(T, P, simplified = True)
    int_film_conductivity = conductivity(T, P, simplified = True)
    int_film_viscosity = viscosity(T, P, simplified = True)
    int_film_prandtl = int_film_heat_capacity * int_film_viscosity / int_film_conductivity

    v = (m_tube /int_film_density ) /(0.25 * pi * Df**2) # m/s
    v_abs = abs(v)

    Re_tube = Df * int_film_density * v_abs / int_film_viscosity

    ff = calculate_fanning(ep, Df, Re_tube)
    fD_tube = 4 * ff

    # Calculating Darcy
    int_film_Re = Df * int_film_density * v_abs / int_film_viscosity
    int_film_fD = calculate_darcy(fD_tube, ep, Df, int_film_Re)

    # Calculates the Nussel dimensionless number using Petukhov correlation modified by Gnielinski. See Incropera 4th Edition [8.63]
    nusselt = (int_film_fD / 8.) * (int_film_Re - 1000.) * int_film_prandtl / ( 1. + 12.7 * (int_film_fD / 8.) ** 0.5 * (int_film_prandtl ** (2 / 3) - 1.))

    hint = nusselt * int_film_conductivity / Di # W/m2K
    Resint = 1 / (pi * Df * hint * L) # W/K

    tau = ( 1 /8 ) *fD_tube *int_film_density * v**2
    hL = 0.5 * fD_tube * v ** 2 /  (Di * g )
    DeltaP = g * int_film_density * hL
    pressure_loss_in_tube = DeltaP * L
    Pout_ = Pin - pressure_loss_in_tube

    return hint, Resint, int_film_heat_capacity, Pout_, fD_tube, pressure_loss_in_tube, v, Re_tube, int_film_density, int_film_viscosity


def calculate_ext(Tvap, Pvap, To, fNtub_tube, L, Do):

    # Calculating properties
    T = 0.5 *(Tvap + To)

    g = 9.80665

    film_density =density(T, Pvap, simplified = True)
    film_heat_capacity = heat_capacity(T, Pvap, simplified = True)
    film_conductivity = conductivity(T, Pvap, simplified = True)
    film_viscosity = viscosity(T, Pvap, simplified = True)
    film_prandtl = film_heat_capacity * film_viscosity / film_conductivity

    exhaust_steam_density = vapour_density(Pvap, simplified = True)
    exhaust_vaporization_heat = vaporization_enthalpy(Pvap, simplified = True)

    num = (g * film_density *
                (film_density - exhaust_steam_density) * film_conductivity ** 3. * exhaust_vaporization_heat)
    den = film_viscosity * (Tvap - To) * Do
    hext_row1 = 0.729 * (num / den) ** 0.25
    Resext_row1 = 1 / (pi * Do * hext_row1 * L)

    hext = hext_row1 * fNtub_tube
    Resext = Resext_row1 / fNtub_tube

    return hext, Resext, exhaust_vaporization_heat


def calculate_wall(Do, Di, kwall, L):
    Reswall = np.log(Do / Di) / (2 * pi * kwall * L)

    return Reswall


def calculate_fouling(Di, Df, kf, L):
    Resfouling = np.log(Di / Df) / (2 * pi * kf * L)

    return Resfouling


def calculate_CO3(pH, Alc):
    k2 = 4.68e-11 # Calcium carbonate second order dissociation constant
    conc_H = 10 ** (-pH)
    conc_CO3 = k2*Alc/1000/(100.0869 * (conc_H + 2*k2))
    return conc_CO3

def fouling(T, v, rho, mu, Df, Ca, Alc, pH):
    Rg = 8.31  # * J / (K * mol)) # Gas universal constant
    k1 = 4.47e-7  # Calcium carbonate first order dissociation constant
    k2 = 4.68e-11  # Calcium carbonate second order dissociation constant
    ksp = 4.9e-9  # Calcium solubility product
    kf = 2.941  # * (W ** (1)) * (m ** (-1)) * (K ** (-1))) # Film thermal conductivity
    rhof = 2.71e3  # * (kg ** (1)) * (m ** (-3))) # Film density
    psi = 0.01  # Deposition strength factor

    conc_Ca = Ca / 1000 / 40.078
    conc_H = 10 ** (-pH)
    conc_CO3 = k2*Alc/1000/(100.0869 * (conc_H + 2*k2))

    Re = Df * v * rho / mu
    kr = np.exp(38.74 - 20700.0 / (1.987 * T))
    Dab = 3.07e-15 * (T / mu)
    Sc = mu / (rho * Dab)
    kd = 0.023 * v * Re ** -0.17 * Sc ** -0.67

    phid = kd * conc_CO3 * (1 - ksp / (conc_Ca * conc_CO3)) / (1 + kd / (kr * conc_CO3) + conc_CO3 / conc_Ca)
    phir = phid * 0.00212 * v ** 2 / (kf ** 0.5 * psi)

    return phid - phir, phid, phir  # kg/m2day

def calculate_darcy(fD0, ep, D, Re):
    """Calculate the darcy friction factor"""
    def idarcy(ifD, ep, D, Re):
        return ifD + 2. * np.log10(ep / 3.72 / D + (2.51 / Re) * ifD )
    sol = root(idarcy, fD0 ** -0.5, args=(ep, D, Re),)
    return  sol.x[0] ** -2

def calculate_fanning(ep, D, Re):
    """Calculate the fanning friction factor"""
    A = (2.457*np.log(((7/Re)**0.9+0.27*ep/D)**-1))**16
    B = (37530/Re)**16
    ff = 2 *((8/Re)**12 + (A+B)**-1.5) ** (1/12)
    return  ff


def calculate_heat(k_tube,
                   cp,
                   Tin,
                   Tout):
    """Calculate the duty"""
    return k_tube * cp * (Tout - Tin)


def calculate_LMTD(T1a, T1b, T2a, T2b):
    """Calculate LMTD"""
    dT1 = T1a - T1b
    dT2 = T2a - T2b
    return (dT1 - dT2) / np.log(dT1 / dT2)


def calculate_heat_via_LMTD(UA, LMTD):
    """Calculate heat exchanger via LMTD"""
    return UA * LMTD


def fun(x, m, Tvap, Tin, Pin, Pvap, fNtub, Rows, tubes_per_width, kf, kwall, ep, L, Df, Do, Di, Ca, Alc, pH):
    f = []

    m_ = 0

    Pout = x[0]

    for i in range(0, Rows):
        fNtub_i = fNtub[i]

        Tout, Tf_in, Tf_out, Ti_in, Ti_out, To_in, To_out, m_tube = x[(8 * i + 1):(8 * (i + 1) + 1)]

        m_ += m_tube * tubes_per_width

        #### FOULING RESISTANCE
        Resfouling = calculate_fouling(Di, Df, kf, L)

        #### WALL RESISTANCE
        Reswall = calculate_wall(Do, Di, kwall, L)

        #### EXTERNAL RESISTANCE
        To = 0.5 * (To_in + To_out)
        hext, Resext, _ = calculate_ext(Tvap, Pvap, To, fNtub_i, L, Do)

        #### INTERNAL RESISTANCE
        hint, Resint, cp, Pout_, fD_tube, pressure_loss_in_tube, v, Re_tube, _, _ = calculate_int(
            Tin, Tout, Pin, Pout, m_tube, ep, Df, L, Di
        )

        # Calculate Overall he
        Restotal = Resext + Resint + Reswall + Resfouling  # W/K

        UA = 1 / Restotal  # W/K

        # Wall conduction
        Reswall = np.log(Do / Di) / (2 * pi * kwall * L)

        LMTD = calculate_LMTD(Tvap, Tin, Tvap, Tout)

        Q1 = calculate_heat_via_LMTD(UA, LMTD)

        Q2 = calculate_heat(m_tube, cp, Tin, Tout)

        Q_at_inlet = (Tvap - Tin) / Restotal  # W
        Q_at_outlet = (Tvap - Tout) / Restotal  # W

        f += [
            Pout - Pout_,
            Q1 - Q2,
            To_in - Tvap + Q_at_inlet * Resext,
            Ti_in - To_in + Q_at_inlet * Reswall,
            Tf_in - Ti_in + Q_at_inlet * Resfouling,
            To_out - Tvap + Q_at_outlet * Resext,
            Ti_out - To_out + Q_at_outlet * Reswall,
            Tf_out - Ti_out + Q_at_outlet * Resfouling
        ]

    f.append(m - m_)

    out = np.array(f)

    # print(np.sum(out**2))

    return out


def calculate_results(x, m, Tvap, Tin, Pin, Pvap, fNtub, Rows, tubes_per_width, kf, kwall, ep, L, Df, Do, Di, Ca=1, Alc=1, pH=1):

    Pout = x[0]
    Tout = np.ones(Rows)
    Tf_in = np.ones(Rows)
    Tf_out = np.ones(Rows)
    Ti_in = np.ones(Rows)
    Ti_out = np.ones(Rows)
    To_in = np.ones(Rows)
    To_out = np.ones(Rows)
    m_tube = np.ones(Rows)
    for i in range(0, Rows):
        Tout[i], Tf_in[i], Tf_out[i], Ti_in[i], Ti_out[i], To_in[i], To_out[i], m_tube[i] = x[(8 * i + 1):(
                    8 * (i + 1) + 1)]

    results = []

    for i in range(0, Rows):

        Tm = 0.5 * (Tin + Tout[i])
        Tf = 0.5 * (Tf_in[i] + Tf_out[i])
        Ti = 0.5 * (Ti_in[i] + Ti_out[i])
        To = 0.5 * (To_in[i] + To_out[i])

        #### FOULING RESISTANCE
        Resfouling = calculate_fouling(Di, Df, kf, L)

        #### WALL RESISTANCE
        Reswall = calculate_wall(Do, Di, kwall, L)

        #### EXTERNAL RESISTANCE
        hext, Resext, exhaust_vaporization_heat = calculate_ext(Tvap, Pvap, To, fNtub[i], L, Do)

        #### INTERNAL RESISTANCE

        hint, Resint, cp, Pout_, fD_tube, pressure_loss_in_tube, v, Re_tube, rho, mu = calculate_int(
            Tin, Tout[i], Pin, Pout, m_tube[i], ep, Df, L, Di
        )

        # Calculate Overall he
        Restotal = Resext + Resint + Reswall + Resfouling  # W/K

        UA = 1 / Restotal  # W/K

        # Calculate LMTD
        LMTD = calculate_LMTD(Tvap, Tin, Tvap, Tout[i])
        Q = calculate_heat_via_LMTD(UA, LMTD)

        # Fouling
        dmfdt, phid, phir = fouling(Tm, v, rho, mu, Df, Ca, Alc, pH)

        results.append({
            "UA": UA,
            "LMTD": LMTD,
            "Q": Q,
            "hint": hint,
            "hext": hext,
            "Restotal": Restotal,  # W/K
            "Resint": Resint,  # W/K
            "Resext": Resext,  # W/K
            "Reswall": Reswall,  # W/K
            "Resfouling": Resfouling,  # W/K
            "Tf_in": Tf_in[i],
            "Ti_in": Ti_in[i],
            "To_in": To_in[i],
            "Tf_out": Tf_out[i],
            "Ti_out": Ti_out[i],
            "To_out": To_out[i],
            "Tf": Tf,
            "Ti": Ti,
            "To": To,
            "Tin": Tin,
            "Tout": Tout[i],
            "Pin": Pin,
            "Pout": Pout,
            "Df": Df,
            "Pout": Pout,
            "v": v,
            "Re": Re_tube,
            "m_tube": m_tube[i],
            "kvap": Q / exhaust_vaporization_heat * tubes_per_width,
            "dmfdt": dmfdt,
            "phid": phid,
            "phir": phir,

        })

        if i in (0, Rows - 1):
            print("")
            print(" -- ROW {} --".format(i))

            results_i = results[i]

            print("Restotal is {number:.{digits}f} W/(K)".format(number=results_i["Restotal"], digits=6))
            print("The row external convection coefficient is {number:.{digits}f} W/(K*m2)".format(
                number=results_i["hext"], digits=2))
            print("The row internal convection coefficient is {number:.{digits}f} W/(K*m2)".format(
                number=results_i["hint"], digits=2))

            print("The last row calculated internal resistance x length is {number:.{digits}f} K/W".format(
                number=results_i["Resint"], digits=6))
            print("The last row calculated external resistance x length is {number:.{digits}f} K/W".format(
                number=results_i["Resext"], digits=6))
            print("LMTD is {number:.{digits}f} K".format(number=results_i["LMTD"], digits=2))
            print("The heat rate per tube is {number:.{digits}f} W".format(number=results_i["Q"], digits=2))
            print("U*A per tube is {number:.{digits}f} W/K".format(number=results_i["UA"], digits=2))

            print("Reswall is {number:.{digits}f} K/W".format(number=results_i["Reswall"], digits=6))
            print("Resint is {number:.{digits}f} K/W".format(number=results_i["Resint"], digits=6))
            print("Resext is {number:.{digits}f} K/W".format(number=results_i["Resext"], digits=6))

            print("Tf is {number:.{digits}f} K".format(number=results_i["Tf"], digits=2))
            print("Ti is {number:.{digits}f} K".format(number=results_i["Ti"], digits=2))
            print("To is {number:.{digits}f} K".format(number=results_i["To"], digits=2))
            print("Tvap is {number:.{digits}f} K".format(number=Tvap, digits=2))
            print("Cooling water inlet temperature is {number:.{digits}f} K".format(number=Tin, digits=2))
            print("Cooling water outlet temperature is {number:.{digits}f} W/K".format(number=results_i["Tout"],
                                                                                       digits=2))

            print("Water mean velocity is {number:.{digits}f} m/s.".format(number=results_i["v"], digits=2))
            print("Inlet Pressure is {number:.{digits}f} Pa.".format(number=results_i["Pin"], digits=2))
            print("Outlet Pressure : ", results_i["Pout"])
            print("Tube mass flowrate (kg/s) : ", results_i["m_tube"])
            print("ResFouling (K/W) : ", results_i["Resfouling"])
            print("dmfdt (kg/m2day) : ", results_i["dmfdt"])

    return results


def solve(x0, *args):
    sol = root(fun, x0, args=args)
    return sol.x

