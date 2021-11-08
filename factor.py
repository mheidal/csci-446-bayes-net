from typing import Dict
from typing import List
from typing import Tuple

# instantiated in make_factor, pointwise_product and sum_out methods of bayesian_network
class Factor():
    def __init__(self, table: Dict, variable_indices: List[str]):
        self.table: Dict[Tuple[Tuple[str, str], ...], float] = table
        self.variable_indices = variable_indices
        self.make_name()

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

    def make_name(self):
        factor_name = "phi("
        for i in range(len(self.variable_indices)):
            factor_name += self.variable_indices[i]
            if i < len(self.variable_indices) - 1:
                factor_name += ","
        factor_name += ")"
        self.name = factor_name

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

    def output_to_latex_with_query(self, queries, title):
        string = ""
        string += r"\begin{center}" + "\n" + title + r"\\" + "\n" + r"\begin{tabular}{ |c|c|c| }" + "\n" + r"\hline" + " Variable Name&Value&Probability" + r"\\" + "\n"
        for key in self.table.keys():
            for pair in key:
                if pair[0] in queries:
                    string += r"\hline " + pair[0] + " & " + pair[1] + " & " + str(round(100 * self.table[key], 5)) + r"\%" + r"\\" + "\n"
        string += r"\hline " + "\n" + r"\end{tabular}" + "\n" + r"\end{center}"
        return string