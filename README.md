# Graph-based network modeling and simulation of condensers in once-through cooling water system under the effect of biofouling formation
## Heat Exchanger Fouling and Cleaning Conference 2019

*celldeposit-condenser* This is the implementation of the "Graph-based network modeling and simulation of condensers in once-through cooling water system under the effect of biofouling formation" pape.

This paper presents the modeling and simulation of an once-through steam condenser system dominated by biofouling in order to describe the behavior of an entire cooling system in power plants. A biofilm deposition model was fitted with experimental data and expanded in order to consider the effect of the temperature and substrate concentration. The proposed model is able to describe the behavior of the system during a determined operation horizon where the effects of the temperature and water quality are associated to a biofouling rate model.  The modeling employs a graph-based network approach to include in the analysis the pump water supply, the associated pipes, and the steam condenser itself. The fouling analysis encompasses thermal and hydraulic effects, i.e. the model can describe the impact of the fouling layer in the reduction of the overall heat transfer coefficient, but also in the increase in the flow resistance associated to the reduction of the free flow area and the increase of surface roughness. The importance of adopting the proposed model is demonstrated by the analysis of two different scenarios: a short-term simulation corresponding to the beginning of an operational run and a long term simulation of two years of operation.

Authors:

* Jaime Souza (jaime.souza@enkrott.com)
* Aline Souza (a.rayboltt@gmail.com)
* André Luiz Hemerly Costa (andrehc@uerj.br)
* Luís Manuel Ferreira de Melo (lmelo@fe.up.pt)

Keywords:  fouling, heat exchanger, condenser, network, power plant

## PYTHON source code

### How to develop?

1. Clone the repository
2. Create a virtualenv with Python 3
3. Ativate the virtualenv.
4. Install the dependences.
5. Install [DAETOOLS](http://www.daetools.com/docs/getting_daetools.html#installation)
6. Test

```console
git clone git@github.com:Jaimenms/conference-hefc.git conference-hefc
cd celldeposit-condenser
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# FOLLOW DAETOOLS INSTALL PROCEDURE
python -m unittest discover ./tests
```

Important: If during the tests you get an error related to missing libs,
please include the LD_LIBRARY_PATH environmental variable according to your python version:

```console
LD_LIBRARY_PATH="/Library/Frameworks/Python.framework/Versions/3.6/lib/:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH
```

### How to run?

#### Running a simulation from command line

To run a simulation from command line, use the ./simulate.py file. It is necessary to have a json input file. Examples of this json are presented in ./cases/ folder.

For example:
```bash
python simulate.py ./cases/input.json --initial_condition ./cases/initial.json --format json --output ./cases/output.json
```

#### Running all cases related to the paper

To run all the simulation cases related to the paper

```bash
python all.py
```

### How to access the results using the DAETools GUI

Open the gui window

```bash
python -m daetools.dae_plotter.plotter &
```

Access the corresponding .simulation case in ./cases/ folder.


## PAPER source code

Please access the [paper](./paper/) folder.


## JUPYTER notebooks

These jupyter notebooks are used for the construction of simulation cases and for the analysis of the results.

Please access the [notebooks](./notebooks/) folder.