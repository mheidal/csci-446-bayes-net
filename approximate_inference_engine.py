from bayesian_network import BayesianNetwork
from inference_engine import InferenceEngine

class ApproximateInferenceEngine():
    def __init__(self, bayes_net: BayesianNetwork):
        return


    def gibbs_sampling(self, list_of_nodes: list, evidence: list, bayes_net: BayesianNetwork, N = 10000):
        # get evidence
        # generate initial sample from non evidence varibales
        generated_initial_sample = []
        for i in list_of_nodes:
            if i not in evidence:
                generated_initial_sample.append(i.generate())
        # iterate
        # for n in range(N):
        #     # sample var from P(var | all other non-evidence variables)
        #     for var in




