from math import inf
import numpy as np
from numpy.linalg import inv

def model_ode(t, y, model_atmospheric, params, update_node_link):
    """
    t: time
    y: vector of temperatures. In this proble it is:
        y[0]: external wall
        y[1]: internal wall
        y[2]: payload
        y[3]: PCM
        y[4]: air
    model_atmospheric: function
    params
    update_node_link: function
    """

    update = update_node_link(params, t, [y[0], y[3]], model_atmospheric)

    C = update.get_node_capacity()
    K = update.get_link_conduction()
    H = update.get_link_convection()
    F = update.get_external_contribution()

    Incidence = params["incidence_matrix"]
    B = Incidence.dot(np.diag(-H - K)).dot(Incidence.T)

    dT = inv(np.diag(C)).dot(B.dot(y) + F)

    return dT
