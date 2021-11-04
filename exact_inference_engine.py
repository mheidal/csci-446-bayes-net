from typing import List, Tuple, Dict
from itertools import product

from inference_engine import InferenceEngine
from bayesian_network import BayesianNetwork
from factor import Factor
from node import Node


class ExactInferenceEngine(InferenceEngine):

    def __init__(self, bayes_net: BayesianNetwork):
        super().__init__(bayes_net)

    # arguments:
    # queries: a list of strings corresponding to the names of query variables
    # evidence: a list of tuples corresponding to names and states of evidence variables
    def elim_ask(self, queries: List[str], evidence: List[Tuple[str, str]]):
        factors: List[Factor] = []
        for node in self.bayesian_network.nodes.keys():
            factors.append(self.make_factors(node, evidence))
            if node not in queries and node not in evidence[:][0]:
                self.sum_out(node, factors)
        return (self.normalize(self.pointwise_product(factors)))

    def product_dict(self, d: Dict):
        keys = d.keys()
        values = d.values()
        for instance in product(*values):
            yield(dict(zip(keys, instance)))

    # Arguments: A node name, a list of evidence nodes and their values.
    # Returns: A truth table of the node and its parents, with values restricted by evidence. For example, if the node
    # has two parents and all three are booleans, then the resulting truth table will have 2x2x2=8 rows. If one of those
    # nodes is listed as evidence, it will be treated as a node with a domain of length 1, and the resulting truth
    # table will have 2x2x1 rows.
    # Format of output: Factor.
    #   - Keys: Tuple.
    #       - Contents: Tuples.
    #           - Contents: String corresponding to node name, string corresponding to node value.
    #   - Value: A float.
    #      - The probability of the child node having the value held in the key given that the parents have the values
    #        given in the key.
    def make_factors(self, node: str, evidence: List[Tuple[str, str]]) -> Factor:
        # identification of what variables are included
        indices = []
        indices.append(node)
        for parent in self.bayesian_network.nodes[node].parents:
            indices.append(parent)

        # describes what the factor includes
        factor_name = "phi("
        for i in range(len(indices)):
            factor_name += indices[i]
            if i < len(indices) - 1:
                factor_name += ","
        factor_name += ")"

        # creation of tables
        # identification of what values to use in each column
        table = {}
        domains = {}
        for index in indices:
            index_is_not_evidence: bool = True
            domain = []
            for event in evidence:
                if event[0] == index:
                    index_is_not_evidence = False
                    domain = [event[1]]
            if index_is_not_evidence:
                for state in self.bayesian_network.nodes[index].domain:
                    domain.append(state)
            domains[index] = domain

        row_keys = list(self.product_dict(domains))

        for i in range(len(row_keys)):
            row_key_assignments = []
            for key in row_keys[i].keys():
                for value in row_keys[i][key]:
                    row_key_assignments.append((key, value))
            row_keys[i] = row_key_assignments

        for key in row_keys:
            table[tuple(key)] = self.bayesian_network.nodes[node].probability_distribution_given_evidence(key)
        factor: Factor = Factor(table, indices, factor_name)
        return factor

    # TODO
    def pointwise_product(self, f1: Factor, f2: Factor):
        f1_exclusive_variables = []
        f2_exclusive_variables = []
        shared_variables = []
        for variable_state_assignments in f1.table.keys():
            for variable_state_assignment in variable_state_assignments:
                f1_exclusive_variables.append(variable_state_assignment[0])
            break

        for variable_state_assignments in f2.table.keys():
            for variable_state_assignment in variable_state_assignments:
                if variable_state_assignment[0] not in f1_exclusive_variables:
                    f2_exclusive_variables.append(variable_state_assignment[0])
                else:
                    shared_variables.append(variable_state_assignment[0])
                    f1_exclusive_variables.remove(variable_state_assignment[0])
            break

        print("Variables exclusive to f1:")
        print(f1_exclusive_variables)

        print("Variables exclusive to f2:")
        print(f2_exclusive_variables)
        print("shared variables:")
        print(shared_variables)

        indices = []
        for f1_variable in f1_exclusive_variables:
            indices.append(f1_variable)
        for shared_variable in shared_variables:
            indices.append(shared_variable)
        for f2_variable in f2_exclusive_variables:
            indices.append(f2_variable)

        print(indices)

    pass

    # TODO
    def sum_out(self, node: str, factors: List[Factor]):
        pass

    #TODO
    def normalize(self, arg):
        pass

def main():

    # B_relations = [([], [("T", 0.5), ("F", 0.5)])]
    # C_relations = [([], [("T", 0.45), ("F", 0.55)])]
    # A_relations = [([("B", "F"), ("C", "F")], [("T", 0.2), ("F", 0.8)]),
    #                ([("B", "F"), ("C", "T")], [("T", 0.7), ("F", 0.3)]),
    #                ([("B", "T"), ("C", "F")], [("T", 0.6), ("F", 0.4)]),
    #                ([("B", "T"), ("C", "T")], [("T", 0.9), ("F", 0.1)]),
    #                ]
    # A.create_probability_table(A_relations)
    # B.create_probability_table(B_relations)
    # C.create_probability_table(C_relations)
    # print("A")
    # print(A)
    # print("B")
    # print(B)
    # print("C")
    # print(C)
    # nodes = [A, B, C]
    print("Factor test")
    domain: List[str] = ["T", "F"]
    B: Node = Node("B", domain, [])
    E: Node = Node("E", domain, [])
    A: Node = Node("A", domain, ["B", "E"])
    J: Node = Node("J", domain, ["A"])
    M: Node = Node("M", domain, ["A"])
    B.create_probability_table([([], [("T", 0.001), ("F", 0.999)])])
    E.create_probability_table([([], [("T", 0.002), ("F", 0.998)])])
    A.create_probability_table([([("B", "F"), ("E", "F")], [("T", 0.001), ("F", 0.999)]),
                                ([("B", "F"), ("E", "T")], [("T", 0.29), ("F", 0.71)]),
                                ([("B", "T"), ("E", "F")], [("T", 0.94), ("F", 0.06)]),
                                ([("B", "T"), ("E", "T")], [("T", 0.95), ("F", 0.05)]),
                                ])
    J.create_probability_table([([("A", "F")], [("T", 0.05), ("F", 0.95)]),
                                ([("A", "T")], [("T", 0.9), ("F", 0.1)])
                                ])
    M.create_probability_table([([("A", "F")], [("T", 0.01), ("F", 0.99)]),
                                ([("A", "T")], [("T", 0.7), ("F", 0.3)])
                                ])
    nodes = [B, E, A, J, M]
    bn = BayesianNetwork("")
    for node in nodes:
        bn.nodes[node.name] = node

    print(bn)
    engine: ExactInferenceEngine = ExactInferenceEngine(bn)
    print("Factors:")
    factors = []
    # factor = bn.make_factors("A", [])
    # print(factor)
    for i in ["B","E","A","J","M",]:
        factor = engine.make_factors(i, [])
        factors.append(factor)
        print(factor)
        print()
    # bn.pointwise_product(factors[3], factors[4])


if __name__ == "__main__":
    main()