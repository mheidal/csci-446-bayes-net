from typing import List
from typing import Tuple

class BayesianNetwork:

    def __init__(self, bif_file: str) -> None:
        self.bif_file: str = bif_file
        pass

    def generate_network_from_bif(self) -> None:
        pass

    # arguments:
    # queries: a list of strings corresponding to the names of query variables
    # evidence: a list of tuples corresponding to names and states of evidence variables
    def query(self, queries: List[str], evidence: List[Tuple[str]]):
        pass