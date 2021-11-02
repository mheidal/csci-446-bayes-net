from typing import List
from typing import Tuple


class Node:
    def __init__(self, name: str, domain: List[str], parents: List[str], is_evidence: bool = False, state: str = None):
        self.name = name
        self.domain = domain

        self.is_evidence: bool = is_evidence
        self.state: str = state

        self.is_root = (len(parents) == 0)

        self.parents = parents

        self.probability_table_indices: List[str] = []
        self.probability_table = []
        if not self.is_root:
            for parent in self.parents:
                self.probability_table_indices.append(parent)

        for state in domain:
            self.probability_table_indices.append(state)

    # arguments:
    # A list of tuples. Each tuple has two elements. The first element is a list of tuples. Each of these tuples
    # contains a parent variable's name and a state for that parent variable. The second element is a list of tuples.
    # Each tuple contains the name of a state for the child variable and the probability of that state given the parent
    # variables.
    def create_probability_table(self, state_relations: List[Tuple[List[Tuple[str, str]], List[Tuple[str, float]]]]):
       for edge in state_relations:
            row = [None] * (len(self.parents) + len(self.domain))
            parent_states: List[Tuple[str, str]] = edge[0]
            child_probabilities: List[Tuple[str, float]] = edge[1]
            if not self.is_root:
                for parent_state in parent_states:
                    parent_index: int = self.probability_table_indices.index(parent_state[0])
                    row[parent_index] = parent_state[1]
            for child_state in child_probabilities:
                child_index: int = self.probability_table_indices.index(child_state[0])
                row[child_index] = child_state[1]
            self.probability_table.append(tuple(row))

    def set_as_evidence(self, state: str) -> None:
        self.is_evidence = True
        self.state = state

    # arguments:
    # evidence: a list of tuples of variable names and state assignments to those variables.
    # TODO: SHOULD THIS ONLY ALLOW EVIDENCE TO INCLUDE PARENTS? LET BAYES NET HANDLE RECURSIVE SHIT?
    # TODO: SHOULD THIS BE A METHOD OF BAYESIAN_NETWORK?
    def probability_distribution_given_evidence(self, evidence: List[Tuple[str, str]]):
        probabilities: List[float] = [0] * len(self.domain)
        for row in self.probability_table:
            row_matches_evidence: bool = True
            for variable in evidence:
                if row[self.probability_table_indices.index(variable[0])] != variable[1]:
                    row_matches_evidence = False
            if row_matches_evidence:
                for i in range(len(self.domain)):
                    probabilities[i] += row[self.probability_table_indices.index(self.domain[i])]
        total = sum(probabilities)
        for i in range(len(probabilities)):
            probabilities[i] = probabilities[i] / total
        return probabilities

    def __str__(self) -> str:
        string: str = ""
        string = string + str(self.probability_table_indices) + "\n"
        for row in self.probability_table:
            string += str(row) + "\n"
        return string

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

    print(A.probability_distribution_given_evidence([("C", "F"), ("B", "T")]))

if __name__ == "__main__":
    main()
