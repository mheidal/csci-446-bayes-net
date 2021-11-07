from bayesian_network import BayesianNetwork


class InferenceEngine:

    def __init__(self, bayesian_network: BayesianNetwork):
        self.bayesian_network: BayesianNetwork = bayesian_network
        return
