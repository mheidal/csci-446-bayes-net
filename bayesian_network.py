import inspect
from copy import deepcopy
import platform
from itertools import chain
from typing import List, Tuple, Dict

from node import Node


# J | B is True
# 94.5% True, 5.3% False

class BayesianNetwork:

    def __init__(self, bif_file_name: str) -> None:
        self.bif_file_name: str = bif_file_name
        self.name = ""
        self.str = ""
        self.traversal: List[str] = []
        self.nodes: dict[str, Node] = {}
        self.roots: List[Node] = []
        self.__generate_network_from_bif()          # this methods must be last in the constructor

    def __str__(self) -> str:
        if self.str == "":
            string: str = ""
            for key in self.nodes:
                string += f"{key}:\n{self.nodes.get(key)}\n"
            self.str = string
            return string
        else:
            return self.str

    def __set_children(self) -> None:
        stack = inspect.stack()[1]
        caller_name: str = stack[3]
        if caller_name != "__generate_network_from_bif":
            raise OSError(
                "BayesianNetwork.__set_children() can only be called from BayesianNetwork.__generate_network_from_bif()")
        for key in self.get_nodes():
            node = self.get_nodes().get(key)
            for parent in node.parents:
                self.get_node(parent).add_child(node.name)

    def __generate_network_from_bif(self) -> None:
        stack = inspect.stack()[1]
        caller_name: str = stack[3]
        if caller_name != "__init__":
            raise OSError("BayesianNetwork.__generate_network_from_bif() can only be called from constructor")
        slashes: str = "\\" if platform.system() == 'Windows' else "/"
        with open(f"networks{slashes}{self.bif_file_name}", 'r') as network_file:
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
                            domain_length: str = this_line[this_line.index("[") + 1:this_line.index("]")].replace(" ",
                                                                                                                  "")
                            node.append(domain_length)
                            domain: List[str] = this_line.split("{")
                            domain[1] = domain[1].replace(" };\n", "")
                            domain = domain[1].split(", ")
                            for state in domain:
                                state = state.replace(" ", "")
                                node.append(state)
                        line = next(iterable_network_file)
                        iteration += 1
                    str_nodes.append(node)
                    continue

                elif line.startswith("probability"):  # probability table for a node and generate Node
                    probability_line: str = deepcopy(line)
                    this_node: List[str] = []
                    domain: List[str] = []

                    if "|" in probability_line:  # get node's parents if not root (root node does not have a '|')
                        node_name = probability_line[
                                    probability_line.index('(') + 1:probability_line.index('|')].replace(" ", "")
                        parents = probability_line[probability_line.index('|') + 1:probability_line.index(')')].replace(
                            " ", "").split(",")
                    else:
                        node_name = probability_line[
                                    probability_line.index('(') + 1:probability_line.index(')')].replace(" ", "")
                        parents = []

                    for str_node in str_nodes:
                        if str_node[0] == node_name:
                            this_node = str_node
                            break

                    for state in range(0, int(this_node[2])):
                        domain.append(this_node[state + 3])

                    nodes.append(Node(name=this_node[0], domain=domain,
                                      parents=parents))  # create node now that parents are known
                    node_index: int = len(nodes) - 1

                    line = next(iterable_network_file)
                    iteration += 1

                    if line.startswith("  table"):  # root node probability table
                        self.roots.append(nodes[-1])
                        probability_line_list: List[str] = deepcopy(line).replace(" ", "").replace(";", "").replace(
                            "table", "").replace("\n", "").split(",")
                        state_prob_list: List[Tuple[str, float]] = []
                        for probability, domain_item in zip(probability_line_list, domain):
                            state_prob: Tuple[str, float] = (domain_item, float(probability))
                            state_prob_list.append(state_prob)
                        relation: List[Tuple[List[Tuple[str, str]], List[Tuple[str, float]]]] = [([], state_prob_list)]
                        nodes[node_index].create_probability_table(relation)
                        continue

                    elif line.startswith("  ("):  # non-root node probability table

                        relation: List[Tuple[List[Tuple[str, str]], List[Tuple[str, float]]]] = []

                        while not line.startswith('}'):
                            parent_states: List[str] = deepcopy(line)[line.index("(") + 1:line.index(")")].replace(" ",
                                                                                                                   "").split(
                                ",")
                            probability_of_node_states_for_parents: List[str] = deepcopy(line)[line.index(")") + 1:len(
                                line) - 2].replace(" ", "").split(",")

                            parents_and_state: List[Tuple[str, str]] = []
                            for parent, state in zip(parents, parent_states):
                                parents_and_state.append((parent, state))

                            node_state_and_probability: List[Tuple[str, float]] = []
                            for domain_item, probability in zip(domain, probability_of_node_states_for_parents):
                                node_state_and_probability.append((domain_item, float(probability)))

                            relation.append((parents_and_state, node_state_and_probability))
                            line = next(iterable_network_file)
                            iteration += 1

                        nodes[node_index].create_probability_table(relation)
                        continue
                elif line.startswith("}"):  # end of a variable, network or probability
                    pass
                else:
                    raise IOError(f"Non standard file format found at line {iteration}: {line}")
                continue
            self.nodes = {}
            for node_obj in nodes:
                self.nodes[node_obj.name] = node_obj
        self.__set_children()
        return None

    def get_nodes(self) -> dict[str, Node]:
        return self.nodes

    def get_node(self, name: str) -> Node:
        return self.nodes.get(name)

    # def topological_order(self) -> List[Node]:
    #     topological_ordering: List[Node] = deepcopy(self.roots)
    #     roots: List[Node] = deepcopy(self.roots)
    #     index: int = 0
    #     while roots != []:
    #         root_node = deepcopy(roots[index])
    #         root_node.visited = True
    #         roots.remove(roots[index])
    #         for child_key in root_node.children:
    #             child: Node = self.get_node(child_key)
    #             child.visited = True
    #     return topological_ordering

    def dfs(self) -> List[Node]:
        roots: List[Node] = deepcopy(self.roots)
        generations: List[List[Node]] = [roots]  # children of previous generation
        topological_ordering: List[Node] = []
        current_generation: List[Node] = self.next_generation(roots, topological_ordering)
        while current_generation != []:
            generations.append(current_generation)
            topological_ordering = list(chain.from_iterable(generations))
            current_generation = self.next_generation(generations[len(generations)-2], topological_ordering)
        return topological_ordering

    def next_generation(self, current_generation: List[Node], current_ordering: List[Node]) -> List[Node]:
        next_generation_list: List[Node] = []
        for node in current_generation:
            for child_key in node.children:
                child: Node = self.get_node(child_key)
                parents_in_ordering: bool = True
                for parent_key in child.parents:
                    parent: Node = self.get_node(parent_key)
                    if parent not in current_ordering:
                        parents_in_ordering = False
                if child not in next_generation_list and parents_in_ordering is True:
                    next_generation_list.append(child)
        return next_generation_list

    # def traverse(self) -> None:
    #     for root in self.roots:
    #         self._traverse(node=root.name)
    #
    # def _traverse(self, node: str) -> None:
    #     if not self.get_node(node).visited:
    #         self.traversal.append(node)
    #     else:
    #         self.get_node(node).visited = True
    #     for child in self.get_node(node).children:
    #         self._traverse(child)
    #     return

    def get_node_order(self) -> Dict[str, Node]:
        return self.nodes
