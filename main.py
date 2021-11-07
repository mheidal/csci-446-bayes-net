from typing import List

from node import Node

from bayesian_network import BayesianNetwork


def main() -> None:
    # bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="child.bif")
    bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="hailfinder.bif")
    print(bayesian_network)
    print(f"Nodes: {len(bayesian_network.get_nodes())}")
    ordering: List[Node] = bayesian_network.dfs()
    print(ordering)
    print(len(ordering))


if __name__ == '__main__':
    main()
