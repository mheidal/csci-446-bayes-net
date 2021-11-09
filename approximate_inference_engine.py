# from inference_engine import InferenceEngine
import random
import math
from bayesian_network import BayesianNetwork
from copy import deepcopy


class ApproximateInferenceEngine():

    def __init__(self, bayes_net: BayesianNetwork):
        #constructor
        self.bn = bayes_net
        # this is the iterations
        self.N = 1000
        self.iterations: int = 0

    def markov_blanket(self, node) -> list:
        """
        Gets the markov blanket of node
        :param node:
        :return lists parents, children, siblings:
        """

        parents = []
        children = []
        siblings = []

        if node.is_root == False:
            parents = node.get_parents()
        children = node.children
        for child_name in node.children:
            self.iterations += 1
            child = self.bn.get_node(child_name)
            child_parents = child.get_parents()
            for parent in child_parents:
                self.iterations += 1
                if parent not in parents and parent not in children and parent not in siblings:
                    if parent != node.name:
                        siblings.append(parent)
        return parents, children, siblings

    def forward_sample(self, query, evidence: list) -> dict:
        """
        This is the forward sampling algorithm,
        It iterates through the topological order and probabilistically generates a state for each node,
        The states it generates are based on their parents if they have them
        :param query:
        :param evidence:
        :return dictionary of nodes, where key is node and value is state of node
        """
        ordering = self.bn.topological_ordering()

        # variables i need
        i = 0
        temp_weights_root = []
        temp_keys_root = []
        temp_weights_non_root = []
        temp_keys_non_root = []
        temp_parents_values = []
        generated_sample = {}

        # generate initial sample

        for node in ordering:
            self.iterations += 1
            this_node_is_evidence = False
            for event in evidence:
                self.iterations += 1
                if node.name == event[0]:
                    generated_sample[node.name] = event[1]
                    this_node_is_evidence = True
            if this_node_is_evidence:
                continue

            for key in node.probability_table:
                self.iterations += 1
                values = node.probability_table.get(key)
                temp_weights_root.append(values)
                temp_keys_root.append(key)
            i += 1
            if node.is_root == True:
                generated_choice_root = random.choices(population=temp_keys_root, weights=temp_weights_root, k=1)
                generated_sample[node.name] = generated_choice_root[0][0]
            else:
                for parent in node.get_parents():
                    self.iterations += 1
                    for key in generated_sample:
                        self.iterations += 1
                        value = generated_sample.get(key)
                        if parent == key:
                            temp_parents_values.append((parent, value))

                temp_tuple_list = temp_parents_values
                probability_distribution_given_parents = node.probability_distribution_given_evidence(temp_tuple_list)
                for key in probability_distribution_given_parents[1]:
                    self.iterations += 1
                    value = probability_distribution_given_parents[1].get(key)
                    temp_keys_non_root.append(key)
                    temp_weights_non_root.append(value)
                generated_choice_non_root = random.choices(population=temp_keys_non_root, weights=temp_weights_non_root,
                                                           k=1)
                generated_sample[node.name] = generated_choice_non_root[0][0]
                # random.choices(population=, weights=temp_weights, k=1)
            temp_weights_root = []
            temp_keys_root = []
            temp_weights_non_root = []
            temp_keys_non_root = []
            temp_parents_values = []
        return generated_sample

    def get_float_siblings(self, node, parent_state, initial_sample, given_evidence):
        """
        this is a method used to reduce bloat in gibbs sampling,
        it generates a probability table for a sibling of current node
        :param node:
        :param parent_state:
        :param initial_sample:
        :param given_evidence:
        :return: dict of probability table, where keys are nodes, and values are states
        """
        # function to reduce bloat of gibbs sampling
        evidence = []
        evidence.append(parent_state)
        for event in given_evidence:
            self.iterations += 1
            if event in initial_sample and not event == parent_state[0]:
                evidence.append((event, initial_sample.get(event)))
        evidence.append((node.name, initial_sample[node.name]))
        return node.probability_distribution_given_evidence(evidence)

    def get_float_parents(self, node_state, initial_sample, given_evidence):
        """
        this is a method used to reduce bloat in gibbs sampling,
        it generates a probability table for a current node given its parents
        :param node_state:
        :param initial_sample:
        :param given_evidence:
        :return: dict of probability table, where keys are nodes, and values are states
        """
        evidence = []
        evidence.append((node_state[0].name, node_state[1]))
        for event in given_evidence:
            self.iterations += 1
            if event in initial_sample and not event == node_state[0].name:
                evidence.append((event, initial_sample.get(event)))
        return node_state[0].probability_distribution_given_evidence(evidence)

    def fractions(self, all_sample, query):
        """helper function
        iterates through all the samples and gets the proportion of times a query variable was at
        a specific state
        :param all_sample:
        :param query:
        :return: dictionary where the key is a query state, and the value is the proprtion of
        times that query state is used
        """
        #find index of query
        index = 0
        fractions = {}
        for initial_sample in all_sample[0]:
            self.iterations += 1
            for i, key in enumerate(initial_sample):
                self.iterations += 1
                if query == key:
                    index = i
        for sample in all_sample:
            self.iterations += 1
            if sample.get(query) not in fractions:
                fractions[sample.get(query)] = 1
            else:
                fractions[sample.get(query)] += 1
        for key in fractions:
            self.iterations += 1
            value = fractions.get(key)
            fractions[key] = value/(self.N+1)

        return fractions

    def gibbs_sampling(self, query, evidence):
        """
        loops self.N times, inside this loop it generates all the samples using probability
        distributions from the most recent sample starting with the initial sample
        :param query:
        :param evidence:
        :return: dictionary where the key is a query state, and the value is the proprtion of
        times that query state is used
        """
        evidence_variables = []
        for event in evidence:
            evidence_variables.append(event[0])

        all_sample  = []
        initial_sample = self.forward_sample(query, evidence)
        all_sample.append(initial_sample)
        current_sample = initial_sample

        for i in range(self.N):
            self.iterations += 1
            current_sample = deepcopy(current_sample)
            q = 0
            for node in self.bn.nodes:
                self.iterations += 1
                if node == "MountainFcst" and query == ["LLIW"]:
                    print("dicks lol")
                if node in evidence_variables:
                    continue
                node = self.bn.get_node(node)

                # get markov blanet
                parents, children_of_node, siblings = self.markov_blanket(node)

                # find all dependent probailities
                dependent_probailities = []

                # find probability of root node

                for state in node.domain:
                    self.iterations += 1
                    product = 1
                    if node.is_root == True:
                        coefficient = node.probability_distribution_given_evidence([(node.name, state)])
                        product *=  coefficient if coefficient != 0 else 1
                    if node.is_root == False:
                        coefficient = self.get_float_parents((node, state),
                                               current_sample,
                                               node.parents)
                        product *=  coefficient if coefficient != 0 else 1
                    for child_ in children_of_node:
                        self.iterations += 1
                        child_ = self.bn.get_node(child_)
                        parents_of_child = child_.get_parents()
                        coefficient = self.get_float_siblings(child_, (node.name, state),
                                                                                     current_sample,
                                                                                     parents_of_child)
                        product *= coefficient if coefficient != 0 else 1

                    dependent_probailities.append(product)
                weights = []
                pop = node.domain
                summm = sum(dependent_probailities)
                if summm == 0:
                    m = query
                    y = 1
                for numerator in dependent_probailities:
                    self.iterations += 1
                    weights.append(numerator/sum(dependent_probailities))
                weighted_choice = random.choices(population=pop, weights=weights, k=1)
                current_sample[node.name] = weighted_choice[0]
                q += 1
            all_sample.append(current_sample)
        return self.fractions(all_sample, query)
