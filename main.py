from typing import List, Tuple, Dict

from node import Node
from bayesian_network import BayesianNetwork
from exact_inference_engine import ExactInferenceEngine


def exact_inference_engine_test(bayesian_network: BayesianNetwork, queries: List[str], evidence: List[Tuple[str, str]]):
    engine: ExactInferenceEngine = ExactInferenceEngine(bayesian_network)
    print(engine.elim_ask(queries, evidence))

def main() -> None:
    # bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="child.bif")
    networks: List[str] = ["alarm.bif", "child.bif", "hailfinder.bif", "insurance.bif", "win95pts.bif"]
    # networks: List[str] = ["win95pts.bif"]
    # networks: List[str] = ["child.bif"]
    evidences: Dict[str, List[List[Tuple[str, str]]]] = {
        "alarm.bif": [[("HRBP", "HIGH"), ("CO", "LOW"), ("BP", "HIGH")],
                     [("HRBP", "HIGH"), ("CO", "LOW"), ("BP", "HIGH"), ("HRSAT", "LOW"), ("HREKG", "LOW"),("HISTORY", "TRUE")]],
        "child.bif": [[("LowerBody02", "<5"),("RUQO2", "12+"),("CO2Report", ">=7.5"),("XrayReport", "Asy/Patchy")],
                      [("LowerBody02", "<5"),("RUQO2", "12+"),("CO2Report", ">=7.5"),("XrayReport", "Asy/Patchy"), ("GruntingReport", "yes"), ("LVHReport", "yes"), "Age", "11-30_days"]],
        "hailfinder.bif": [[("R5Fcst", "XNIL"),("N32StarFcst", "XNIL"),("MountainFCST", "XNIL"),("AreaMoDryAir", "VeryWet")],
                          [("R5Fcst", "XNIL"),("N32StarFcst", "XNIL"),("MountainFCST", "XNIL"),("AreaMoDryAir", "VeryWet"),("CombVerMo", "Down"),("AreaMeso_ALS", "Down"),("CurPropConv", "Strong")]],
        "insurance.bif": [[("Age", "Adolescent"),("GoodStudent", "True"),("SeniorTrain", "False"),("DrivQuality", "Poor")],
                          [("Age", "Adolescent"),("GoodStudent", "True"),("SeniorTrain", "False"),("DrivQuality", "Poor"),("MakeModel", "Luxury"),("CarValue", "FiftyThou"),("DrivHistory", "Zero")]],
        "win95pts.bif": [[("Problem1", "No_Output")],
                         [("Problem2", "Too_Long")],
                         [("Problem3", "No")],
                         [("Problem4", "No")],
                         [("Problem5", "No")],
                         [("Problem6", "Yes")]
                         ]
    }
    queries: Dict[str, List[str]] = {
        "alarm.bif": ["HYPOVOLEMIA", "LVFAILURE", "ERRLOWOUTPUT"],
        "child.bif": ["Disease"],
        "hailfinder.bif": ["SatContMoise", "LLIW"],
        "insurance.bif": ["MedCost", "ILiCost", "PropCost"],
        "win95pts.bif": ["Problem1","Problem2","Problem3","Problem4","Problem5","Problem6"]

    }
    for network in networks:
        print("Network is", network)
        bayesian_network: BayesianNetwork = BayesianNetwork(network)
        for evidence in evidences[network]:
            for query in queries[network]:
                exact_inference_engine_test(bayesian_network, [query], evidence)

    bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="hailfinder.bif")
    # print(bayesian_network)
    # print(f"Nodes: {len(bayesian_network.get_nodes())}")

    # bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="child.bif")
    bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="hailfinder.bif")
    print(bayesian_network)
    print(f"Nodes: {len(bayesian_network.get_nodes())}")
    ordering: List[Node] = bayesian_network.topological_ordering()
    print(ordering)
    print(len(ordering))


if __name__ == '__main__':
    main()
