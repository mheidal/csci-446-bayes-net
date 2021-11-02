from bayesian_network import BayesianNetwork


def main() -> None:
    bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="child.bif")
    print(bayesian_network)


if __name__ == '__main__':
    main()
