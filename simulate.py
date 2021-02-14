# CELLDEPOSIT-CONDENSER Project
#
# Author: Jaime Souza
#
# This code is part of the publication:
#   Graph-based network modeling and simulation of condensers in once-through cooling water system under the effect of
#   biofouling formation
#
# This code aims to dynamically simulate a network
#
# How to use?
#
#     >>> python simulate.py help
#

# Before you have to run:
# python -m daetools.dae_plotter.plotter &

# Import modules
import argparse
import json
import os

# Import Daetools
from daetools.pyDAE import *
from daetools.pyDAE.data_reporters import daeJSONFileDataReporter
from daetools.dae_plotter.data_receiver_io import pickleProcess
from models.network import Network
from daetools_extended.tools import merge_initial_condition

def loadInitFile(simulation, log):
    if simulation.init_filename is not None:
        print("Loading Initialization Values")
        simulation.LoadInitializationValues(simulation.init_filename)

def saveInitFile(simulation, log):
    print("Saving Initialization Values")
    simulation.StoreInitializationValues(simulation.output_filename + ".init")

class Simulate(daeSimulation):

    def __init__(self, name, args):

        self.input_filename = args['input']
        self.output_filename = args['output']
        if 'init' in args:
            self.init_filename = args['init']
        else:
            self.init_filename = None

        with open(args['input']) as f:
            json_data = f.read()
        input = json.loads(json_data)

        # Merge Initial Condition
        input = merge_initial_condition(args, input)

        daeSimulation.__init__(self)
        self.m = Network(name, Parent=None, Description="", data=input)

    def SetUp(self, methods):
        for method_ in methods:
            for name, obj in self.m.submodels.items():
                getattr(obj.Parent, method_)(obj)

    def SetUpVariables(self):
        self.InitialConditionMode = eQuasiSteadyState

        self.SetUp(('setup_active_states', 'setup_variables', 'setup_initial_guess'))

    def SetUpParametersAndDomains(self):
        self.SetUp(('setup_domains', 'setup_parameters',))

    def SavePickle(self, filename, dr):
        pickleProcess(dr.Process, filename)

    def run(self, args):
        self.m.SetReportingOn(args['reporting_interval']>0)
        if args['reporting_interval']>0:
            self.ReportingInterval = args['reporting_interval']

        if args['time_horizon'] > 0:
            self.TimeHorizon = args['time_horizon']

        cfg = daeGetConfig()
        cfg.SetBoolean('daetools.activity.printHeader', False)
        cfg.SetFloat('daetools.IDAS.MaxStep', args['MaxStep'])
        cfg.SetFloat('daetools.IDAS.relativeTolerance', args['relative_tolerance'])
        cfg.GetInteger('daetools.IDAS.MaxNumSteps', args['MaxNumSteps'])
        cfg.SetBoolean("daetools.IDAS.LineSearchOffIC", False)
        cfg.SetInteger("daetools.IDAS.MaxConvFails", 200)
        cfg.SetInteger("daetools.IDAS.MaxNumStepsIC", 50)
        #cfg.SetBoolean("daetools.IDAS.printInfo", True  )



        solver = daeIDAS()
        solver.RelativeTolerance = args['relative_tolerance']

        # Initialize
        dr = daeJSONFileDataReporter()
        dr.Connect(args['output'], args["name"])
        daeActivity.simulate(self,
                             reportingInterval=args["reporting_interval"],
                             timeHorizon=args["time_horizon"],
                             datareporter=dr,
                             run_after_simulation_init_fn=loadInitFile,
                             run_before_simulation_fn=saveInitFile,
                             )

        print("Number of equations", self.NumberOfEquations)
        # print("Number of variables", self.TotalNumberOfVariables)
        self.m.SaveModelReport('{0}.model.xml'.format(args["input"], ))
        self.m.SaveModelReport('{0}.model-rt.xml'.format(args["input"], ))

        with open(args['output']) as f:
            json_data = f.read()
        # output = json.loads(json_data)
        # print(output)

def main(**args):

    name = args['name']
    simulate = Simulate(name, args)
    simulate.run(args)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Simulate a model according to DAETOOLS based on a json data. '
                                                 'It is necessary to have an openned dae_plotter thread before '
                                                 'executing. For that, please execute the following command:  '
                                                 'python -m daetools.dae_plotter.plotter &')
    parser.add_argument('name', help='Simulation name.')
    parser.add_argument('input', help='Path of the json input file.')
    parser.add_argument('output', help='Path of the json output file.')
    parser.add_argument('--steady_state', help='T if simulation starts with steady state.')
    parser.add_argument('--init', help='Path to initial file.')
    parser.add_argument('--initial_condition', help='Path to the initial condition file.')
    parser.add_argument('--reporting_interval', type=int, default= 3600, help='Reporting interval in seconds.')
    parser.add_argument('--time_horizon', type=int, default= 20*24*3600, help='Time horizon in seconds')
    parser.add_argument('--relative_tolerance', type=float, default= 1e-6, help='Relative tolerance for the integration '
                                                                                'method.')
    parser.add_argument('--MaxStep', type=int, default= 10., help='IDAS.MaxStep parameter.')
    parser.add_argument('--MaxNumSteps', type=int, default= 1000000, help='IDAS.MaxNumSteps parameter.')

    args = parser.parse_args()

    main(**vars(args))
