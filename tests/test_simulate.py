import unittest
import json
import os
from simulate import execute

class TestSimulate(unittest.TestCase):

    def test_01(self):

        data = {"name": "test",
                "simulation_parameters": {
                    "name": "test",
                    "reporting_interval": 0,
                    "initial_condition": "",
                    "time_horizon": 10,
                    "relative_tolerance": 0.000001,
                    "MaxStep": 1,
                    "MaxNumSteps": 1000000000,
                    "format": "json",
                },
                "class": "Network",
                "submodels": {
                    "node_A": {
                        "kind": "node",
                        "module": "models.source",
                        "class": "Source",
                        "specifications": {
                            "w": 224.44564654203782
                        },
                        "parameters": {
                            "Text": 286.95,
                            "Pext": 119742.12132707184,
                            "x": 0.0,
                            "y": 1.0,
                            "z": 0.0
                        },
                        "initial_guess": {
                            "w": 224.44564654203782,
                            "P": 119742.12132707184,
                            "T": 286.95
                        }
                    },
                    "pipe_1": {
                        "kind": "edge",
                        "module": "models.pipe",
                        "class": "Pipe",
                        "from": "node_A",
                        "to": "node_B",
                        "domains": {
                            "x": {
                                "initial": 0.0,
                                "final": 1.0,
                                "N": 10
                            }
                        },
                        "states": {},
                        "parameters": {
                            "Di": 0.35559999999999997,
                            "tetha": 0.0,
                            "L": 50.0,
                            "epw": 4.5e-05,
                            "Klb": 0.0,
                            "Kub": 1.1,
                            "Npipes": 1.0
                        },
                        "specifications": {},
                        "initial_guess": {
                            "ep": 4.5e-05,
                            "Re": 941310.0900539967,
                            "D": 0.35559999999999997,
                            "v": 2.2677514105028203,
                            "k": 224.44564654203782,
                            "T": 286.95,
                            "fD": 0.013944952017407693
                        }
                    },
                    "node_B": {
                        "kind": "node",
                        "module": "models.sink",
                        "class": "Sink",
                        "specifications": {
                            "P": "initial_guess.P"
                        },
                        "parameters": {
                            "Text": 286.95,
                            "Pext": 100000,
                            "x": 0.0,
                            "y": 0.0,
                            "z": 0.0
                        },
                        "initial_guess": {
                            "w": 224.44564654203782,
                            "P": 111898.92540354044,
                            "T": 286.95
                        }
                    },

                }, }

        self.runner(data)

    def test_02(self):
        data = {"name": "test",
                "simulation_parameters": {
                    "name": "test",
                    "reporting_interval": 0,
                    "initial_condition": "",
                    "time_horizon": 10,
                    "relative_tolerance": 0.000001,
                    "MaxStep": 1,
                    "MaxNumSteps": 1000000000,
                    "format": "json",
                },
                "class": "Network",
                "submodels": {
                    "node_A": {
                        "kind": "node",
                        "module": "models.source",
                        "class": "Source",
                        "specifications": {
                            "w": 224.44564654203782
                        },
                        "parameters": {
                            "Text": 286.95,
                            "Pext": 119742.12132707184,
                            "x": 0.0,
                            "y": 1.0,
                            "z": 0.0
                        },
                        "initial_guess": {
                            "w": 224.44564654203782,
                            "P": 119742.12132707184,
                            "T": 286.95
                        }
                    },
                    "pipe_1": {
                        "kind": "edge",
                        "module": "models.carbfilmed_pipe",
                        "class": "CarbfilmedPipe",
                        "from": "node_A",
                        "to": "node_B",
                        "domains": {
                            "x": {
                                "initial": 0.0,
                                "final": 1.0,
                                "N": 10
                            }
                        },
                        "constants": {
                          "lagt": 1,
                        },
                        "states": {},
                        "parameters": {

                            "conc_H": 1e-7,
                            "conc_Ca": 9.55,
                            "pCO2": 0.0314/100*101325,
                            "mfi": 1e-9,

                            "Di": 0.35559999999999997,
                            "tetha": 0.0,
                            "L": 50.0,
                            "epw": 4.5e-05,
                            "Klb": 0.0,
                            "Kub": 1.1,
                            "Npipes": 1.0
                        },
                        "specifications": {},
                        "initial_guess": {

                            "mf": 1e-9,
                            "phid": 0.0,
                            "phir": 0.0,
                            "Rf": 0.0,

                            "ep": 4.5e-05,
                            "Re": 941310.0900539967,
                            "D": 0.35559999999999997,
                            "v": 2.2677514105028203,
                            "k": 224.44564654203782,
                            "T": 286.95,
                            "fD": 0.013944952017407693
                        }
                    },
                    "node_B": {
                        "kind": "node",
                        "module": "models.sink",
                        "class": "Sink",
                        "specifications": {
                            "P": "initial_guess.P"
                        },
                        "parameters": {
                            "Text": 286.95,
                            "Pext": 100000,
                            "x": 0.0,
                            "y": 0.0,
                            "z": 0.0
                        },
                        "initial_guess": {
                            "w": 224.44564654203782,
                            "P": 111898.92540354044,
                            "T": 286.95
                        }
                    },

                }, }

        self.runner(data)


    def runner(self,data):

        input_filename = os.path.abspath("./tmp/input.json")
        output_filename = os.path.abspath("./tmp/output.json")

        args = {"input": input_filename, "output": output_filename, }
        input_path = os.path.dirname(input_filename)
        if not os.path.exists(input_path):
            os.makedirs(input_path)

        with open(input_filename, 'w+') as f:
            json.dump(data, f, indent=4)

        if os.path.exists(output_filename):
            os.unlink(output_filename)

        execute(args)

        with open(output_filename) as f:
            output = json.load(f)

        self.assertAlmostEqual(output["node_A.P"]["Values"][0], 119869.94247218208)
