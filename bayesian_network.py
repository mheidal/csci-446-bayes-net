import inspect
from copy import deepcopy
from typing import List
from typing import Tuple

import numpy as numpy
from node import Node


class BayesianNetwork:

    def __init__(self, bif_file_name: str) -> None:
        self.bif_file_name: str = bif_file_name
        self.name = ""
        self.__generate_network_from_bif()

    def __generate_network_from_bif(self) -> None:
        stack = inspect.stack()[1]
        caller_name: str = stack[3]
        if caller_name != "__init__":
            raise OSError("BayesianNetwork.__generate_network_from_bif() can only be called from constructor")
        with open(f"networks\\{self.bif_file_name}", 'r') as network_file:
            str_nodes = []  # str node format: [name, type, number_of_states, state names..., ]
            nodes: List[Node] = []
            iterable_network_file = iter(network_file)
            iteration: int = -1
            for line in iterable_network_file:
                iteration += 1
                if line.startswith("network"):  # start of a network file
                    if iteration != 0:
                        raise IOError("File does not start with a network declaration")
                    else:
                        name: str = deepcopy(line)
                        name = name.replace("network ", "")
                        bracket_index: int = name.index('{')
                        self.name = name[:bracket_index - 1]
                elif line.startswith("variable"):  # node
                    node: List[str] = []
                    node_name: str = deepcopy(line)
                    node_name = node_name.replace("variable ", "")
                    node_name = node_name.replace(" {", "")
                    node_name = node_name.replace("\n", "")
                    node.append(node_name)
                    line = next(iterable_network_file)
                    iteration += 1
                    while not line.startswith('}'):
                        if line.startswith('  type'):
                            node_type: str = deepcopy(line)
                            node_type = node_type.replace("type ", "")
                            node_type = node_type[:node_type.index("[") - 1]
                            node.append(node_type.replace(" ", ""))
                            this_line: str = deepcopy(line)
                            domain_length: str = this_line[this_line.index("[")+1:this_line.index("]")].replace(" ", "")
                            node.append(domain_length)
                            domain: List[str] = this_line.split("{")
                            domain[1] = domain[1].replace(" };\n", "")
                            domain = domain[1].split(", ")
                            for state in domain:
                                node.append(state)
                        line = next(iterable_network_file)
                        iteration += 1
                    str_nodes.append(node)
                    continue
                elif line.startswith("probability"):  # probability table for a node
                    probability_line: str = deepcopy(line)
                    parents: List[str] = []
                    this_node: List[str] = []
                    domain: List[str] = []
                    node_name: str = ""
                    if "|" in probability_line:
                        node_name = probability_line[probability_line.index('(')+1:probability_line.index('|')].replace(" ", "")
                        parents = probability_line[probability_line.index('|')+1:probability_line.index(')')].replace(" ", "").split(",")
                    else:
                        node_name = probability_line[probability_line.index('(')+1:probability_line.index(')')].replace(" ", "")
                    for str_node in str_nodes:
                        if str_node[0] == node_name:
                            this_node = str_node
                            break
                    for state in range(0, int(this_node[2])-1):
                        domain.append(this_node[state+int(this_node[2])])
                    nodes.append(Node(name=this_node[0], domain=domain, parents=parents))
                    while not line.startswith('}'):
                        if line.startswith("  table"):
                            pass
                        if line.startswith("  ("):
                            pass
                        line = next(iterable_network_file)
                        iteration += 1
                    continue
                elif line.startswith("}"):  # end of a variable, network or probability
                    pass
                elif False:
                    pass
                else:
                    raise IOError(f"Non standard file format found at line {iteration}: {line}")
                continue

    # arguments:
    # queries: a list of strings corresponding to the names of query variables
    # evidence: a list of tuples corresponding to names and states of evidence variables
    def query(self, queries: List[str], evidence: List[Tuple[str]]):
        pass