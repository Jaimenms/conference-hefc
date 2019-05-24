__doc__="""
TOOLS
Author: Jaime Souza
Extra tools for the daemode_extended module.
"""

import numpy as np
import importlib
from copy import copy


def get_module_class_from_data(data):

    if 'module' in data:

        # get relevant data
        module_name = data['module']
        class_name = data['class']

        # Import the demanded class
        module_ = importlib.import_module(module_name)
        class_ = getattr(module_, class_name)

    else:

        class_ = None

    return class_

def get_model_name_list(name, data, kind, kind_list = list()):
    """
    Recursively search the data dictionary looking for all the model names that shares the same kind
    :param name: model name
    :param data: model data
    :param kind: kind that we are looking for
    :param kind_list: kind list that is recursively incremented
    :return:
    """

    # Get the name if has the same kind
    if 'kind' in data and data['kind'] == kind:

        if name not in kind_list:

            kind_list.append(name)

    # Recursively search accross the submodels
    if 'submodels' in data:

        for submodel_name, datai in data['submodels'].items():

            kind_list = get_model_name_list(submodel_name, datai, kind, kind_list)

    return kind_list


def get_node_tree(name, data, node_tree=dict()):
    """
    Recursively constructs the node tree
    :param name: model name
    :param data: model data
    :param node_tree: dict with a key with the name of the node model conining a dict with an outlet list (list of
    edges at the node outlet) and an inlet list (list of edges at the node inlet).
    :return:
    """

    # It it is an edge (in this case the data dictionary of an edge constains the connectivity by the elements from
    # and to)
    if 'kind' in data and data['kind'] == 'edge':

        edge_name = name
        node_from = data['from']
        node_to = data['to']

        # starting a node dict part 1
        if node_from not in node_tree:
            node_tree[node_from] = {'outlet': [],'inlet': []}
        node_tree[node_from]['outlet'].append(edge_name)

        # starting a node dict part2
        if node_to not in node_tree:
            node_tree[node_to] = {'outlet': [],'inlet': []}
        node_tree[node_to]['inlet'].append(edge_name)

    # Recursively search accross the submodels
    if 'submodels' in data:

        for submodel_name, datai in data['submodels'].items():

            node_tree = get_node_tree(submodel_name, datai, node_tree=node_tree)

    return node_tree


def execute_recursive_method(obj, method_, subobj_name='submodels'):
    """
    This function permits the recursively execution a method method_ inside an object obj.
    :param obj: object
    :param method_: method name
    :return:
    """

    # if the object has it has the method execu
    if hasattr(obj, method_):
        getattr(obj, method_)()

    # If the object has an attribute with name subobj_name, start the recursivity
    if hasattr(obj, subobj_name):

        # Recursivity
        for obj_name, obj_i in obj.submodels.items():
            execute_recursive_method(obj_i, method_,subobj_name=subobj_name)


def get_initialdata_from_reporter(datareporter):
    """
    Get name, time and data for the variablens in the DaeTools datareporter
    :param datareporter: DaeTools data reporter
    :return:
    """

    # Collecting output
    output = {}

    for variable_name, (ndarr_values, ndarr_times, l_domains, s_units) in datareporter.Process.dictVariableValues.items():

        name = variable_name

        if type(ndarr_values[0]) == np.float64:
            value = ndarr_values[0]
        else:
            value = list(ndarr_values[0])

        output[name] = value


    return output


def update_initialdata(name, previous_output, data):
    """
    To update the data dictionary with the output obtained with a previous simulation
    :param name: the name of the root of the data dictionary
    :param previous_output: output dictionary of the previous simulation
    :param data: data dictionary
    :return:
    """

    # copy the data dictionary
    data_new = copy(data)

    # update the dictionary recursively
    new_data = update_initialdata_rec(name, data_new, previous_output)

    return new_data


def update_initialdata_rec(prenom, nodedata, previous_output):

    # If initial guess
    if 'initial_guess' in nodedata:
        for name in nodedata['initial_guess'].keys():

            # get variable name according to DaeTools reporter pattern
            variable_name = "{0}.{1}".format(prenom, name)

            # if found in the reporter dict
            if variable_name in previous_output:

                # update it
                if "Values" in previous_output[variable_name]:
                    nodedata['initial_guess'][name] = previous_output[variable_name]["Values"][-1]
                else:
                    nodedata['initial_guess'][name] = previous_output[variable_name][-1]

    # If the model has submodels
    if 'submodels' in nodedata:

        # Loop of the submodels
        for node_name_i, nodedata_i in nodedata['submodels'].items():

            if prenom:
                # prepare the prenom of the DaeTools reporter variable
                new_prenom = "{0}.{1}".format(prenom, node_name_i)
            else:
                new_prenom = node_name_i

            # re-run the update to the submodel
            nodedata['submodels'][node_name_i] = update_initialdata_rec(new_prenom, nodedata_i, previous_output)

    return nodedata


def daeVariable_wrapper(variable, domains_list):
    return variable(*domains_list)

def distribute_on_domains(domains, eq, eKind):
    if type(domains) == list:
        domains_list = []
        for domain in domains:
            domains_list.append(eq.DistributeOnDomain(domain, eKind))
        return domains_list
    else:
        return eq.DistributeOnDomain(domains, eKind)
