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
            for child_state in edge[1]:
                row_key = [None] * len(self.probability_table_indices)
                row_key[self.probability_table_indices.index(self.name)] = child_state[0]
                for parent_state in edge[0]:
                    row_key[self.probability_table_indices.index(parent_state[0])] = parent_state[1]
                self.probability_table[tuple(row_key)] = child_state[1]

    def set_as_evidence(self, state: str) -> None:
        self.is_evidence = True
        self.domain = [state]

    # Given some list of evidence, finds which evidence is relevant to itself and returns a subset of its dictionary if
    # there are some unknown variables and a float if there are zero unknown variables, along with a list of labels of
    # the unknown variables.
    def probability_distribution_given_evidence(self, evidence: List[Tuple[str, str]]):
        common_variables = []
        for event in evidence:
            if event[0] in self.probability_table_indices:
                common_variables.append(event[0])
        if len(common_variables) == len(self.probability_table_indices):
            key = [None] * len(common_variables)
            for event in evidence:
                key[self.probability_table_indices.index(event[0])] = event[1]
            key = tuple(key)
            return self.probability_table[key]
        elif len(common_variables) == 0:
            return self.probability_table
        else:
            unknowns = []
            for index in self.probability_table_indices:
                if index not in common_variables:
                    unknowns.append(index)
            probability_table_subset = {}
            for key in self.probability_table.keys():
                is_matching_row = True
                row_key = [None] * len(unknowns)
                for event in evidence:
                    if event[0] in common_variables:
                        if not key[self.probability_table_indices.index(event[0])] == event[1]:
                            is_matching_row = False
                if is_matching_row:
                    for unknown in unknowns:
                        row_key[unknowns.index(unknown)] = key[self.probability_table_indices.index(unknown)]
                    row_key = tuple(row_key)
                    probability_table_subset[row_key] = self.probability_table[key]
            return unknowns, probability_table_subset

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
            string += "\n----------------\n"
            for key, value in self.probability_table.items():
                for state_assignment in key:
                    string += state_assignment + " "
                string += " | " + str(value) + "\n"
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

    evidences = [ [("C", "F"), ("B", "F"), ("A", "F")],
                  [("C", "F"), ("B", "F"), ("A", "T")],
                  [("C", "F"), ("B", "T"), ("A", "F")],
                  [("C", "F"), ("B", "T"), ("A", "T")],
                  [("C", "T"), ("B", "F"), ("A", "F")],
                  [("C", "T"), ("B", "F"), ("A", "T")],
                  [("C", "T"), ("B", "T"), ("A", "F")],
                  [("C", "T"), ("B", "T"), ("A", "T")],
                  [("C", "T"), ("B", "T")],
                  [("C", "T"), ("B", "F")],
                  [("C", "F"), ("B", "T")],
                  [("C", "F"), ("B", "F")],
                  [("A", "T"), ("B", "T")],
                  [("A", "T"), ("B", "F")],
                  [("A", "F"), ("B", "T")],
                  [("A", "F"), ("B", "F")],
                  [("A", "T"), ("C", "T")],
                  [("A", "T"), ("C", "F")],
                  [("A", "F"), ("C", "T")],
                  [("A", "F"), ("C", "F")]
                  ]

    for evidence in evidences:
        print(A.probability_distribution_given_evidence(evidence))

if __name__ == "__main__":
    main()
