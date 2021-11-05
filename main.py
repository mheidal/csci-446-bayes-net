from bayesian_network import BayesianNetwork
from approximate_inference_engine import ApproximateInferenceEngine






def main() -> None:
    # bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="child.bif")
    bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="hailfinder.bif")
    #print(bayesian_network)

    approximate_inference_engine: ApproximateInferenceEngine = ApproximateInferenceEngine(bayesian_network)

    """ 3. Hailfinder Netowrk
    a) Report [SatContMoist, LLIW]
    b) Little Evidence: RSFcst=XNIL; N32StarFcst=XNIL; MountainFcst=XNIL; AreaMoDryAir=VeryWet.
    c) Moderate Evidence: RSFcst=XNIL; N32StarFcst=XNIL; MountainFcst=XNIL; AreaMoD-ryAir=VeryWet; 
       CombVerMo=Down; AreaMeso_ALS=Down; CurPropConv=Strong.
    """
    # initialize query
    query3 = ["SatContMoist", "LLIW"]
    # initialize evidence
    bayesian_network.nodes['R5Fcst'].set_as_evidence("XNIL")
    bayesian_network.nodes['N34StarFcst'].set_as_evidence("XNIL")
    bayesian_network.nodes['MountainFcst'].set_as_evidence("XNIL")
    bayesian_network.nodes['AreaMoDryAir'].set_as_evidence("VeryWet")
    evidence3 = ['R5Fcst', 'N34StarFcst', 'MountainFcst', 'AreaMoDryAir']

    approximate_inference_engine.gibbs_sampling(query3, evidence3)


# TODO: compute sample, method
# to compute sample
# P(X|e) = a*P(X, e)
#
# = for y in Y
#      prob = P(X,e,y)
# return prob*a

# TODO: pointwise product method

    print(bayesian_network)
    print(f"Nodes: {len(bayesian_network.get_nodes())}")


if __name__ == '__main__':
    main()
