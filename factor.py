from typing import Dict
from typing import List

# instantiated in make_factor, pointwise_product and sum_out methods of bayesian_network
class Factor():
    def __init__(self, table: Dict, variable_indices: List[str], name):
        self.table = table
        self.variable_indices = variable_indices
        self.name = name

    def __str__(self):
        string = ""
        string += self.name + "\n" + str(self.table)
        return string