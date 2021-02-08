import numpy as np
import collections
import importlib
from daetools.pyDAE import *

__doc__="""
Network model
"""


class Network(daeModel):

    def __init__(self, Name, Parent=None, Description="", data={}):
        """
        Model for the edge elements
        :param Name: name of the model
        :param Parent: parent model
        :param Description: description of the model
        :param data: parameters and other required data
        """
        daeModel.__init__(self, Name, Parent, Description)

        self.set_data(data)

        self.set_nodes()

        self.set_submodels()


    def DeclareEquations(self):
        """
        This Methos is called by the DaeTools. Here is where all the equations are defined
        :return:
        """
        for submodel_name, submodel in self.submodels.items():
            submodel.DeclareEquations()

    def set_data(self, data):
        self.data = data

    def set_nodes(self):
        """
        Recursively constructs the node tree
        :param data: model data
        :return:
        """
        nodes = {}

        for name, data in self.data.items():
            if 'kind' in data and data['kind'] == 'node' and name not in nodes:
                nodes[name] = {'outlet': [], 'inlet': []}

        for name, data in self.data.items():

            # It it is an edge (in this case the data dictionary of an edge constains the connectivity by the elements from
            # and to)
            if 'kind' in data and data['kind'] == 'edge':

                edge_name = name
                node_from = data['from']
                node_to = data['to']

                # starting a node dict part 1
                nodes[node_from]['outlet'].append(edge_name)

                # starting a node dict part2
                nodes[node_to]['inlet'].append(edge_name)


            self.nodes = nodes


    def set_submodels(self):

        self.submodels = {}

        for submodel_name, submodel_data in self.data.items():
            # get relevant data
            module_name = submodel_data['module']
            class_name = submodel_data['class']

            # Import the demanded class
            module_ = importlib.import_module(module_name)
            class_ = getattr(module_, class_name)

            # get relevant data
            module_name = submodel_data['module']
            class_name = submodel_data['class']

            # Instantiate the submodel class
            self.submodels[submodel_name] = class_(
                submodel_name,
                Parent=self,
                Description="{0} with {1}.{2}".format(submodel_name, module_name, class_name),
            )
            self.submodels[submodel_name].Parent = self
            self.submodels[submodel_name].name = submodel_name
            self.submodels[submodel_name].data = self.get_data(submodel_name)


    def get_data(self, name=None):
        if name is None:
            return self.data
        elif name not in self.data:
            return {}
        else:
            return self.data[name]


    @staticmethod
    def setup_domains(other):
        """
        Setup domains according to data dictionary structure
        :return:
        """

        if 'domains' in other.data:
            for domain, domain_data in other.data['domains'].items():
                N = domain_data['N']
                if 'initial' in domain_data:
                    initial = domain_data['initial']
                    final = domain_data['final']
                    getattr(other, domain).CreateStructuredGrid(N - 1, initial, final)

                else:
                    getattr(other,domain).CreateArray(N)

    @staticmethod
    def setup_active_states(other):
        """
        Setup active states according to data dictionary structure
        :return:
        """

        if 'states' in other.data:
            for name, value in other.data['states'].items():
                getattr(other, name).ActiveState = value


    @staticmethod
    def setup_variables(other):
        """
        Setup variables according to data dictionary structure
        :return:
        """

        # Setting the specifications
        if 'specifications' in other.data:
            for name, value in other.data['specifications'].items():
                if type(value) is str:
                    value_aux = value.split(".")
                    value = other.data[value_aux[0]][value_aux[1]]

                # n = getattr(other, name).NumberOfPoints
                # if n == 1:
                #     getattr(other, name).AssignValue(value)
                # else:
                #     for i in range(n):
                #         getattr(other, name).AssignValue(i, value)

                if isinstance(value, collections.Iterable):
                    getattr(other, name).AssignValues(np.array(value))
                else:
                    getattr(other, name).AssignValue(value)

        if 'initial_conditions' in other.data:
            for name, value in other.data['initial_conditions'].items():
                n = getattr(other, name).NumberOfPoints
                if n == 1:
                    getattr(other, name).SetInitialCondition(value)
                else:
                    for i in range(n):
                        getattr(other, name).SetInitialCondition(i, value)


    @staticmethod
    def setup_parameters(other):
        """
        Setup parameters according to data dictionary structure
        :return:
        """
        # Setting the parameters
        if 'parameters' in other.data:
            for name, values in other.data['parameters'].items():

                if type(values) is str:
                    values_aux = values.split(".")
                    values = other.data[values_aux[0]][values_aux[1]]

                # Get Shape of Domain
                expected_shape = []
                obj = getattr(other, name)
                for domain in obj.Domains:
                    expected_shape.append(domain.NumberOfPoints)

                if isinstance(values, collections.Iterable):
                    i = 0
                    for value in values:
                        getattr(other, name).SetValue(i,value)
                        i += 1
                else:
                    getattr(other, name).SetValues(values)

    @staticmethod
    def setup_initial_guess(other):
        """
        Setup initial guesses according to data dictionary structure
        :return:
        """

        # Setting the parameters

        if 'initial_guess' in other.data:

            for name, values in other.data['initial_guess'].items():

                # Get Shape of Domain
                expected_shape = []
                for domain in getattr(other, name).Domains:
                    expected_shape.append(domain.NumberOfPoints)
                expected_shape = tuple(expected_shape)

                if type(values) is dict:
                    initial = values['initial']
                    final = values['final']
                    values = np.linspace(initial, final, expected_shape[0])

                    if not expected_shape:
                        exit()

                    if values.shape == expected_shape:
                        getattr(other, name).SetInitialGuesses(np.asarray(values))
                    else:
                        values = np.repeat(values, expected_shape[1])
                        values = np.reshape(values, expected_shape)
                        getattr(other, name).SetInitialGuesses(np.asarray(values))

                else:
                    if not expected_shape:
                        getattr(other, name).SetInitialGuess(values)
                    else:
                        if not isinstance(values, collections.Iterable):
                            values = values * np.ones(expected_shape)
                        getattr(other, name).SetInitialGuesses(np.asarray(values))


    def get_inlet(self):
        """
        Get the list of all edges that gives fluid to the node
        :return:
        """
        if 'inlet' not in self.data: return []
        return self.data['inlet']


    def get_outlet(self):
        """
        Get the list of all edges that takes fluid from the node
        :return:
        """
        if 'outlet' not in self.data: return []
        return self.data['outlet']


    def get_from(self):
        """
        Get the node from which the fluid enters the edge
        :return:
        """

        return self.data['from']


    def get_to(self):
        """
        Get the node which the fluid goes
        :return:
        """

        return self.data['to']


    def get_node(self, position):
        """
        Get the node acoording to the position of the edge (from or to)
        :param position:
        :return:
        """

        if position == 'from':
            return self.get_from()
        elif position == 'to':
            return self.get_to()
        else:
            return None
