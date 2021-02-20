import random
import json
import simulate
import time
import os

filename = "navajo"
suffix = "mc"

with open("notebooks/{}_{}_pumped.json".format(filename, "cs")) as f:
    json_data = f.read()
data = json.loads(json_data)

output_mc = []
for i in range(1000):

    Alci = data["condenser"]["parameters"]["Alc"] * (1 + random.gauss(0, 0.02))
    pHi = data["condenser"]["parameters"]["pH"] * (1 + random.gauss(0, 0.02))
    Cai = data["condenser"]["parameters"]["Ca"] * (1 + random.gauss(0, 0.02))

    id = round(time.time())
    print("Montecarlo ID {} for Alc {}, pH {} and Ca {}".format(id, Alci, pHi, Cai))

    data_mc = data.copy()

    data_mc["condenser"]["parameters"].update({
        "Alc": Alci,
        "pH": pHi,
        "Ca": Cai,
    })

    with open("mc/{}_{}_pumped.json".format(filename, suffix), 'w') as outfile:
        json.dump(data_mc, outfile, indent=4)

    output_filename = "mc/{}_{}_pumped_{}.out.json".format(filename, suffix, id)

    simulate.main(
        name=filename,
        input="mc/{}_{}_pumped.json".format(filename, suffix),
        output=output_filename,
        initial_condition="notebooks/{}_{}_fixedW.out.json".format(filename, "cs"),
        init="notebooks/{}_{}_fixedW.out.json.init".format(filename, "cs"),
        reporting_interval=25 * 24 * 3600,
        time_horizon=1000 * 24 * 3600,
        relative_tolerance=1e-3,
        MaxStep=10 * 24 * 3600,
        MaxNumSteps=100,
    )
    os.remove(output_filename+".init")
    with open(output_filename) as f:
        json_data = f.read()

    output = json.loads(json_data)
    output2 = output.copy()

    for key in output.keys():
        if key in ("condenser.Rf","condenser.Alc","condenser.Ca","condenser.pH","condenser.T", "condenser.k", "condenser.v", "condenser.P", "condenser.Text", "condenser.Pext"):
            continue
        if key.startswith("node_C"):
            continue
        del(output2[key])

    with open(output_filename, 'w') as outfile:
        json.dump(output2, outfile)
