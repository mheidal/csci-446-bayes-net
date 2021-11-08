from typing import List, Tuple, Dict

from node import Node
from bayesian_network import BayesianNetwork
from exact_inference_engine import ExactInferenceEngine

from approximate_inference_engine import ApproximateInferenceEngine





def exact_inference_engine_test(bayesian_network: BayesianNetwork, queries: List[str], evidence: List[Tuple[str, str]], title: str):
    engine: ExactInferenceEngine = ExactInferenceEngine(bayesian_network)
    print(engine.elim_ask(queries, evidence).output_to_latex_with_query(queries, title))

def output_evidence_as_latex(evidence: List[Tuple[str, str]], title: str) -> None:
    string = ""
    string += r"\begin{center}" + "\n" + title + r"\\" + "\n" + r"\begin{tabular}{ |c|c| }" + "\n" + r"\hline" + " Variable Name&Value" + r"\\" + "\n"
    for event in evidence:
        string += r"\hline " + event[0] + " & " + event[1] + r"\\" + "\n"
    string += r"\hline " + "\n" + r"\end{tabular}" + "\n" + r"\end{center}"
    print(string)

# Variable elimination:
# - Creates lists of networks, query variables and evidence sets.
# - Iterates through each of these lists to find the probability distribution of each query variable given each evidence
#   set in every network.
# - Outputs each probability distribution in LaTeX format.
# Gibbs sampling: TODO
def main() -> None:
    networks: List[str] = ["alarm.bif", "child.bif", "hailfinder.bif", "insurance.bif", "win95pts.bif"]
    # evidences: Dict[str, List[List[Tuple[str, str]]]] = {
    #     "alarm.bif": [[], [("HRBP", "HIGH"), ("CO", "LOW"), ("BP", "HIGH")],
    #                  [("HRBP", "HIGH"), ("CO", "LOW"), ("BP", "HIGH"), ("HRSAT", "LOW"), ("HREKG", "LOW"),("HISTORY", "TRUE")]],
    #     "child.bif": [[], [("LowerBody02", "<5"),("RUQO2", "12+"),("CO2Report", ">=7.5"),("XrayReport", "Asy/Patchy")],
    #                   [("LowerBody02", "<5"),("RUQO2", "12+"),("CO2Report", ">=7.5"),("XrayReport", "Asy/Patchy"), ("GruntingReport", "yes"), ("LVHReport", "yes"), "Age", "11-30_days"]],
    #     "hailfinder.bif": [[], [("R5Fcst", "XNIL"),("N32StarFcst", "XNIL"),("MountainFCST", "XNIL"),("AreaMoDryAir", "VeryWet")],
    #                       [("R5Fcst", "XNIL"),("N32StarFcst", "XNIL"),("MountainFCST", "XNIL"),("AreaMoDryAir", "VeryWet"),("CombVerMo", "Down"),("AreaMeso_ALS", "Down"),("CurPropConv", "Strong")]],
    #     "insurance.bif": [[], [("Age", "Adolescent"),("GoodStudent", "True"),("SeniorTrain", "False"),("DrivQuality", "Poor")],
    #                       [("Age", "Adolescent"),("GoodStudent", "True"),("SeniorTrain", "False"),("DrivQuality", "Poor"),("MakeModel", "Luxury"),("CarValue", "FiftyThou"),("DrivHistory", "Zero")]],
    #     "win95pts.bif": [[], [("Problem1", "No_Output")],
    #                      [("Problem2", "Too_Long")],
    #                      [("Problem3", "No")],
    #                      [("Problem4", "No")],
    #                      [("Problem5", "No")],
    #                      [("Problem6", "Yes")]
    #                      ]
    # }

    evidences: Dict[str, List[List[Tuple[str, str]]]] = {
        "alarm.bif": [[]],
        "child.bif": [[]],
        "hailfinder.bif": [[]],
        "insurance.bif": [[]],
        "win95pts.bif": [[]]
    }

    queries: Dict[str, List[str]] = {
        "alarm.bif": ["HYPOVOLEMIA", "LVFAILURE", "ERRLOWOUTPUT"],
        "child.bif": ["Disease"],
        "hailfinder.bif": ["SatContMoist", "LLIW"],
        "insurance.bif": ["MedCost", "ILiCost", "PropCost"],
        "win95pts.bif": ["Problem1","Problem2","Problem3","Problem4","Problem5","Problem6"]

    }
    for network in networks:

        bayesian_network: BayesianNetwork = BayesianNetwork(network)
        for i, evidence in enumerate(evidences[network]):
            output_evidence_as_latex(evidence, network + " evidence set " + str(i))
            print()
            for query in queries[network]:
                exact_inference_engine_test(bayesian_network, [query], evidence, "Probability distribution of " + query + " in network " + network + " with evidence set " + str(i))
                print()
    bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="hailfinder.bif")
    # print(bayesian_network)
    # print(f"Nodes: {len(bayesian_network.get_nodes())}")

    # bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="child.bif")
    bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="hailfinder.bif")
    bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="child.bif")
    #bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="hailfinder.bif")
    #print(bayesian_network)

    approximate_inference_engine: ApproximateInferenceEngine = ApproximateInferenceEngine(bayesian_network)
    approximate_inference_engine.gibbs_sampling([],[])

    # """ 3. Hailfinder Netowrk
    # a) Report [SatContMoist, LLIW]
    # b) Little Evidence: RSFcst=XNIL; N32StarFcst=XNIL; MountainFcst=XNIL; AreaMoDryAir=VeryWet.
    # c) Moderate Evidence: RSFcst=XNIL; N32StarFcst=XNIL; MountainFcst=XNIL; AreaMoD-ryAir=VeryWet;
    #    CombVerMo=Down; AreaMeso_ALS=Down; CurPropConv=Strong.
    # """
    # # initialize query
    # query3 = ["SatContMoist", "LLIW"]
    # # initialize evidence
    # bayesian_network.nodes['R5Fcst'].set_as_evidence("XNIL")
    # bayesian_network.nodes['N34StarFcst'].set_as_evidence("XNIL")
    # bayesian_network.nodes['MountainFcst'].set_as_evidence("XNIL")
    # bayesian_network.nodes['AreaMoDryAir'].set_as_evidence("VeryWet")
    # evidence3 = ['R5Fcst', 'N34StarFcst', 'MountainFcst', 'AreaMoDryAir']
    #
    # approximate_inference_engine.gibbs_sampling(query3, evidence3)


# TODO: compute sample, method
# to compute sample
# P(X|e) = a*P(X, e)
#
# = for y in Y
#      prob = P(X,e,y)
# return prob*a

# TODO: pointwise product method

    bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="child.bif")
    # bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="hailfinder.bif")
    print(bayesian_network)
    print(f"Nodes: {len(bayesian_network.get_nodes())}")
    ordering: List[Node] = bayesian_network.topological_ordering()
    print(ordering)
    print(len(ordering))


if __name__ == '__main__':
    main()
