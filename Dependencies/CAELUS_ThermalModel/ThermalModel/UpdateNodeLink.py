"""
Created on Sat Oct  9 16:40:24 2021

@author: gianlucafilippi
"""

from math import pi
import numpy as np
from functools import lru_cache


class UpdateNodeLink:

    @staticmethod
    def model_pcm_cp(t, params):
        if t < params["PCM_t1"]:
            cp = params["PCM_cps"]
        elif params["PCM_t1"] <= t < params["PCM_t2"]:
            cp = (params["PCM_cps"] * (params["PCM_t2"] - t)
                  + params["PCM_cpl"] * (t - params["PCM_t1"])
                  + params["PCM_h"]) \
                 / (params["PCM_t2"] - params["PCM_t1"])
        else:
            cp = params["PCM_cpl"]

        return cp

    @staticmethod
    def model_pcm_k(t, params):
        if t < params["PCM_t1"]:
            k = params["PCM_ks"]
        elif params["PCM_t1"] <= t < params["PCM_t2"]:
            norm_t = (t - params["PCM_t1"]) / (params["PCM_t2"] - params["PCM_t1"])
            k = params["PCM_ks"] + norm_t * (params["PCM_kl"] - params["PCM_ks"])
        else:
            k = params["PCM_kl"]

        return k

    @staticmethod
    def spreading_resistance(r1, r2, t, k, h):
        epsilon = r1 / r2
        tau = t / r2
        bi = (h * r2) / k
        l = pi + 1 / (1 / (epsilon * pow(pi, 0.5)))
        phi = (np.tanh(l * tau) + l / bi) / (1 + l / bi * np.tanh(l * tau))
        psi = (epsilon * tau) / pow(pi, 0.5) + 1 / pow(pi, 0.5) * (1 - epsilon) * phi

        return psi / (k * r1 * pow(pi, 0.5))

    def __init__(self, params, time, temperature, model_atmospheric):
        self.__params = params
        self.__time = time
        self.__temperature = temperature
        self.__model_atmospheric = model_atmospheric

    def get_param(self, param_name):
        if param_name in self.__params:
            return self.__params[param_name]
        raise Exception(f'Requested invalid parameter name "{param_name}"')

    # @lru_cache
    def get_node_capacity(self):
        # -------------- heat capacity ------------------------

        capacity = np.empty(5, dtype=float)

        # node 0 : external wall / payload
        capacity[0] = self.get_param("container_V") / 2 \
            * self.get_param("container_rho") \
            * self.get_param("container_cp")  # J K-1

        # node 1 : internal wall / payload
        capacity[1] = self.get_param("container_V") / 2\
            * self.get_param("container_rho") \
            * self.get_param("container_cp")  # J K-1

        # node 2 : payload
        capacity[2] = self.get_param("payload_V") \
            * self.get_param("payload_rho") \
            * self.get_param("payload_cp")  # J K-1

        # node 3 : PCM
        capacity[3] = self.get_param("PCM_V") \
            * self.get_param("PCM_rho") \
            * UpdateNodeLink.model_pcm_cp(self.__temperature[1], self.__params)

        # node 4 : air
        capacity[4] = self.get_param("air_V") \
            * self.get_param("air_rho") \
            * self.get_param("air_cp")  # J K-1

        return np.array(capacity)

    # @lru_cache
    def get_link_conduction(self):

        # ----------------- spreading resistance ------------------------
        # from "square" to "circular" geometry
        r_container = pow(self.get_param("container_Aout") / pi, 0.5)
        r_brick = pow(self.get_param("payload_A_cond") / pi, 0.5)
        r_PCM = pow(self.get_param("PCM_A_cond") / pi, 0.5)

        R_c2b = UpdateNodeLink.spreading_resistance(r_brick, r_container, self.get_param('Dx_container'),
                                                    self.get_param("container_k"), self.get_param("air_hf"))
        R_PCM2b = UpdateNodeLink.spreading_resistance(r_brick, r_PCM, self.get_param("PCM_z"), self.get_param("PCM_ks"),
                                                      self.get_param("air_hn"))

        # ----------------- conductivity ------------------------

        # node 0 (external wall) <-> node 1 (internal wall/payload)
        K_0_1 = self.get_param("container_k") * self.get_param("container_Aout") / self.get_param('Dx_container')

        # node 1 (internal wall/payload)  <-> node 2 (payload)
        R_1_2_pl = (self.get_param("payload_z") / 2) / self.get_param("payload_k") * self.get_param("payload_A_cond")
        K_1_2 = pow(R_1_2_pl + R_c2b, -1)

        # node 2 (payload)  <-> node 3 (PCM)
        R_2_3_pl = self.get_param("payload_z") / 2 \
            / self.get_param("payload_k") \
            / self.get_param("PCM_A_cond")
        R_pcm = self.get_param("PCM_z") / 2\
            / UpdateNodeLink.model_pcm_k(self.__temperature[1], self.__params) \
            / self.get_param("PCM_A_cond")
        K_2_3 = pow(R_pcm + R_2_3_pl + R_PCM2b, -1)

        K_vector = [0, 0, 0, 0, 0, 0, 0]
        K_vector[0] = K_0_1  # link 0: node 0 (external wall) -> node 1 (internal wall)
        K_vector[1] = K_1_2  # link 1: node 1 (internal wall) -> node 2 (payload)
        K_vector[2] = K_2_3  # link 2: node 2 (payload) -> node 3 (PCM)
        K_vector[3] = 0  # link 3: node 1 (internal wall) -> node 3 (PCM)
        K_vector[4] = 0  # link 4: node 3 (PCM) -> node 4 (internal air)
        K_vector[5] = 0  # link 5: node 1 (internal wall) -> node 4 (internal air)
        K_vector[6] = 0  # link 6: node 2 (payload) -> node 4 (internal air)

        return np.array(K_vector)

    def get_link_convection(self):

        # node 2 (internal wall)  <-> node 5 (air)
        H_1_4 = self.get_param("air_hn") * self.get_param("container_Ain_conv")

        # node 3 (payload)  <-> node 5 (air)
        H_2_4 = self.get_param("air_hn") * self.get_param("payload_A_conv")

        # node 4 (PCM)  <-> node 5 (air)
        H_3_4 = self.get_param("air_hn") * self.get_param("PCM_A_conv")

        H_vector = [0, 0, 0, 0, 0, 0, 0]
        H_vector[0] = 0  # link 0: node 0 (external wall) -> node 1 (internal wall)
        H_vector[1] = 0  # link 1: node 1 (internal wall) -> node 2 (payload)
        H_vector[2] = 0  # link 2: node 2 (payload) -> node 3 (PCM)
        H_vector[3] = 0  # link 3: node 1 (internal wall) -> node 3 (PCM)
        H_vector[4] = H_3_4  # link 4: node 3 (PCM) -> node 4 (internal air)
        H_vector[5] = H_1_4  # link 5: node 1 (internal wall) -> node 4 (internal air)
        H_vector[6] = H_2_4  # link 6: node 2 (payload) -> node 4 (internal air)

        return np.array(H_vector)

    def get_external_contribution(self):

        # node 1 (internal wall)  <-> external air
        H = self.get_param("air_hn") * self.get_param("container_Aout")
        t_atmospheric = self.__model_atmospheric(self.__time)
        F = H * (t_atmospheric - self.__temperature[0])
        return np.array([F, 0, 0, 0, 0])
