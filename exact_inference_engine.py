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
        evidence_vars: List[str] = []
        for event in evidence:
            evidence_vars.append(event[0])
        for node in self.bayesian_network.nodes.keys():
            factor = self.make_factors(node, evidence)
            factors.append(factor)

        for node in self.bayesian_network.nodes.keys():
            if node not in queries and node not in evidence_vars:
                for i in range(len(factors) - 1, -1, -1):
                    factors[i] = self.sum_out(node, factors[i])
                    if factors[i] == False:
                        factors.remove(factors[i])

        result = factors.pop()
        while factors:
            result = self.pointwise_product(result, factors.pop())
        result = self.normalize(result)
        return result

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
        factor: Factor = Factor(table, indices)
        return factor

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

        # print("Variables exclusive to f1:")
        # print(f1_exclusive_variables)
        #
        # print("Variables exclusive to f2:")
        # print(f2_exclusive_variables)
        # print("shared variables:")
        # print(shared_variables)

        indices = []
        for f1_variable in f1_exclusive_variables:
            indices.append(f1_variable)
        for shared_variable in shared_variables:
            indices.append(shared_variable)
        for f2_variable in f2_exclusive_variables:
            indices.append(f2_variable)

        new_dict: Dict[Tuple[Tuple[str], ...], float] = {}
        for key_1 in f1.table.keys():
            for key_2 in f2.table.keys():
                new_row = [None] * (len(shared_variables) + len(f1_exclusive_variables) + len(f2_exclusive_variables))
                rows_match = True
                for shared_variable in shared_variables:
                    if not key_1[f1.variable_indices.index(shared_variable)] == key_2[f2.variable_indices.index(shared_variable)]:
                        rows_match = False
                if rows_match:
                    for index in indices:
                        if index in f1_exclusive_variables or index in shared_variables:
                            new_row[indices.index(index)] = key_1[f1.variable_indices.index(index)]
                        elif index in f2_exclusive_variables:
                            new_row[indices.index(index)] = key_2[f2.variable_indices.index(index)]
                    new_row = tuple(new_row)
                    new_dict[new_row] = f1.table[key_1] * f2.table[key_2]

        factor: Factor = Factor(new_dict, indices)
        return factor


    def sum_out(self, node: str, factor: Factor) -> Factor:
        new_table: Dict[Tuple[Tuple[str], ...], float] = {}
        new_key_indices: List[int] = []
        for index in factor.variable_indices:
            if not index == node:
                new_key_indices.append(factor.variable_indices.index(index))
        if len(new_key_indices) == 0:
            return False
        row_marked = [False] * len(factor.table.keys())
        for i, key in enumerate(factor.table.keys()):
            if not row_marked[i]:
                new_float: float = 0
                new_float += factor.table[key]
                row_marked[i] = True
                for j, other_key in enumerate(factor.table.keys()):
                    if not row_marked[j]:
                        row_matches = True
                        for index in new_key_indices:
                                if not key[index] == other_key[index]:
                                    row_matches = False
                        if row_matches:
                            row_marked[j] = True
                            new_float += factor.table[other_key]
                row_key = [None] * len(new_key_indices)
                for k in range(len(new_key_indices)):
                    row_key[k] = key[new_key_indices[k]]
                row_key = tuple(row_key)
                new_table[row_key] = new_float

        new_key_index_names = [factor.variable_indices[m] for m in new_key_indices]
        new_factor = Factor(new_table, new_key_index_names)
        return new_factor


    #TODO
    def normalize(self, factor: Factor) -> Factor:
        norm: float = 0
        for key in factor.table.keys():
            norm += factor.table[key]
        for key in factor.table.keys():
            factor.table[key] = factor.table[key] / norm
        return factor


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
    # f = engine.make_factors("A", [("B", "T")])
    # print(f)
    # f = engine.sum_out("B", f)
    # engine.normalize(f)
    # print(f)
    # f = engine.sum_out("E", f)
    # print(f)
    # engine.normalize(f)
    # print(f)

    # print("Factors:")
    factors = []
    # factor = bn.make_factors("A", [])
    # print(factor)
    # for i in ["B","E","A","J","M",]:
    #     factor = engine.make_factors(i, [])
    #     factors.append(factor)
    #     print(factor)
    #     print()
    #
    # print("phi(A, B, E), before summing out B:")
    # print(factors[2])
    # print("after:")
    # print(engine.sum_out("B", factors[2]))
    # print("phi(B):")
    # print(factors[0])
    # print("phi(E):")
    # print(factors[1])
    # print("Pointwise product of B and E:")
    # print(engine.pointwise_product(factors[0], factors[1]))

    # x = engine.pointwise_product(
        # engine.pointwise_product(
        #     engine.pointwise_product(
        #         engine.pointwise_product(factors[0],factors[1]),factors[2]),factors[3]),factors[4])
    # x = engine.pointwise_product(factors[3], factors[4])
    # print(x)
    # engine.normalize(x)
    # print(x)

    # factor = factors[2]
    # factor = engine.pointwise_product(factor, factors[0])
    # factor = engine.sum_out("B", factor)
    # print(factor)

    # f = engine.make_factors("E", [])
    # print(f)
    # f = engine.sum_out("E", f)
    #

    # dict_x_y = {
    #     (("X", "T"), ("Y", "T")): 0.3,
    #     (("X", "T"), ("Y", "F")): 0.7,
    #     (("X", "F"), ("Y", "T")): 0.9,
    #     (("X", "F"), ("Y", "F")): 0.1,
    # }
    # indices_x_y = ["X", "Y"]
    #
    #
    # dict_y_z = {
    #     (("Y", "T"), ("Z", "T")): 0.2,
    #     (("Y", "T"), ("Z", "F")): 0.8,
    #     (("Y", "F"), ("Z", "T")): 0.6,
    #     (("Y", "F"), ("Z", "F")): 0.4,
    # }
    # indices_y_z = ["Y", "Z"]
    #
    # f1 = Factor(dict_x_y, indices_x_y)
    # print(f1)
    # f2 = Factor(dict_y_z, indices_y_z)
    # print(engine.pointwise_product(f1, f2))
    # print(engine.normalize(engine.sum_out("Z", engine.pointwise_product(f1, f2))))

    print("Begin elim ask.")
    print(engine.elim_ask(["J"], [("B", "T")]))
    print("End elim ask.")
    print("Begin elim ask.")
    print(engine.elim_ask(["B"], [("J", "T")]))
    print("End elim ask.")

if __name__ == "__main__":
    main()