__doc__="""
DAESIMULATIONEXTENDED
Author: Jaime Souza
This code extends the class daeModel (http://www.daetools.com)
"""

from daetools.pyDAE import *
from daetools_extended.daemodel_extended import daeModelExtended
from daetools_extended.tools import execute_recursive_method, get_module_class_from_data, get_node_tree
from daetools.dae_plotter.data_receiver_io import pickleProcess


class daeSimulationExtended(daeSimulation):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree = {}, set_reporting = True, reporting_interval = 100, time_horizon = 0):

        daeSimulation.__init__(self)

        class_ = get_module_class_from_data(data)

        if not class_:
            class_ = daeModelExtended

        if not node_tree:
            node_tree = get_node_tree(Name, data)

        self.m = class_(Name, Parent=Parent, Description=Description, data=data, node_tree=node_tree)

        self.m.SetReportingOn(set_reporting)

        if set_reporting:
            self.ReportingInterval = reporting_interval

        if time_horizon > 0:
            self.TimeHorizon = time_horizon


    def SetUpVariables(self):

        self.InitialConditionMode = eQuasiSteadyState

        execute_recursive_method(self.m,'setup_active_states')
        execute_recursive_method(self.m,'setup_variables')
        execute_recursive_method(self.m,'setup_initial_guess')


    def SetUpParametersAndDomains(self):

        execute_recursive_method(self.m,'setup_domains')
        execute_recursive_method(self.m,'setup_parameters')


    def SavePickle(self, filename, dr):

        pickleProcess(dr.Process, filename)
