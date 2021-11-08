#from inference_engine import InferenceEngine
import random
import math
from bayesian_network import BayesianNetwork

class ApproximateInferenceEngine():

    def __init__(self, bayes_net: BayesianNetwork):
        #super().__init__(bayes_net)
        self.bn = bayes_net
        self.N = 10000
        return

    def markov_blanket(self, node) -> list:
        # get parents, get children, get childrens parents
        # markov_blanet = []
        # markov_blanet.append(node.get_parents())
        # markov_blanet.append(node.children)
        # for child_name in node.children:
        #     child = self.bn.get_node(child_name)
        #     child_parents = child.get_parents()
        #     for parent in child_parents:
        #         if parent not in markov_blanet:
        #             markov_blanet.append(parent)
        # for node_name in markov_blanet:
        #     markov_blanet[markov_blanet.index(node_name)] = self.bn.get_node(node_name)
        # return markov_blanet

        parents = []
        children = []
        siblings = []

        if node.is_root == False:
            parents = node.get_parents()
        children = node.children
        for child_name in node.children:
            child = self.bn.get_node(child_name)
            child_parents = child.get_parents()
            for parent in child_parents:
                if parent not in parents and parent not in children and parent not in siblings:
                    siblings.append(parent)
        return parents, children, siblings





    def forward_sample(self, query, evidence: list) -> dict:
        ordering = self.bn.dfs()

        #remove non evidence and non query variables
        for remove_evidence_query in ordering:
            if remove_evidence_query in evidence:
                ordering.remove(remove_evidence_query)
            if remove_evidence_query in query:
                ordering.remove(remove_evidence_query)


        # variables i nees
        i = 0
        temp_weights_root = []
        temp_keys_root = []
        temp_weights_non_root = []
        temp_keys_non_root = []
        temp_parents_values = []
        generated_sample = {}

        # generate initial sample
        for node in ordering:
            #print("node",node)
            for key in node.probability_table:
                values = node.probability_table.get(key)

                #print(i, " value ", values)
                #print(i, "key", key)
                temp_weights_root.append(values)
                temp_keys_root.append(key)
            i+=1
            if node.is_root == True:
                generated_choice_root = random.choices(population=temp_keys_root, weights=temp_weights_root, k=1)
                generated_sample[node.name] = generated_choice_root[0][0]
                #print(generated_sample)
            else:
                for parent in node.get_parents():
                    for key in generated_sample:
                        value = generated_sample.get(key)
                        if parent == key:
                            temp_parents_values.append((parent, value))
                    # for event in evidence:
                    #     if parent == event:
                    #         temp_parents_values.append((parent, event.evidence))

                temp_tuple_list = temp_parents_values
                probability_distribution_given_parents = node.probability_distribution_given_evidence(temp_tuple_list)
                for key in probability_distribution_given_parents[1]:
                    value = probability_distribution_given_parents[1].get(key)
                    temp_keys_non_root.append(key)
                    temp_weights_non_root.append(value)
                generated_choice_non_root = random.choices(population=temp_keys_non_root, weights=temp_weights_non_root, k=1)
                generated_sample[node.name] = generated_choice_non_root[0][0]
                #random.choices(population=, weights=temp_weights, k=1)
            temp_weights_root = []
            temp_keys_root = []
            temp_weights_non_root = []
            temp_keys_non_root = []
            temp_parents_values = []
        return generated_sample

    def get_probability_distribution(self, node, initial_sample, given_evidence):
        # function to reduce bloat of gibbs sampling
        evidence = []
        for event in given_evidence:
            if event in initial_sample:
                value = initial_sample.get(event)
                evidence.append((event, value))
        return node.probability_distribution_given_evidence(evidence)

    def get_keys_and_weights(self, pd) -> list:
        # function to reduce bloat of gibbs sampling
        temp_keys = []
        temp_weights = []
        for key in pd:
            value = pd.get(key)
            temp_keys.append(key)
            temp_weights.append(value)
        return temp_weights, temp_keys

    def gibbs_sampling(self, query, evidence: list):
        initial_sample = self.forward_sample(query, evidence)
        print(initial_sample)
        for node in self.bn.nodes:
            node = self.bn.get_node(node)

            # get markov blanet
            parents, children, siblings = self.markov_blanket(node)

            # find all dependent probailities
            dependent_probailities = []

            # find probability of root node
            if node.is_root == True:
                #find base probaility of node
                #print(node.probability_table)
                probability_distribution = node.probability_table
                weights = []
                keys = []
                weights, keys = self.get_keys_and_weights(probability_distribution)
                weighted_choice = random.choices(population=keys, weights=weights, k=1)
                dependent_probailities.append(weights[keys.index(weighted_choice[0])])

            #find probability distribution of node given parents and slect nevariable based on weight
            if node.is_root == False:
                probability_distribution = self.get_probability_distribution(node, initial_sample, parents)
                weights = []
                keys = []
                weights, keys = self.get_keys_and_weights(probability_distribution[1])
                weighted_choice = random.choices(population=keys, weights=weights, k=1)
                dependent_probailities.append(weights[keys.index(weighted_choice[0])])

            #find probability distribution of children given node and childrens parents
            for child_ in children:
                child_in_children = self.bn.get_node(child_)
                child_in_children_parent = child_in_children.get_parents()
                probability_distribution = self.get_probability_distribution(child_in_children, initial_sample, child_in_children_parent)
                weights = []
                keys = []
                weights, keys = self.get_keys_and_weights(probability_distribution[1])
                weighted_choice = random.choices(population=keys, weights=weights, k=1)
                dependent_probailities.append(weights[keys.index(weighted_choice[0])])

            #x = math.prod(dependent_probailities)

            # for node_name in markov_blanet:
            #     markov_blanet[markov_blanet.index(node_name)] = self.bn.get_node(node_name)



        # for i in non_evidence_variables:
        #     i = random.choice(bayes_net.variable_value(i))
        #     initial_sample.append(i)

        # non_evidence_variables = []
        # for key in self.bn.get_nodes():
        #     if self.bn.nodes[key].is_evidence == False:
        #         if key not in query:
        #             non_evidence_variables.append(key)
        #
        # initial_sample = self.forward_sample(query, evidence)

        # for n in range(self.N):
        #     for var in non_evidence_variables:
        #         markov_blanet = self.markov_blanket_varibales(var)
        #         # compute P(var | varibales in vars markov blanket)








