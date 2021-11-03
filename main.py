from bayesian_network import BayesianNetwork






def main() -> None:
    # bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="child.bif")
    bayesian_network: BayesianNetwork = BayesianNetwork(bif_file_name="hailfinder.bif")
    print(bayesian_network)

# TODO: compute sample, method
# to compute sample
# P(X|e) = a*P(X, e)
#
# = for y in Y
#      prob = P(X,e,y)
# return prob*a

# TODO: pointwise product method



if __name__ == '__main__':
    main()
