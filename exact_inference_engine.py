from typing import List, Tuple, Dict
from itertools import product
from copy import deepcopy

from bayesian_network import BayesianNetwork
from factor import Factor

verbose_logging: bool = False

class ExactInferenceEngine:

    def __init__(self, bayesian_network: BayesianNetwork):
        self.bayesian_network: BayesianNetwork = bayesian_network
        return

    # arguments:
    # queries: a list of strings corresponding to the names of query variables
    # evidence: a list of tuples corresponding to names and states of evidence variables
    def elim_ask(self, queries: List[str], evidence: List[Tuple[str, str]]):
        factors: List[Factor] = []
        evidence_vars: List[str] = []
        for event in evidence:
            evidence_vars.append(event[0])
        if verbose_logging:
            print("Query variable(s)                 :", queries)
            print("Evidence variable(s) and value(s) :", evidence)
            print("Creating factors.")
        for node in self.bayesian_network.nodes.keys():
            factor = self.make_factor(node, evidence)
            factors.append(factor)
        if verbose_logging:
            print("Created factors.")

        variables = []
        for key in self.bayesian_network.nodes.keys():
            if key not in queries and key not in evidence_vars :
                variables.append(key)
        next_node: str = self.get_next_variable_to_sum_out(factors, variables)

        while next_node is not None:
            factors_with_this_node: List[Factor] = []
            for factor in factors:
                if next_node in factor.variable_indices:
                    factors_with_this_node.append(factor)
            if verbose_logging:
                print("Reducing", len(factors_with_this_node), "factors to one, converging around", next_node)
                print("There are", len(factors), "factors.")
            megafactor: Factor = None
            for factor in factors_with_this_node:
                if megafactor is None:
                    megafactor = factor
                else:
                    if verbose_logging:
                        print("        Multiplying by a factor with", len(factor.table), "rows, megafactor has", len(megafactor.table), "rows.")
                    megafactor = self.pointwise_product(megafactor, factor)
                factors.remove(factor)
            megafactor = self.sum_out(next_node, megafactor)
            factors.append(megafactor)
            variables.remove(next_node)
            next_node = self.get_next_variable_to_sum_out(factors, variables)


        if verbose_logging:
            print("Performing pointwise product.")
        result = factors.pop()
        while factors:
            result = self.pointwise_product(result, factors.pop())
            if verbose_logging:
                print(len(factors), "factor(s) remain.")
                print("Length of megatable is", len(result.table))
        if verbose_logging:
            print("Performed pointwise product.")
        result = self.normalize(result)
        return result

    # Helper function. Yields a list containing every combination of keys and values in a dictionary.
    # Used in make_factors to create every permutation of values from several nodes' domains to create truth tables.
    # Source: https://stackoverflow.com/questions/5228158/cartesian-product-of-a-dictionary-of-lists
    @staticmethod
    def product_dict(d: Dict):
        keys = d.keys()
        values = d.values()
        for instance in product(*values):
            yield(dict(zip(keys, instance)))

    # Arguments: A node name, a list of evidence nodes and their values.
    # Returns: A factor containing truth table of the node and its parents, with values restricted by evidence. For
    # example, if the node has two parents and all three are booleans, then the resulting truth table will have 2x2x2=8
    # rows. If one of those nodes is listed as evidence, it will be treated as a node with a domain of length 1, and
    # the resulting truth table will have 2x2x1=4 rows.
    # Format of output: Factor.
    #   - Keys: Tuple.
    #       - Contents: Tuples.
    #           - Contents: String corresponding to node name, string corresponding to node value.
    #   - Value: A float.
    #      - The probability of the child node having the value held in the key given that the parents have the values
    #        given in the key.
    def make_factor(self, node: str, evidence: List[Tuple[str, str]]) -> Factor:
        # identification of what variables are included
        indices = []
        indices.append(node)
        for parent in self.bayesian_network.nodes[node].parents:
            indices.append(parent)

        # creation of tables
        # identification of what values to use in each column
        table = {}
        domains = {}
        for index in indices:
            index_is_not_evidence: bool = True
            domain = []
            for event in evidence:
                if event[0] == index:
                    index_is_not_evidence = False
                    domain = [event[1].strip(" ")]
            if index_is_not_evidence:
                for state in self.bayesian_network.nodes[index].domain:
                    domain.append(state.strip(" "))
            domains[index] = domain

        row_keys = list(self.product_dict(domains))

        for i in range(len(row_keys)):
            row_key_assignments = []
            for key in row_keys[i].keys():
                row_key_assignments.append((key, row_keys[i][key]))
            row_keys[i] = row_key_assignments

        for key in row_keys:
            table[tuple(key)] = self.bayesian_network.nodes[node].probability_distribution_given_evidence(key)
        factor: Factor = Factor(table, indices)
        return factor

    # Calculates the pointwise product of two factors.
    # Does so by identifying which variables are unique to the first factor, which are unique to the second factor,
    # and which they have in common. Then iterates through every row in the first factor, concatenating its row
    # with the values of the variables unique to the second factor in each row of the second factor where the two rows
    # have equal values for all of the common variables. This concatenation produces a new row. This row is used as
    # a key in the dictionary of a new factor. The value of that key is equal to the multiplicative product of the
    # values of the two products.
    # Arguments:
    # - f1: one factor.
    # - f2: the other factor.
    # Returns:
    # - A new factor which is the pointwise product of the first two factors.
    @staticmethod
    def pointwise_product(f1: Factor, f2: Factor):
        f1_exclusive_variables = []
        f2_exclusive_variables = []
        shared_variables = []
        for variable_state_assignments in f1.table.keys():
            for variable_state_assignment in variable_state_assignments:
                f1_exclusive_variables.append(variable_state_assignment[0])
            break

        for variable_state_assignments in f2.table.keys():
            for variable_state_assignment in variable_state_assignments:
                if variable_state_assignment[0] not in f1_exclusive_variables:
                    f2_exclusive_variables.append(variable_state_assignment[0])
                else:
                    shared_variables.append(variable_state_assignment[0])
                    f1_exclusive_variables.remove(variable_state_assignment[0])
            break

        indices = []
        for f1_variable in f1_exclusive_variables:
            indices.append(f1_variable)
        for shared_variable in shared_variables:
            indices.append(shared_variable)
        for f2_variable in f2_exclusive_variables:
            indices.append(f2_variable)

        new_dict: Dict[Tuple[Tuple[str], ...], float] = {}
        for key_1 in f1.table.keys():
            for key_2 in f2.table.keys():
                new_row = [None] * (len(shared_variables) + len(f1_exclusive_variables) + len(f2_exclusive_variables))
                rows_match = True
                for shared_variable in shared_variables:
                    if not key_1[f1.variable_indices.index(shared_variable)] == key_2[f2.variable_indices.index(shared_variable)]:
                        rows_match = False
                if rows_match:
                    for index in indices:
                        if index in f1_exclusive_variables or index in shared_variables:
                            new_row[indices.index(index)] = key_1[f1.variable_indices.index(index)]
                        elif index in f2_exclusive_variables:
                            new_row[indices.index(index)] = key_2[f2.variable_indices.index(index)]
                    new_row = tuple(new_row)
                    new_dict[new_row] = f1.table[key_1] * f2.table[key_2]

        factor: Factor = Factor(new_dict, indices)
        return factor

    # Sums out a variable from a factor. This is accomplished by identifying every set of rows in the factor which are
    # identical except for the value of the variable to be summed out. For each set of rows whose only difference is the
    # value of the variable to be summed out, a new row key is constructed by removing the value of the variable to be
    # summed out and adjusting the indices of the other variables accordingly. Once all such rows have been identified,
    # the values of each row are summed together.
    # Arguments:
    # - node: A string representing the variable to be summed out.
    # - factor: A factor from which the variable should be summed out.
    # Returns:
    # - new_factor: A modification of factor with the variable summed out.
    @staticmethod
    def sum_out(node: str, factor: Factor) -> Factor:
        new_table: Dict[Tuple[Tuple[str], ...], float] = {}
        new_key_indices: List[int] = []
        for index in factor.variable_indices:
            if not index == node:
                new_key_indices.append(factor.variable_indices.index(index))
        if len(new_key_indices) == 0:
            return False
        row_marked = [False] * len(factor.table.keys())
        for i, key in enumerate(factor.table.keys()):
            if not row_marked[i]:
                new_float: float = 0
                new_float += factor.table[key]
                row_marked[i] = True
                for j, other_key in enumerate(factor.table.keys()):
                    if not row_marked[j]:
                        row_matches = True
                        for index in new_key_indices:
                                if not key[index] == other_key[index]:
                                    row_matches = False
                        if row_matches:
                            row_marked[j] = True
                            new_float += factor.table[other_key]
                row_key = [None] * len(new_key_indices)
                for k in range(len(new_key_indices)):
                    row_key[k] = key[new_key_indices[k]]
                row_key = tuple(row_key)
                new_table[row_key] = new_float

        new_key_index_names = [factor.variable_indices[m] for m in new_key_indices]
        new_factor = Factor(new_table, new_key_index_names)
        return new_factor

    # Normalizes the values of all rows in a factor.
    # Sums the values of all rows, then divides each value by the sum of all values.
    # Arguments:
    # - factor: The factor to be normalized.
    # Returns:
    # - factor: The same factor, normalized.
    @staticmethod
    def normalize(factor: Factor) -> Factor:
        norm: float = 0
        for key in factor.table.keys():
            norm += factor.table[key]
        for key in factor.table.keys():
            factor.table[key] = factor.table[key] / norm
        return factor

    # Used in var_elim to determine which variable to sum out next. var_elim returns the same answer no matter the order
    # in which variables are summed out, but runs very slowly with poor choices of variable ordering.
    # For reference, in an arbitrary order, hailfinder.bif evidence set 0 took more than 9 hours to run, and took
    # less than 10 minutes to run in this order.
    # Given a list of variables and a list of factors, calculates which factor(s) the variable is included in and
    # sums the number of rows for each of those factors. Returns the variable included in the least number of rows.
    # Arguments:
    # - factors: A list of factors from which a variable should be summed out.
    # - variables: A list of strings representing variables which could be summed out.
    # Returns:
    # - The variable which is involved in the least number of rows across all factors.
    def get_next_variable_to_sum_out(self, factors: List[Factor], variables: List[str]) -> str:
        if len(variables) == 0:
            return None
        variable_complexities: List = deepcopy(variables)
        for i in range(len(variable_complexities)):
            count = 0
            for factor in factors:
                if variable_complexities[i] in factor.variable_indices:
                    count += len(factor.table)
            variable_complexities[i] = [variable_complexities[i], count]
        variable_complexities = sorted(variable_complexities, key=lambda variable: variable[1])
        return variable_complexities[0][0]
