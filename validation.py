from simulate import main

cases = [
    # {'name': "colesoncove_pre",
    #  'input': "notebooks/colesoncove_pre.json",
    #  'output': "notebooks/colesoncove_pre.out.json",
    #  "reporting_interval": 1,
    #  "time_horizon": 1,
    #  "relative_tolerance": 1e-3,
    #  "MaxStep": 1,
    #  "MaxNumSteps": 1000000,
    #  },
    {'name': "colesoncove",
     'input': "notebooks/colesoncove.json",
     'output': "notebooks/colesoncove.out.json",
     'initial_condition': "notebooks/colesoncove_pre.out.json",
     "reporting_interval": 1,
     "time_horizon": 1,
     "relative_tolerance": 1e-3,
     "MaxStep": 1,
     "MaxNumSteps": 1000000,
     },
]



if __name__ == "__main__":
    for case in cases:
        main( **case )
