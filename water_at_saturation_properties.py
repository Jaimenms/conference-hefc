from iapws.iapws97 import _Region4, _Region1, _Region2
from iapws._iapws import _ThCond, _Viscosity
import numpy as np
import inspect

def simple_model_parameters():

    c_dict = {
        'conductivity': np.array([ 6.20940155e-01,  1.90022194e-06, -2.45476728e-11,  1.12611502e-16]),
        'density': np.array([ 9.96906358e+02, -8.11519963e-04,  7.28615211e-09, -3.02080951e-14]),
        'enthalpy': np.array([ 1.31488947e+05,  7.28807358e+00, -7.84449119e-05,  3.44521411e-10]),
        'heat_capacity': np.array([ 4.17429701e+03,  4.31727962e-04,  7.44863129e-10, -8.92950974e-15]),
        'saturation_temperature': np.array([ 3.04528132e+02,  1.74387838e-03, -1.88042391e-08,  8.25850104e-14]),
        'vapour_density': np.array([ 4.62513512e-03,  6.47401547e-06, -9.47682219e-12,  3.32572527e-17]),
        'vapour_total_compressibility': np.array([ 6.47401547e-06, -1.89536444e-11,  9.97717582e-17]),
        'viscosity': np.array([ 6.97318785e-04, -1.47128076e-08,  1.98579652e-13, -9.38312502e-19]),
        'vaporization_enthalpy': np.array([2.42706159e+06, -4.20868251e+00, 4.44518182e-05, -1.94852702e-10]),
    }

    return c_dict


def simplified_model(x,):

    c_dict = simple_model_parameters()

    c = c_dict[inspect.stack()[1][3]]

    f = 0.

    for i in range(c.shape[0]):
        f += c[i] * (x ** i)

    return f


def calculate_saturation_temperature(P):

    P = P*1e-6
    out = _Region4(P, 0.)

    return out['T']


def vapour_total_compressibility(P):

    return simplified_model(P)



def vaporization_enthalpy(P, simplified = False):

    if simplified:

        return simplified_model(P)


    T = calculate_saturation_temperature(P)

    P = P*1e-6

    v = _Region2(T, P)
    l = _Region1(T, P)

    return 1e3 * (v['h'] - l['h'])


def density(P, simplified = False):

    if simplified:

        return simplified_model(P)


    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)

    v = out['v']

    rho = 1 / v # kg/m3

    return rho


def vapour_density(P, simplified = False):

    if simplified:

        return simplified_model(P)


    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region2(T, P)

    v = out['v']

    rho = 1 / v # kg/m3

    return rho


def enthalpy(P, simplified = False):

    if simplified:

        return simplified_model(P)

    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)
    h = 1e3 * out['h']

    return h


def enthalpy_vapour(P, simplified = False):

    if simplified:

        return simplified_model(P)

    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)
    h = 1e3 * out['h']

    return h


def heat_capacity(P, simplified = False):

    if simplified:

        return simplified_model(P)

    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)
    cp = 1e3 * out['cp']

    return cp



def conductivity(P, simplified = False):

    if simplified:

        return simplified_model(P)

    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)
    T = out['T']
    v = out['v']

    rho = 1 / v

    return _ThCond(rho, T)


def viscosity(P, simplified = False):

    if simplified:

        return simplified_model(P)

    T = calculate_saturation_temperature(P)

    P = P*1e-6
    out = _Region1(T, P)
    T = out['T']
    v = out['v']

    rho = 1 / v

    return _Viscosity(rho, T)


def saturation_temperature(P, simplified = False):

    if simplified:

        return simplified_model(P)

    return calculate_saturation_temperature(P)
