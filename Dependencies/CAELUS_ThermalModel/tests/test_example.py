# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from ThermalModel.ThermalSim import ThermalSim
from ThermalModel.inputs import input_geometry
from ThermalModel.model_atmospheric import model_atmospheric
from ThermalModel.UpdateNodeLink import UpdateNodeLink
from ThermalModel.model_ode import model_ode


def test_integration():

    # Define Inputs

    initial_time = 0  # [seconds]
    final_time = 10000  # [seconds]
    initial_state = [20, 20, 5, 0, 20]  # temperature: array of 5 elements
                                        # y[0]: external wall. At the intial condition = ambient temperature
                                        # y[1]: internal wall. At the intial condition = ambient temperature
                                        # y[2]: payload. It depends on the package. 5 seems to be a reasonable number
                                        # y[3]: PCM. 0 seems to be a reasonable number
                                        # y[4]: internal container air. At the intial condition = ambient temperature

    # RUN EXAMPLE

    params = input_geometry()
    tm = ThermalSim(params, model_atmospheric, model_ode, UpdateNodeLink, )
    t, sol = tm.solve(initial_time, final_time, initial_state)

    # plot results

    plt.plot(t, sol)
    plt.legend([str(i) for i in range(len(sol))])
    plt.xlabel('time')
    plt.ylabel('y(t)')
    plt.show()
