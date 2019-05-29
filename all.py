# CELLDEPOSIT-CONDENSER Project
#
# Author: Jaime Souza
#
# This code is part of the publication:
#   Graph-based network modeling and simulation of condensers in once-through cooling water system under the effect of
#   biofouling formation
#
# This code aims to run a certain simulation in order to produce the results for this study
#
# How to use?
#
#     Define the index of the simulation that needs to be executed, for exemplo, 5, and:
#
#     >>> python all.py "0,1,2,3"
#
#     To run all the cases:
#
#     >>> python all.py

# Importing modules
import sys
import simulate
import os.path

# All cases considered in thi publication
cases = [

    #{'input': "cases/3/scenario_shortterm/model_simplified/bc_pump/preparation.json"},

    {'input': "cases/3/scenario_shortterm/model_complete/bc_wfixed/preparation.json"},

    {'input': "cases/3/scenario_shortterm/model_complete/bc_pump/preparation.json"},

    #{'input': "cases/3/scenario_shortterm/model_simplified/bc_pump/simulation.json",
    # "initial_condition": "cases/3/scenario_shortterm/model_simplified/bc_pump/preparation.output.json"},

    #{'input': "cases/3/scenario_shortterm/model_complete/bc_wfixed/simulation.json",
    # "initial_condition": "cases/3/scenario_shortterm/model_complete/bc_wfixed/preparation.output.json"},

    {'input': "cases/3/scenario_shortterm/model_complete/bc_pump/simulation.json",
     "initial_condition": "cases/3/scenario_shortterm/model_complete/bc_pump/preparation.output.json"},

    {'input': "cases/3/scenario_shortterm/model_complete/bc_pump/simulationwithoutbiofilm.json",
     "initial_condition": "cases/3/scenario_shortterm/model_complete/bc_pump/preparation.output.json"},

]

try:
    ind = list(map(int, sys.argv[1].strip("\"").strip("\'").split(",")))
except:
    ind = range(0, len(cases))

for i in ind:

    # Collecting case data
    try:
        case = cases[i]
    except:
        print("Case {} not found".format(i))

    # Running
    print("Starting case {}".format(case))

    # Completing data
    if 'initial_condition' not in case:
        case['initial_condition'] = ""
    filename = case["input"]
    directory = os.path.dirname(filename)
    if case['initial_condition'] == -1:
        initial_condition_file = os.path.join(directory, "preparation.output.json")
        if os.path.isfile(initial_condition_file):
            case['initial_condition'] = initial_condition_file

    # Simulating
    try:
        simulate.main(
            input=case['input'],
            format='json',
            initial_condition=case['initial_condition'],
            output='',
            name=''
        )
    except:
        print("Not converged")

    print("End")

    # end
