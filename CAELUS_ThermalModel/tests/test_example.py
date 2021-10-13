# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from ThermalModel.ThermalSim import ThermalSim
from ThermalModel.container_inputs import input_geometry
from ThermalModel.atmos_model import model_atmosferic
from ThermalModel.thermal_model import thermal_model


def test_integration():

    # RUN EXAMPLE
    params = input_geometry()
    tm = ThermalSim(params, model_atmosferic, thermal_model)
    t, sol = tm.solve(0, 2000)
        
    # plot results

    plt.plot(t, sol)
    plt.legend([str(i) for i in range(len(sol))])
    plt.xlabel('time')
    plt.ylabel('y(t)')
    plt.show()

