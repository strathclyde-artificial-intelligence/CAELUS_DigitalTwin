from math import inf
import numpy as np


def thermal_model(t, T, PCM_model, atmos_model, params):
    """
    Explain me!
    """

    dT = [0, 0, 0, 0, 0, 0]

    C = params["matrix_C"]
    K = params["matrix_K"]
    H = params["matrix_H"]
    R = params["matrix_R"]
    Q = params["matrix_Q"]

    # ambient temperature from Atmosferic model
    T[5] = atmos_model(t)

    # update K and H
    K, H = PCM_model(T, params, C, K, H)

    # define matrix equation
    TT_row = np.array([ [T[0]]*6, [T[1]]*6, [T[2]]*6, [T[3]]*6, [T[4]]*6, [T[5]]*6 ])
    TT_col = TT_row.transpose()
    TT = TT_row - TT_col
    TTR = pow(TT_row, 4) - pow(TT_col, 4)

    dT = 1/C * (np.diag(np.dot(H, TT) + np.dot(K, TT) + np.dot(R, TTR)) + Q)
    dT[5] = 0

    return dT
