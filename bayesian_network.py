import inspect
from copy import deepcopy
from typing import List
from typing import Tuple
from typing import Dict
from itertools import product

from node import Node
from factor import Factor


class BayesianNetwork:

    def __init__(self, bif_file_name: str) -> None:
        self.bif_file_name: str = bif_file_name
        self.name = ""
        self.str = ""
        self.nodes: dict[str, Node] = {}
        #self.__generate_network_from_bif()          # this must be last in this method

    def __str__(self) -> str:
        if self.str == "":
            string: str = ""
            for key in self.nodes:
                string += f"{key}:\n{self.nodes.get(key)}\n"
            self.str = string
            return string
        else:
            return self.str

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
                            domain_length: str = this_line[this_line.index("[") + 1:this_line.index("]")].replace(" ",
                                                                                                                  "")
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

                elif line.startswith("probability"):  # probability table for a node and generate Node
                    probability_line: str = deepcopy(line)
                    this_node: List[str] = []
                    domain: List[str] = []

                    if "|" in probability_line:     # get node's parents if not root (root node does not have a '|')
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

                    nodes.append(Node(name=this_node[0], domain=domain, parents=parents))   # create node now that parents are known
                    node_index: int = len(nodes) - 1

                    line = next(iterable_network_file)
                    iteration += 1

                    if line.startswith("  table"):  # root node probability table
                        probability_line_list: List[str] = deepcopy(line).replace(" ", "").replace(";", "").replace(
                            "table", "").replace("\n", "").split(",")
                        state_prob_list: List[Tuple[str, float]] = []
                        for probability, domain_item in zip(probability_line_list, domain):
                            state_prob: Tuple[str, float] = (domain_item, float(probability))
                            state_prob_list.append(state_prob)
                        relation: List[Tuple[List[Tuple[str, str]], List[Tuple[str, float]]]] = [([], state_prob_list)]
                        nodes[node_index].create_probability_table(relation)
                        continue

                    elif line.startswith("  ("):    # non-root node probability table

                        relation: List[Tuple[List[Tuple[str, str]], List[Tuple[str, float]]]] = []

                        while not line.startswith('}'):
                            parent_states: List[str] = deepcopy(line)[line.index("(")+1:line.index(")")].replace(" ", "").split(",")
                            probability_of_node_states_for_parents: List[str] = deepcopy(line)[line.index(")")+1:len(line) - 2].replace(" ", "").split(",")

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

    # arguments:
    # queries: a list of strings corresponding to the names of query variables
    # evidence: a list of tuples corresponding to names and states of evidence variables
    def elim_ask(self, queries: List[str], evidence: List[Tuple[Node, str]]):
        factors: List[Dict] = []
        for node in self.nodes.keys():
            factors.append(self.make_factors(node, evidence))


    def make_factors(self, node: str, evidence: List[Tuple[str, str]]) -> Dict:
        indices = []
        indices.append(node)
        for parent in self.nodes[node].parents:
            indices.append(parent)
        factor_name = "phi("
        for i in range(len(indices)):
            factor_name += indices[i]
            if i < len(indices) - 1:
                factor_name += ","
        factor_name += ")"
        table = {}
        value_lists = []
        for index in indices:
            index_is_not_evidence: bool = True
            col_values = []
            for event in evidence:
                if event[0] == index:
                    index_is_not_evidence = False
                    col_values.append(event[1])
            if index_is_not_evidence:
                for state in self.nodes[index].domain:
                    col_values.append(state)
            value_lists.append(col_values)

        row_key_state_assignments: List[Tuple] = list(product(*value_lists))
        row_keys: List[Tuple[Tuple]] = [None] * len(row_key_state_assignments)
        for i in range(len(row_key_state_assignments)):
            row_keys[i] = tuple(zip(indices, row_key_state_assignments[i]))

        for key in row_keys:
            table[key] = self.nodes[node].probability_distribution_given_evidence(list(key))
        print(factor_name)
        for key in table.keys():
            print(key, ":", table[key])


    def pointwise_product(self, f1, f2):
        pass

    def get_node_order(self) -> List[Node]:
        return self.nodes

    def sum_out(self, node: Node, factors: List[Factor]):
        pass

def main():
    print("Node test")
    domain: List[str] = ["T", "F"]
    parents: List[str] = ["B", "C"]
    B: Node = Node("B", domain, [])
    C: Node = Node("C", domain, [])
    A: Node = Node("A", domain, parents)
    B_relations = [([], [("T", 0.5), ("F", 0.5)])]
    C_relations = [([], [("T", 0.45), ("F", 0.55)])]
    A_relations = [([("B", "F"), ("C", "F")], [("T", 0.2), ("F", 0.8)]),
                   ([("B", "F"), ("C", "T")], [("T", 0.7), ("F", 0.3)]),
                   ([("B", "T"), ("C", "F")], [("T", 0.6), ("F", 0.4)]),
                   ([("B", "T"), ("C", "T")], [("T", 0.9), ("F", 0.1)]),
                   ]
    A.create_probability_table(A_relations)
    B.create_probability_table(B_relations)
    C.create_probability_table(C_relations)
    print("A")
    print(A)
    print("B")
    print(B)
    print("C")
    print(C)
    nodes = [A, B, C]
    bn = BayesianNetwork("")
    for node in nodes:
        bn.nodes[node.name] = node

    print('made bn')
    print(bn)
    print("Factors:")
    bn.make_factors("A", [])



if __name__ == "__main__":
    main()