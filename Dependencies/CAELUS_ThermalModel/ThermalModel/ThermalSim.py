import numpy as np
from scipy.integrate import odeint


SIM_STATE_SPACE_SIZE = 5


class ThermalSim:

    def __init__(self, params, atmospheric_model, ode_model, update_node_link):
        self.__params = params
        self.__model_atmospheric = atmospheric_model
        self.__model_ode = ode_model
        self.__update_node_link = update_node_link

    def solve(self,
              time_start,
              time_end,
              initial_state=None,
              min_step=0,
              max_step=0):
        if initial_state is None:
            initial_state = [0] * SIM_STATE_SPACE_SIZE

        t = np.linspace(time_start, time_end)
        sol = odeint(self.__model_ode, initial_state, t,
                     args=(self.__model_atmospheric, self.__params, self.__update_node_link), tfirst=True, hmax=max_step, hmin=min_step)
        return t, sol
