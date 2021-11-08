from typing import Dict
from typing import List
from typing import Tuple

# Represents a factor.
# Main data structure is a dictionary which represents a truth table. One key to the dictionary is a row of the truth
# table, and the value of that key is the associated value in the truth table.
# Each key is a tuple of strings. Each key represents a unique configuration of values for the variables which are
# included in the factor. Factors are represented in the tuple in the order they appear in the array variable_indices.
# instantiated in make_factor, pointwise_product and sum_out methods of bayesian_network
class Factor():
    def __init__(self, table: Dict, variable_indices: List[str]):
        self.table: Dict[Tuple[Tuple[str, str], ...], float] = table
        self.variable_indices = variable_indices
        self.make_name()

    # Default to_string method. Returns a table representing every configuration of every variable in the factor and
    # the associated value.
    def __str__(self):
        string = ""
        headered = False
        longest_element = ""
        for key in self.table.keys():
            if len(key) > len(longest_element):
                longest_element = key
            for pair in key:
                if len(pair[0]) > len(longest_element):
                    longest_element = pair[0]
                if len(pair[1]) > len(longest_element):
                    longest_element = pair[1]

        for key in self.table.keys():
            if not headered:
                for pair in key:
                    string += pair[0] + str(" " * (len(longest_element) - len(pair[0])))
                    string += " "
                string += " | " + self.name + str(" " * (len(longest_element) - len(self.name)))
                string += "\n-------\n"
                headered = True
            for pair in key:
                string += pair[1] + str(" " * (len(longest_element) - len(pair[1]))) + " "
            string += "| "
            # string += str(100*round(self.table[key], 5)) + "%" + str(" " * (len(longest_element) - len(str(100*round(self.table[key], 5))) - 1))
            string += str(100 * self.table[key]) + "%" + str(
                " " * (len(longest_element) - len(str(100 * self.table[key])) - 1))
            string += "\n"
        return string

    # Creates a string representing which variables are included in the factor. If variables X, Y, and Z are included
    # in the factor, then the string is of the format "phi(X, Y, Z)".
    # Arguments: none.
    # Returns: none.
    def make_name(self):
        factor_name = "phi("
        for i in range(len(self.variable_indices)):
            factor_name += self.variable_indices[i]
            if i < len(self.variable_indices) - 1:
                factor_name += ","
        factor_name += ")"
        self.name = factor_name

    # Returns a string showing a nice-looking, evently-spaced and labeled representation of the probability
    # distributions of all query variables in the factor. Note that this method was used in testing the functionality
    # of other methods, but is not used in the final output of the program.
    # Arguments:
    # - queries: a list of strings representing query variables.
    # Returns:
    # - A string representing a table containing probability distributions of each query variable in the factor.
    def output_query_only(self, queries: List[str]):
        relevant_queries = []
        for index in self.variable_indices:
            if index in queries:
                relevant_queries.append(index)
        string = ""
        headered = False
        longest_element = ""
        for key in self.table.keys():
            if len(key) > len(longest_element):
                longest_element = key
            for pair in key:
                if pair[0] in relevant_queries:
                    if len(pair[0]) > len(longest_element):
                        longest_element = pair[0]
                    if len(pair[1]) > len(longest_element):
                        longest_element = pair[1]

        for key in self.table.keys():
            if not headered:
                for pair in key:
                    if pair[0] in relevant_queries:
                        string += pair[0] + str(" " * (len(longest_element) - len(pair[0])))
                        string += " "
                string += " | " + self.name + str(" " * (len(longest_element) - len(self.name)))
                string += "\n-------\n"
                headered = True
            for pair in key:
                if pair[0] in relevant_queries:
                    string += pair[1] + str(" " * (len(longest_element) - len(pair[1]))) + " "
            string += "| "
            # string += str(100*round(self.table[key], 5)) + "%" + str(" " * (len(longest_element) - len(str(100*round(self.table[key], 5))) - 1))
            string += str(100 * self.table[key]) + "%" + str(
                " " * (len(longest_element) - len(str(100 * self.table[key])) - 1))
            string += "\n"
        return string

    # Returns a string representation of the probabilities of all query variables in a factor.
    # String is formatted in LaTeX table format to permit easy copy-and-paste into a document.
    # Arguments:
    # - queries: a list of strings representing query variables.
    # - title: the title of the table to be produced.
    # Returns:
    # - a string formatted in LaTeX displaying the probability distribution of each query variable in the factor.
    def output_to_latex_with_query(self, queries: List[str], title: str):
        string = ""
        string += r"\begin{center}" + "\n" + title + r"\\" + "\n" + r"\begin{tabular}{ |c|c|c| }" + "\n" + r"\hline" + " Variable Name&Value&Probability" + r"\\" + "\n"
        for key in self.table.keys():
            for pair in key:
                if pair[0] in queries:
                    string += r"\hline " + pair[0] + " & " + pair[1] + " & " + str(round(100 * self.table[key], 5)) + r"\%" + r"\\" + "\n"
        string += r"\hline " + "\n" + r"\end{tabular}" + "\n" + r"\end{center}"
        return string.replace("_", r"\_")