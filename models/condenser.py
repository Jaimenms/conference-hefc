__doc__="""
DaetTools model that describes the behavior of a condenser.
"""


from daetools.pyDAE import *
from pyUnits import m, kg, s, K, Pa, J, W, rad

try:
    from models.edge import Edge
except:
    from .edge import Edge


class Condenser(Edge):

    def __init__(self, Name, Parent=None, Description="", data={}, node_tree={}):

        Edge.__init__(self, Name, Parent=Parent, Description=Description, data=data, node_tree=node_tree)