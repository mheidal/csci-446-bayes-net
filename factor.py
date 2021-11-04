from typing import Dict
from typing import List
from typing import Tuple

# instantiated in make_factor, pointwise_product and sum_out methods of bayesian_network
class Factor():
    def __init__(self, table: Dict, variable_indices: List[str], name):
        self.table: Dict[Tuple[Tuple[str, str], ...], float] = table
        self.variable_indices = variable_indices
        self.name = name

    def __str__(self):
        string = ""
        headered = False
        for key in self.table.keys():
            if not headered:
                for pair in key:
                    string += pair[0]
                    string += " "
                string += " | " + self.name
                string += "\n-------\n"
                headered = True
            for pair in key:
                string += pair[1] + " "
            string += "| "
            string += str(self.table[key])
            string += "\n"
        return string