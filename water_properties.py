from iapws.iapws97 import _Region1, _TSat_P
from iapws._iapws import _ThCond, _Viscosity
import numpy as np
import inspect


c_dict = {'conductivity': np.array([[-7.82942581e-01,  7.51176144e-09, -2.80953450e-17],
           [ 7.66718213e-03, -4.25398696e-11,  1.61930300e-19],
           [-1.00913840e-05,  6.46458388e-14, -2.37494994e-22]]),
     'density': np.array([[ 7.34932166e+02,  3.00114904e-06, -1.03284845e-13],
           [ 2.00946864e+00, -1.57558559e-08,  6.55299865e-16],
           [-3.79375187e-03,  2.41680119e-11, -1.03916779e-18]]),
     'enthalpy': np.array([[-1.14300669e+06,  2.76932708e-03, -1.65617505e-11],
           [ 4.18741376e+03, -9.41078372e-06,  9.47294517e-14],
           [-7.66664890e-03,  1.08497737e-08, -1.36786265e-16]]),
     'heat_capacity': np.array([[ 5.66685353e+03, -6.55474142e-05, -1.26388806e-13],
           [-9.38832563e+00,  3.76870350e-07,  9.99815092e-16],
           [ 1.48029878e-02, -5.60190728e-10, -1.79692966e-18]]),
     'viscosity': np.array([[ 2.64395831e-02, -5.33641016e-11,  4.29013822e-19],
           [-1.49875404e-04,  3.22989760e-13, -2.65882055e-21],
           [ 2.15632416e-07, -4.85829663e-16,  4.11084517e-24]])}



def simplified_model(x, y, c=None):

    if c is None:
        c = c_dict[inspect.stack()[1][3]]

    f = 0.

    for i in range(c.shape[0]):

        for j in range(c.shape[1]):
            f += c[i][j] * (x ** i) * (y ** j)

    return f


def saturation_temperature(P):

    P = P*1e-6

    T = _TSat_P(P)

    if T > 623.15:

        return None

    else:

        return T


def density(T, P, simplified = False):

    if simplified:
        return simplified_model(T, P, c=c_dict['density'])

    P = P*1e-6

    v = _Region1(T, P)['v']
    alfav = _Region1(T, P)['alfav']
    kt = _Region1(T, P)['kt']

    rho = 1 / v # kg/m3
    drhodT = -alfav / v  # kg/m3K
    drhodP = kt / v * 1e-6 # kg/m3Pa

    return rho, drhodT, drhodP


def enthalpy(T, P, simplified = False):

    if simplified:

        return simplified_model(T, P, c=c_dict['enthalpy'])

    P = P*1e-6
    h = 1e+3 * _Region1(T, P)['h']
    cp = 1e+3 * _Region1(T, P)['cp']
    v = _Region1(T, P)['v']
    alfav = _Region1(T, P)['alfav']

    dvdT = alfav * v

    dhdP = v - T * dvdT
    dhdT = cp

    return h, dhdT, dhdP


def heat_capacity(T, P, simplified = False):

    if simplified:

        return simplified_model(T, P, c=c_dict['heat_capacity'])

    P = P*1e-6
    cp = 1e+3 * _Region1(T, P)['cp']

    return cp, 0, 0


def conductivity(T, P, simplified = False):

    if simplified:

        return simplified_model(T, P, c=c_dict['conductivity'])

    P = P*1e-6

    v = _Region1(T, P)['v']

    rho = 1 / v

    return _ThCond(rho, T), 0, 0


def viscosity(T, P, simplified = False):

    if simplified:

        return simplified_model(T, P, c=c_dict['viscosity'])

    P = P*1e-6

    v = _Region1(T, P)['v']

    rho = 1 / v

    return _Viscosity(rho, T), 0, 0

