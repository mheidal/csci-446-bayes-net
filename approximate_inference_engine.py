#from inference_engine import InferenceEngine
import random
from bayesian_network import BayesianNetwork

class ApproximateInferenceEngine():

    def __init__(self, bayes_net: BayesianNetwork):
        #super().__init__(bayes_net)
        self.bn = bayes_net
        self.N = 10000
        return

    def dfs(self):
        pass

        # get root nodes.
        # traverse root
        # get children of roots
        # traverse children of roots
        # get children of children...

    def forward_sample(self, query, evidence: list) -> list:


        # traverse graph in order

        for nodes in self.bn.roots:
            #node = self.bn.nodes.get(key)
        #create topological order
        top_order = dfs()

        # at each node generate 'answer' based on probability

        # if random.randint(0, 100) < 50:
        #     pass
        #return list of generated sample

    def markov_blanket_varibales(self, var) -> list:
        pass

    def gibbs_sampling(self, query, evidence: list):
        #get non_evidence variables
        # non_evidence_variables = []
        # for var in self.bn.nodes.keys:
        #     if var not in evidence:
        #         if var != query:
        #             non_evidence_variables.append(var)

        # generate initial sample
        #initial_sample = self.forward_sample(non_evidence_variables)

        # for i in non_evidence_variables:
        #     i = random.choice(bayes_net.variable_value(i))
        #     initial_sample.append(i)

        non_evidence_variables = []
        for key in self.bn.get_nodes():
            if self.bn.nodes[key].is_evidence == False:
                if key not in query:
                    non_evidence_variables.append(key)

        initial_sample = self.forward_sample(query, evidence)

        # for n in range(self.N):
        #     for var in non_evidence_variables:
        #         markov_blanet = self.markov_blanket_varibales(var)
        #         # compute P(var | varibales in vars markov blanket)








