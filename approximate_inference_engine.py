from inference_engine import InferenceEngine
import random

class ApproximateInferenceEngine(InferenceEngine):
    def __init__(self, bayes_net: bayseian_network):
        super().__init__(bayes_net)
        self.N = 10000
        return

    def forward_sample(self, query, evidence: list, bayes_net: bayseian_network) -> list:

        # traverse graph in order
        # at each node generate 'answer' based on probability
        if random.randint(0, 100) < 50:
            pass
        #return list of generated sample

    def markov_blanket_varibales(self, var) -> list:
        pass

    def gibbs_sampling(self, query, evidence: list, bayes_net: bayseian_network):
        #get non_evidence variables
        non_evidence_variables = []
        for var in bayes_net.variables:
            if var not in evidence:
                if var != query:
                    non_evidence_variables.append(var)
        # generate initial sample
        #initial_sample = self.forward_sample(non_evidence_variables)

        # for i in non_evidence_variables:
        #     i = random.choice(bayes_net.variable_value(i))
        #     initial_sample.append(i)

        initial_sample = self.forward_sample(query, evidence, bayes_net)

        for n in range(self.N):
            for var in non_evidence_variables:
                markov_blanet = self.markov_blanket_varibales(var)
                # compute P(var | varibales in vars markov blanket)








