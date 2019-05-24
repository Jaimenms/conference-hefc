__doc__="""
DaetTools base edge model to be extended by pipe and others:
"""

from daetools.pyDAE import *
from daetools_extended.daemodel_extended import daeModelExtended
from pyUnits import m, kg, s, K, Pa, mol, J, W, rad


class Edge(daeModelExtended):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):
        """
        Model for the edge elements
        :param Name: name of the model
        :param Parent: parent model
        :param Description: description of the model
        :param data: parameters and other required data
        """

        daeModelExtended.__init__(self, Name, Parent, Description, data=data, node_tree=node_tree)

        # Domains
        self.define_domains()

        # Defining Constants
        self.define_constants()

        # Defining Parameters
        self.define_parameters()

        # Defining Variables
        self.define_variables()


    def define_domains(self):

        pass


    def define_constants(self):

        pass


    def define_parameters(self):

        pass


    def define_variables(self):

        pass


    def eq_nodal_boundaries(self, edge_variable='P', edge_dp_variable=None, node_variable='P', position='from'):

        nodename = self.get_node(position)
        if nodename:

            if position == 'from':
                domainType = eLowerBound
                dsignal = -1
            else:
                domainType = eUpperBound
                dsignal = +1

            eq = self.CreateEquation("BC_{0}_{1}_{2}".format(edge_variable, node_variable, nodename))
            x = eq.DistributeOnDomain(self.x, domainType)
            if self.YDomains:
                y = eq.DistributeOnDomain(self.y, eClosedClosed)
                if edge_dp_variable:
                    eq.Residual = getattr(self, edge_variable)(x,y) - dsignal * getattr(self, edge_dp_variable)(y) - getattr(self.Parent.submodels[nodename],node_variable)()
                else:
                    eq.Residual = getattr(self, edge_variable)(x,y) - getattr(self.Parent.submodels[nodename],node_variable)()
            else:
                if edge_dp_variable:
                    eq.Residual = getattr(self, edge_variable)(x,) - dsignal * getattr(self, edge_dp_variable)() - getattr(self.Parent.submodels[nodename],node_variable)()
                else:
                    eq.Residual = getattr(self, edge_variable)(x,) - getattr(self.Parent.submodels[nodename],node_variable)()


    def eq_pressure_boundaries(self):
        """
        This method writes the pressure balance to the correspondent node instance
        :return:
        """

        self.eq_nodal_boundaries(edge_variable='P', node_variable='P', position='from', edge_dp_variable='dPlb')
        self.eq_nodal_boundaries(edge_variable='P', node_variable='P', position='to', edge_dp_variable='dPub')

        #self.eq_nodal_boundaries(edge_variable='P', node_variable='P', position='from', edge_dp_variable=None)
        #self.eq_nodal_boundaries(edge_variable='P', node_variable='P', position='to', edge_dp_variable=None)


    def eq_temperature_boundaries(self):
        """
        This method writes the pressure balance to the correspondent node instance
        :return:
        """

        self.eq_nodal_boundaries(edge_variable='T', node_variable='T', position='from')
        #self.eq_nodal_boundaries(edge_variable='T', node_variable='T', position='to')


    def DeclareEquations(self):
        """
        This Methos is called by the DaeTools. Here is where all the equations are defined
        :return:
        """

        daeModelExtended.DeclareEquations(self)