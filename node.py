from typing import List
from typing import Tuple

# all nodes have their children
# probability distrib for node
# sum_out

class Node:
    def __init__(self, name: str, domain: List[str], parents: List[str], is_evidence: bool = False, state: str = None) -> None:
        self.name: str = name
        self.domain: List[str] = domain
        self.is_evidence: bool = is_evidence
        self.state: str = state
        self.is_root: bool = (len(parents) == 0)
        self.parents: List[str] = parents
        self.children: List[str] = []
        self.string: str = ""
        self.visited: bool = False
        self.probability_table_indices: List[str] = []
        self.probability_table: dict[Tuple[Tuple[str, str]], List[Tuple[str, float]]] = {}

        self.probability_table_indices.append(self.name)

        if not self.is_root:
            for parent in self.parents:
                self.probability_table_indices.append(parent)



    def create_probability_table(self, state_relations: List[Tuple[List[Tuple[str, str]], List[Tuple[str, float]]]]) -> None:

        for edge in state_relations:
            print(edge)
            for child_state in edge[1]:
                row_key = [None] * len(self.probability_table_indices)
                row_key[self.probability_table_indices.index(self.name)] = child_state[0]
                for parent_state in edge[0]:
                    row_key[self.probability_table_indices.index(parent_state[0])] = parent_state[1]
                self.probability_table[tuple(row_key)] = child_state[1]


        # for edge in state_relations:
        #     row = [None] * (len(self.parents) + len(self.domain))
        #     parent_states: List[Tuple[str, str]] = edge[0]
        #     child_probabilities: List[Tuple[str, float]] = edge[1]
        #     if not self.is_root:
        #         for parent_state in parent_states:
        #             parent_index: int = self.probability_table_indices.index(parent_state[0])
        #             row[parent_index] = parent_state[1]
        #     for child_state in child_probabilities:
        #         child_index: int = self.probability_table_indices.index(child_state[0])
        #         row[child_index] = child_state[1]
        #     self.probability_table[tuple(parent_states)] = child_probabilities

    def set_as_evidence(self, state: str) -> None:
        self.is_evidence = True
        self.state = state

    # arguments:
    # evidence: a list of tuples of variable names and state assignments to those variables.
    # def probability_distribution_given_evidence(self, evidence: List[Tuple[str, str]]) -> List[float]:
    #     evidence_parents = []
    #     for event in evidence:
    #         if event[0] in self.parents:
    #             evidence_parents.append(event)
    #     probabilities: List[float] = [0] * len(self.domain)
    #     for row in self.probability_table:
    #         row_matches_evidence: bool = True
    #         for variable in evidence_parents:
    #             if row[self.probability_table_indices.index(variable[0])] != variable[1]:
    #                 row_matches_evidence = False
    #         if row_matches_evidence:
    #             for i in range(len(self.domain)):
    #                 probabilities[i] += row[self.probability_table_indices.index(self.domain[i])]
    #     total = sum(probabilities)
    #     for i in range(len(probabilities)):
    #         probabilities[i] = probabilities[i] / total
    #
    #     for event in evidence:
    #         if event[0] == self.name:
    #             return [probabilities[self.probability_table_indices.index(event[1]) - len(self.parents)]]
    #     return probabilities

    # def probability_distribution_given_evidence(self, evidence: List[Tuple[str, str]]) -> List[float]:
    #     evidence_parents = []
    #     prob = []
    #     for event in evidence:
    #         if event[0] in self.parents:
    #             evidence_parents.append(event)
    #     probabilities: List[float] = [0] * len(self.domain)
    #     for key in self.probability_table:
    #         key_matches_evidence: bool = True
    #         for variable in evidence_parents:
    #             if key[self.probability_table_indices.index(variable[0])][1] != variable[1]:
    #                 key_matches_evidence = False
    #         if key_matches_evidence:
    #             for i, domain_item in enumerate(self.domain):
    #                 probabilities[i] += self.probability_table.get(key)[i][1]
    #                 prob.append(self.probability_table.get(key)[i][1])
    #     # total = sum(probabilities)
    #     # for i in range(len(probabilities)):
    #     #     probabilities[i] = probabilities[i] / total
    #
    #     for event in evidence:
    #         if event[0] == self.name:
    #             return [probabilities[self.probability_table_indices.index(event[1]) - len(self.parents)]]
    #     return prob

    def probability_distribution_given_evidence(self, evidence: List[Tuple[str, str]]) -> List[float]:
        self.parents = self.parents
        return []

    def get_parents(self) -> List[str]:
        return self.parents

    def add_child(self, child: str) -> None:
        self.children.append(child)

    #TODO: MAKE WORK WITH MULTI-CHARACTER STATES AND VARIABLE NAMES
    def __str__(self) -> str:
        if self.string == "":
            string: str = ""
            for index in self.probability_table_indices:
                string += index + " "
            string += "\n"
            for key, value in self.probability_table.items():
                for state_assignment in key:
                    string += state_assignment + " "
                string += str(value) + "\n"
            self.string = string
            return string
        else:
            return self.string


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

    print(A.probability_distribution_given_evidence([("B", "T")]))  # ("C", "F")

if __name__ == "__main__":
    main()
