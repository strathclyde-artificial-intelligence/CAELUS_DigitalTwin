"""
Created on Sat Oct  9 16:40:24 2021

@author: gianlucafilippi
"""

from math import pi
import numpy as np
from functools import lru_cache

class ODEMatrices():

    @staticmethod
    def spreading_resistance(r1, r2, t, k, h):
        epsilon = r1/r2
        tau = t / r2
        bi = (h * r2) / k
        l = pi + 1/(1/ (epsilon * pow(pi,0.5)) )
        phi = (np.tanh(l * tau) + l/bi) / (1+ l/bi * np.tanh(l*tau))
        psi = (epsilon*tau)/pow(pi,0.5) + 1/pow(pi,0.5)*(1-epsilon)*phi

        return psi / (k*r1*pow(pi,0.5))

    def __init__(self, params):
        self.__params = params

    def get_param(self, param_name):
        if param_name in self.__params:
            return self.__params[param_name]
        raise Exception(f'Requested invalid parameter name "{param_name}"')

    @lru_cache
    def get_C(self):
        # -------------- heat capcity ------------------------
        # node 1 : external wall / payload

        C1 = self.get_param("container_V")\
            * self.get_param("container_rho")\
            * self.get_param("container_cp")   # J K-1

        # node 2 : internal wall / payload
        C2 = self.get_param("container_V")\
            * self.get_param("container_rho")\
            * self.get_param("container_cp")   # J K-1

        # node 3 : payload
        C3 = self.get_param("payload_V")\
            * self.get_param("payload_rho")\
            * self.get_param("payload_cp")   # J K-1

        C4 = 0

        # node 5 : air
        C5 = self.get_param("air_V")\
            * self.get_param("air_rho")\
            * self.get_param("air_cp")   # J K-1
        
        # -------------------------------------------------
        return np.array([C1, C2, C3, C4, C5, 0])

    @lru_cache
    def get_K(self):
        # from "square" to "circular" geometry
        r_contianer = pow(self.get_param("container_Aout") / pi, 0.5)
        r_brick = pow(self.get_param("payload_A_cond") / pi, 0.5)
        r_PCM = pow(self.get_param("PCM_A_cond") / pi, 0.5)

        R_c2b = ODEMatrices.spreading_resistance(r_brick, r_contianer, self.get_param('Dx_container'), self.get_param("container_k"), self.get_param("air_hf"))
        R_PCM2b = ODEMatrices.spreading_resistance(r_brick, r_PCM, self.get_param("PCM_z"), self.get_param("PCM_ks"), self.get_param("air_hn"))

        # ----------------- conductivity ------------------------

        # node 1 (external wall) <-> node 2 (internal wall/payload)
        K_1_2 = self.get_param("container_k") * self.get_param("container_Aout") / self.get_param('Dx_container')
        K_2_1 = K_1_2

        # node 2 (internal wall/payload)  <-> node 3 (payload)
        R_23 = pow( self.get_param("payload_k") * self.get_param("payload_A_cond") / (self.get_param("payload_z")/2) , -1)
        R_tot = R_23+R_c2b
        K_tot = pow(R_tot, -1)

        K_3_2 = K_tot
        K_2_3 = K_3_2 # R_23^-1

        # node 3 (payload)  <-> node 4 (PCM)                 N.B.! ONLY PAYLOAD PART
        R_34 = pow( self.get_param("payload_k") * self.get_param("PCM_A_cond") / (self.get_param("payload_z")/2),  -1)
        # R_tot = R_34+R_PCM2b
        
        K_4_3 = pow(R_34, -1)
        K_3_4 = K_4_3 # R_tot^(-1)
        
        Kpartial = K_4_3
        
        return np.array([
            [0, K_1_2, 0, 0, 0, 0],
            [K_2_1, 0, K_2_3, 0, 0, 0],
            [0, K_3_2, 0, K_3_4, 0, 0],
            [0, 0, K_4_3, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0]
        ])
        # ---------------------------------------------------------

    @lru_cache
    def get_H(self):
        # --------- convection -------------
        # node 1 (internal wall)  <-> node 6 (external air)
        H_1_6 = self.get_param("air_hn") * self.get_param("container_Aout")
        H_6_1 = H_1_6

        # node 2 (internal wall)  <-> node 5 (air)
        H_2_5 = self.get_param("air_hn") * self.get_param("container_Ain_conv")
        H_5_2 = H_2_5

        # node 3 (payload)  <-> node 5 (air)
        H_3_5 = self.get_param("air_hn") * self.get_param("payload_A_conv")
        H_5_3 = H_3_5

        # node 4 (PCM)  <-> node 5 (air)
        H_4_5 = self.get_param("air_hn") * self.get_param("PCM_A_conv")
        H_5_4 = H_4_5
        
        return np.array([
            [0, 0, 0, 0, 0, H_1_6],
            [0, 0, 0, 0, H_2_5, 0],
            [0, 0, 0, 0, H_3_5, 0],
            [0, 0, 0, 0, H_4_5, 0],
            [0, H_5_2, H_5_3, H_5_4, 0, 0],
            [H_6_1, 0, 0, 0, 0, 0]
        ])
        # ----------------------------------

    @lru_cache
    def get_R(self):
        return [np.zeros(6) for _ in range(6)]
    
    @lru_cache
    def get_Q(self):
        return np.zeros(6)
