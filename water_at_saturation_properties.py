from iapws.iapws97 import _Region4, _Region1, _Region2
from iapws._iapws import _ThCond, _Viscosity
import numpy as np
import inspect


c_dict = {'conductivity': np.array([3.20875162e-01, -6.91454761e-07, 6.24672812e-12, -2.71195484e-17,
                                    2.96320329e-02, 5.13558596e+00]),
          'density': np.array([1.01836874e+03, -6.74336724e-04, 6.06149751e-09, -2.58678900e-14,
                               -2.25901488e+00, 1.82321986e+00]),
          'enthalpy': np.array([-6.08505954e+05, 1.94062497e+00, -1.68186492e-05, 7.06340277e-11,
                                6.43850329e+04, 1.88345119e+01]),
          'heat_capacity': np.array([4.22512004e+03, 1.88493270e-03, -1.78694338e-08, 7.96209770e-14,
                                     -1.44442248e+01, 8.41137683e-03]),
          'saturation_temperature': np.array([2.48404503e+02, 4.67253143e-04, -4.09934326e-09, 1.72548088e-14,
                                              1.53833719e+01, 7.37059350e-03]),
          'vaporization_enthalpy': np.array([2.96216663e+06, -1.20540634e+00, 9.85003104e-06, -4.10994887e-11,
                                             -3.61781700e+04, 5.09057715e+02]),
          'vapour_density': np.array([2.37652486e-03, 6.65298567e-06, -1.31408942e-11, 5.49191279e-17]),
          'vapour_total_compressibility': np.array([6.65298567e-06, -2.62817883e-11, 1.64757384e-16]),
          'viscosity': np.array([5.17865934e-03, 2.55434669e-08, -3.01011890e-13, 1.39267038e-18,
                                 -4.25522968e-04, 8.56155473e+00])}


def simplified_model(x,c=None):

    if c is None:
        c = c_dict[inspect.stack()[1][3]]

    f = 0.

    if c.shape[0] == 4:
        for i in range(c.shape[0]):
            f += c[i] * (x ** i)
    else:
        for i in range(c.shape[0] - 2):
            f += c[i] * (x ** i)
        f += c[-2] * np.log(c[-1] * x)

    return f


def calculate_saturation_temperature(P):

    P = P*1e-6
    out = _Region4(P, 0.)

    return out['T']


def vapour_total_compressibility(P):

    return simplified_model(P)


def vaporization_enthalpy(P, simplified = False):

    if simplified:

        return simplified_model(P, c=c_dict['vaporization_enthalpy'])


    T = calculate_saturation_temperature(P)

    P = P*1e-6

    v = _Region2(T, P)
    l = _Region1(T, P)

    return 1e3 * (v['h'] - l['h'])


def density(P, simplified = False):

    if simplified:

        return simplified_model(P, c=c_dict['density'])


    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)

    v = out['v']

    rho = 1 / v # kg/m3

    return rho


def vapour_density(P, simplified = False):

    if simplified:

        return simplified_model(P, c=c_dict['vapour_density'])


    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region2(T, P)

    v = out['v']

    rho = 1 / v # kg/m3

    return rho


def enthalpy(P, simplified = False):

    if simplified:

        return simplified_model(P, c=c_dict['enthalpy'])

    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)
    h = 1e3 * out['h']

    return h


def enthalpy_vapour(P, simplified = False):

    if simplified:

        return simplified_model(P, c=c_dict['enthalpy_vapour'])

    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)
    h = 1e3 * out['h']

    return h


def heat_capacity(P, simplified = False):

    if simplified:

        return simplified_model(P, c=c_dict['heat_capacity'])

    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)
    cp = 1e3 * out['cp']

    return cp



def conductivity(P, simplified = False):

    if simplified:

        return simplified_model(P, c=c_dict['conductivity'])

    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)
    T = out['T']
    v = out['v']

    rho = 1 / v

    return _ThCond(rho, T)


def viscosity(P, simplified = False):

    if simplified:

        return simplified_model(P, c=c_dict['viscosity'])

    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)
    T = out['T']
    v = out['v']

    rho = 1 / v

    return _Viscosity(rho, T)


def saturation_temperature(P, simplified = False):

    if simplified:

        return simplified_model(P, c=c_dict['saturation_temperature'])

    return calculate_saturation_temperature(P)
