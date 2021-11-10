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
    initial_state = [20, 20, 5, 0, 20]  # temperature: array of 5 elements [Kelvin]

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
