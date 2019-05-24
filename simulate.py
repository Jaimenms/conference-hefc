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

# Import Daetools
from daetools.pyDAE import *
from daetools.pyDAE.data_reporters import *
from daetools_extended.daesimulation_extended import daeSimulationExtended
from daetools_extended.tools import update_initialdata


### Subfunctions

def read_data(args):
    with open(args['input']) as f:
        json_data=f.read()
    return json.loads(json_data)

def configure(args):
    cfg = daeGetConfig()
    cfg.SetBoolean('daetools.activity.printHeader', False)
    cfg.SetFloat('daetools.IDAS.MaxStep',args['MaxStep'])
    cfg.SetFloat('daetools.IDAS.relativeTolerance',args['relative_tolerance'])
    cfg.GetInteger('daetools.IDAS.MaxNumSteps',args['MaxNumSteps'])
    return cfg

def save_reports(args, simulation):

    xmlfile1 = '{0}.model.xml'.format(args['input'], )
    simulation.m.SaveModelReport(xmlfile1)
    xmlfile2 = '{0}.model-rt.xml'.format(args['input'], )
    simulation.m.SaveModelReport(xmlfile2)

def inject_external(xmlfile, xmlfile_modified):

    origin_str = ('dae-tools.xsl', 'dae-tools.css')
    destination_str = ('https://s3-us-west-2.amazonaws.com/jaimenms/daetools/dae-tools.xsl',
                       'https://s3-us-west-2.amazonaws.com/jaimenms/daetools/dae-tools.css')

    try:
        with open(xmlfile) as f, open(xmlfile_modified, "w") as g:

            text = f.read()
            for str, str_modified in zip(origin_str, destination_str):
                text = text.replace(str, str_modified)
            g.write(text)
    except:
        print("File not generated")

def convert_to_xhtml(infile, outfile, xslfile):

    from lxml import etree
    xslt_doc = etree.parse(xslfile)
    xslt_transformer = etree.XSLT(xslt_doc)
    source_doc = etree.parse(infile)
    output_doc = xslt_transformer(source_doc)
    output_doc.write(outfile, pretty_print=True)

def get_reporter(args):

    if args['format'] == 'json':
        dr = daeJSONFileDataReporter()
    elif args['format'] == 'xml':
        dr = daeXMLFileDataReporter()
    elif args['format'] == 'mat':
        dr = daeMatlabMATFileDataReporter()
    elif args['format'] == 'xslx':
        dr = daeExcelFileDataReporter()
    elif args['format'] == 'vtk':
        dr = daeVTKDataReporter()
    elif args['format'] == 'csv':
        dr = daeCSVFileDataReporter()
    else:
        dr = None

    return dr

def get_name(args, data):

    if not args['name']:
        simName = data['name']
    else:
        simName = args['name']

    return simName

def merge_initial_condition(args, data):

    if args['initial_condition']:

        json_data = open(args['initial_condition']).read()
        previous_output = json.loads(json_data)
        new_data = update_initialdata("", previous_output, data)

        return new_data

    return data

def get_names(args):

    # Collect input data
    input_dirname = os.path.dirname(args['input'])
    input_basename = os.path.basename(args['input'])
    input_filename = os.path.splitext(input_basename)[0]

    # Prepare pickle
    pickle_basename = '{0}.simulation'.format(input_filename)
    pickle_file = os.path.join(input_dirname, pickle_basename)

    # Prepare output
    if not args['output']:
        output_basename = '{0}.output.{1}'.format(input_filename, args['format'])
        output_file = os.path.join(input_dirname, output_basename)
        args['output'] = output_file
    else:
        output_file = args['output']

    return (output_file, pickle_file)

# Main function
def execute(args):

    args['output'], args['pickle'] = get_names(args)

    # Read data
    data = read_data(args)

    # Merge args
    if "simulation_parameters" in data:
        for key, value in data["simulation_parameters"].items():
            args[key]=value

    # Merge Initial Condition
    data = merge_initial_condition(args, data)

    # Configure
    configure(args)

    # Reports
    dr = get_reporter(args)

    # Name
    simName = get_name(args, data)


    # Instantiate
    simulation = None
    simulation = daeSimulationExtended(simName, data=data, set_reporting = True, reporting_interval = args['reporting_interval'], time_horizon = args['time_horizon'])

    # Gui Option
    if args['format'] == 'gui':

        qtApp = daeCreateQtApplication(sys.argv)
        simulator = daeSimulator(qtApp, simulation=simulation)
        simulator.exec_()

    else:

        dr.Connect(args['output'], simName)

        solver = daeIDAS()
        solver.RelativeTolerance = args['relative_tolerance']
        log = daePythonStdOutLog()

        # Initialize
        simulation.Initialize(solver, dr, log)
        print("Number of equations", simulation.NumberOfEquations)
        print("Number of variables", simulation.TotalNumberOfVariables)
        save_reports(args, simulation)

        # Solve at time = 0
        simulation.SolveInitial()

        # Run
        try:
            simulation.Run()
        except:
            print("Could not reach the time horizon")

        # Save Pickle
        simulation.SavePickle(args['pickle'], dr)

        # Clean up
        simulation.Finalize()


def main(**kwargs):

    execute(kwargs)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Simulate a model according to DAETOOLS based on a json data. '
                                                 'It is necessary to have an openned dae_plotter thread before '
                                                 'executing. For that, please execute the following command:  '
                                                 'python -m daetools.dae_plotter.plotter &')
    parser.add_argument('input', help='Path of the json input file.')
    parser.add_argument('--format', default='gui', help='Format of output, where gui is actually '
                                                        'a graphical interface.',
                        choices=['gui', 'json', 'xml', 'mat','vtk','xlsx','csv'])
    parser.add_argument('--initial_condition', help='Path to the initial condition file.')
    parser.add_argument('--output', help='Path to the output file (not used if format is gui).')
    parser.add_argument('--name', help='Simulation name.')
    parser.add_argument('--reporting_interval', type=int, default= 3600, help='Reporting interval in seconds.')
    parser.add_argument('--time_horizon', type=int, default= 20*24*3600, help='Time horizon in seconds')
    parser.add_argument('--relative_tolerance', type=float, default= 1e-6, help='Relative tolerance for the integration '
                                                                                'method.')
    parser.add_argument('--MaxStep', type=int, default= 10., help='IDAS.MaxStep parameter.')
    parser.add_argument('--MaxNumSteps', type=int, default= 1000000, help='IDAS.MaxNumSteps parameter.')

    args = parser.parse_args()

    main(**vars(args))

# end