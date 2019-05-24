import json
import numpy as np


def get_list(x0, x1, Nelements, Ntubes):
    return np.reshape(np.repeat(np.linspace(x0, x1, Nelements), Ntubes), (Nelements, Ntubes)).tolist()


def json_node_inlet(pressure, temperature, flowrate):
    return {
        "kind": "node",
        "module": "models.source",
        "class": "Source",
        "specifications": {
            "P": "initial_guess.P",
        },
        "parameters": {
            "Text": temperature,
            "Pext": pressure,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        },
        "initial_guess": {
            "w": flowrate,
            "P": pressure,
            "T": temperature

        }
    }


def json_node_outlet(pressure, temperature, flowrate):
    return {
        "kind": "node",
        "module": "models.sink",
        "class": "Sink",
        "specifications": {
            "P": pressure,
        },
        "parameters": {
            "Text": temperature,
            "Pext": pressure,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        },
        "initial_guess": {
            "w": flowrate,
            "P": pressure,
            "T": temperature
        }
    }


def json_node_pumped(pressure, temperature, flowrate, A, B, C):
    return {
        "kind": "node",
        "module": "models.pumped_source_secondorder",
        "class": "PumpedSource",
        "specifications": {
        },
        "parameters": {
            "Text": temperature,
            "Pext": pressure,
            "x": 0.0,
            "y": 1.0,
            "z": 0.0,
            "A": A,
            "B": B,
            "C": C,
        },
        "initial_guess": {
            "w": flowrate,
            "P": pressure,
            "T": temperature
        }
    }

def json_node_river(pressure, temperature, flowrate, A, B, C, alpha1, alpha2, tau, stnRiverTemperature):
    return {
        "kind": "node",
        "module": "models.river_source",
        "class": "RiverSource",
        "specifications": {
        },
        "states": {
            'stnRiverTemperature': stnRiverTemperature,
        },
        "parameters": {
            "Text0": temperature,
            "Pext": pressure,
            "x": 0.0,
            "y": 1.0,
            "z": 0.0,
            "A": A,
            "B": B,
            "C": C,
            "alpha1": alpha1,
            "alpha2": alpha2,
            "tau": tau,
        },
        "initial_guess": {
            "w": flowrate,
            "P": pressure,
            "T": temperature
        }
    }



def json_node_wfix(pressure, temperature, flowrate):
    return {
        "kind": "node",
        "module": "models.source",
        "class": "Source",
        "specifications": {
            "w": flowrate
        },
        "parameters": {
            "Text": temperature,
            "Pext": pressure,
            "x": 0.0,
            "y": 1.0,
            "z": 0.0
        },
        "initial_guess": {
            "w": flowrate,
            "P": pressure,
            "T": temperature
        }
    }


def json_node_wpfix(pressure, temperature, flowrate):
    return {
        "kind": "node",
        "module": "models.source",
        "class": "Source",
        "specifications": {
            "w": flowrate,
            "P": pressure,
        },
        "parameters": {
            "Text": temperature,
            "Pext": pressure,
            "x": 0.0,
            "y": 1.0,
            "z": 0.0
        },
        "initial_guess": {
            "w": flowrate,
            "P": pressure,
            "T": temperature
        }
    }


def json_node_Nonefix(pressure, temperature, flowrate):
    return {
        "kind": "node",
        "module": "models.source",
        "class": "Source",
        "specifications": {
        },
        "parameters": {
            "Text": temperature,
            "Pext": pressure,
            "x": 0.0,
            "y": 1.0,
            "z": 0.0
        },
        "initial_guess": {
            "w": flowrate,
            "P": pressure,
            "T": temperature
        }
    }


def json_condenser_complete(from_,
                   to_,
                   Nelements,
                   Ntubes,
                   Npipes,
                   Di,
                   Do,
                   kwall,
                   L,
                   ep,
                   water_flowrate_per_tube,
                   water_inlet_temperature, water_outlet_temperature,
                   water_inlet_pressure, water_outlet_pressure,
                   temperature_external_surface_at_intlet, temperature_external_surface_at_outlet,
                   temperature_internal_surface_at_inlet, temperature_internal_surface_at_outlet,
                   Re_tube, water_desired_speed,
                   fD_tube, hint, hext_list,
                   external_volume,
                   Pext0,
                   PextH,
                   PextSP,
                   steam_mass_flowrate,
                   fNtub,
                   exhaust_steam_pressure,
                   exhaust_steam_temperature,
                   rhomf, Ccell, Csubstrate, lagt, stnShellPressure, vbf0, Tbf0,
                   Q_at_inlet, Q_at_outlet
                   ):
    return {
        "kind": "edge",
        "module": "models.carbfilmed_external_film_cond_tube_arrange",
        "class": "CarbfilmedExternalFilmCondensationTubeArrange",
        "from": from_,
        "to": to_,
        "domains": {
            "x": {
                "initial": 0.0,
                "final": 1.0,
                "N": Nelements
            },
            "y": {
                "N": Ntubes
            }
        },
        'constants': {
            'lagt': lagt,
        },
        "states": {
            'stnRegulator': 'Closed',
            'stnShellPressure': stnShellPressure

        },
        "parameters": {
            "Di": Di,
            "Do": Do,
            "kwall": kwall,
            "tetha": 0.0,
            "L": L,
            "epw": ep,
            "Klb": 0.9 / 2,
            "Kub": 0.9 / 2,
            "Npipes": list(Npipes * np.ones((Ntubes,))),
            "fNtub": fNtub.tolist(),
            "Vext": external_volume,
            "Pext0": "initial_guess.Pext",
            "PextH": PextH,
            "PextSP": PextSP,
            "kvap": "initial_guess.kcond",
            "mfi": 1e-06,
        },
        "specifications": {},
        "initial_guess": {
            "ep": ep,
            "Pext": exhaust_steam_pressure,
            "Text": exhaust_steam_temperature,
            "Re": Re_tube,
            "D": Di - 1e-6,
            "v": water_desired_speed,
            "k": water_flowrate_per_tube,
            "T": get_list(water_inlet_temperature, water_outlet_temperature, Nelements, Ntubes),
            "P": get_list(water_inlet_pressure, water_outlet_pressure, Nelements, Ntubes),
            "Qout": get_list(Q_at_inlet / L, Q_at_outlet / L, Nelements, Ntubes),
            "To": get_list(temperature_external_surface_at_intlet, temperature_external_surface_at_outlet, Nelements,
                           Ntubes),
            "Ti": get_list(temperature_internal_surface_at_inlet, temperature_internal_surface_at_outlet, Nelements,
                           Ntubes),
            "fD": fD_tube,
            "hint": hint,
            "hext": hext_list.tolist(),
            "kcond": steam_mass_flowrate
        }
    }


def json_condenser_simplified(from_,
                              to_,
                              Nelements,
                              Ntubes,
                              Npipes,
                              Di,
                              Do,
                              kwall,
                              L,
                              ep,
                              water_flowrate_per_tube,
                              water_inlet_temperature, water_outlet_temperature,
                              water_inlet_pressure, water_outlet_pressure,
                              temperature_external_surface_at_intlet, temperature_external_surface_at_outlet,
                              temperature_internal_surface_at_inlet, temperature_internal_surface_at_outlet,
                              Re_tube, water_desired_speed,
                              fD_tube, hint, hext_list,
                              external_volume,
                              Pext0,
                              PextH,
                              PextSP,
                              steam_mass_flowrate,
                              fNtub,
                              exhaust_steam_pressure,
                              exhaust_steam_temperature,
                              rhomf, Ccell, Csubstrate, lagt, stnShellPressure, vbf0, Tbf0,
                              Q_at_inlet, Q_at_outlet
                              ):
    return {
        "kind": "edge",
        "module": "models.simplified_carbfilmed_external_film_cond_tube_arrange",
        "class": "SimpCarbfilmedExternalFilmCondensationTubeArrange",
        "from": from_,
        "to": to_,
        "domains": {
            "x": {
                "initial": 0.0,
                "final": 1.0,
                "N": Nelements
            },
            "y": {
                "N": Ntubes
            }
        },
        'constants': {
            'lagt': lagt,
        },
        "states": {
            'stnRegulator': 'Closed',
            'stnShellPressure': stnShellPressure

        },
        "parameters": {
            "Di": Di,
            "Do": Do,
            "kwall": kwall,
            "tetha": 0.0,
            "L": L,
            "epw": ep,
            "Klb": 0.9 / 2,
            "Kub": 0.9 / 2,
            "Npipes": list(Npipes * np.ones((Ntubes,))),
            "fNtub": fNtub.tolist(),
            "Vext": external_volume,
            "Pext0": exhaust_steam_pressure,

            # "Pext0": "initial_guess.Pext",

            "PextH": PextH,
            "PextSP": PextSP,
            "kvap": steam_mass_flowrate,

            # "kvap": "initial_guess.kcond",

            "mfi": 1e-06,
            "vbf0": vbf0,
            "Tbf0": Tbf0,
        },
        "specifications": {},
        "initial_guess": {
            "ep": ep,
            "Pext": exhaust_steam_pressure,
            "Text": exhaust_steam_temperature,
            "Re": Re_tube,
            "D": Di - 1e-6,
            "v": water_desired_speed,
            "k": water_flowrate_per_tube,
            "T": get_list(water_inlet_temperature, water_outlet_temperature, Nelements, Ntubes),
            "P": get_list(water_inlet_pressure, water_outlet_pressure, Nelements, Ntubes),
            "Qout": get_list(Q_at_inlet / L, Q_at_outlet / L, Nelements, Ntubes),
            "To": get_list(temperature_external_surface_at_intlet, temperature_external_surface_at_outlet, Nelements,
                           Ntubes),
            "Ti": get_list(temperature_internal_surface_at_inlet, temperature_internal_surface_at_outlet, Nelements,
                           Ntubes),
            "fD": fD_tube,
            "hint": hint,
            "hext": hext_list.tolist(),
            "kcond": steam_mass_flowrate
        }
    }


def json_pipe_dirty(from_, to_, Nelements, Di, L, ep, Klb, Kub, Re, v, k, T, P1, P2, fD, rhomf, Ccell, Csubstrate,
                    lagt):
    return {
        "kind": "edge",
        "module": "models.carbfilmed_pipe",
        "class": "CarbfilmedPipe",
        "from": from_,
        "to": to_,
        "domains": {
            "x": {
                "initial": 0.0,
                "final": 1.0,
                "N": Nelements
            }
        },
        'constants': {
            'lagt': lagt,
        },
        "states": {},
        "parameters": {
            "Di": Di,
            "tetha": 0.0,
            "L": L,
            "epw": ep,
            "Klb": Klb,
            "Kub": Kub,
            "Npipes": 1.0,
            "mfi": 1e-06,
        },
        "specifications": {},
        "initial_guess": {
            "ep": ep,
            "Re": Re,
            "D": Di,
            "v": v,
            "k": k,
            "T": T,
            "P": np.linspace(P1, P2, Nelements).tolist(),
            "fD": fD,
        }
    }


def json_pipe(from_, to_, Nelements, Di, L, ep, Klb, Kub, Re, v, k, T, P1, P2, fD):
    return {
        "kind": "edge",
        "module": "models.pipe",
        "class": "Pipe",
        "from": from_,
        "to": to_,
        "domains": {
            "x": {
                "initial": 0.0,
                "final": 1.0,
                "N": Nelements
            }
        },
        "states": {},
        "parameters": {
            "Di": Di,
            "tetha": 0.0,
            "L": L,
            "epw": ep,
            "Klb": Klb,
            "Kub": Kub,
            "Npipes": 1.0,

        },
        "specifications": {},
        "initial_guess": {
            "ep": ep,
            "Re": Re,
            "D": Di,
            "v": v,
            "k": k,
            "T": T,
            "P": np.linspace(P1, P2, Nelements).tolist(),
            "fD": fD,
        }
    }


