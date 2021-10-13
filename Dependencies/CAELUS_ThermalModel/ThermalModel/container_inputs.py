#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 16:40:24 2021

@author: Gianluca Filippi
"""

from .ODEMatrices import ODEMatrices


"""
define parameters
"""


def input_geometry():

    # ------------------------------
    # DEFINE INPUTS
    # ------------------------------

    Dx_container = .02

    # container
    container_xin = .236  # x in [m]
    container_yin = .158  # y in
    container_zin = .089  # z in
 
    # payload
    payload_x = .100    # x [m]
    payload_y = .052    # y
    payload_z = .039    # z
    
    # PCM
    PCM_x = .198        # x  [m]
    PCM_y = .156        # y
    PCM_z = .011        # z    

    # container
    container_k = 0.015      # conductivity k [W m-1 K-1] 0.039
    container_epsilon = .05  # emissivity ϵ
    container_cp = 1.5e3     # specific heat cp [J kg-1 K-1]
    container_rho = 20.0     # density ρ [kg m-3]

    # payload
    payload_k = 5          # conductivity k [W m-1 K-1]
    payload_epsilon = .05  # emissivity ϵ
    payload_cp = 4.186e3   # cp [J kg-1 K-1]
    payload_rho = 1000     # density ρ [kg m-3]

    # PCM
    PCM_ks = .126      # conductivity solid k [W m-1 K-1]
    PCM_kl = .145      # conductivity liquid k [W m-1 K-1]
    PCM_epsilon = .05  # emissivity ϵ
    PCM_cps = 1.4e3    # specific heat solid cp [J kg-1 K-1]
    PCM_cpl = 1.8e3    # specific heat liquid  cp [J kg-1 K-1]
    PCM_rho = 868      # density ρ [kg m-3]
    PCM_t1 = 4         # T1 melting window
    PCM_t2 = 6         # T2 melting window
    PCM_h = 183e3      # H latent

    # air
    air_cp = 1.5e3     # specific heat  cp [J kg-1 K-1]
    air_rho = 1.225    # density ρ [kg m-3]
    air_hn = 4         # coefficient of natural convection
    air_hf = 25        # coefficient of forced convection

    # ------------------------------
    # THERMAL PROPERTIES
    # ------------------------------

    # container
    container_xout = container_xin + 2*Dx_container    # x out
    container_yout = container_yin + 2*Dx_container    # y out
    container_zout = container_zin + 2*Dx_container    # z out
    container_Ain = 2 * (container_xin * container_yin + container_xin * container_zin + container_yin * container_zin)
    container_Aout = 2 * (container_xout * container_yout + container_xout * container_zout + container_yout * container_zout)
    container_Ain_cond = payload_x * payload_y
    container_Ain_conv = container_Ain - container_Ain_cond
    container_V_in = container_xin * container_yin * container_zin
    container_V = container_xout * container_yout * container_zout - container_V_in
    
    # payload
    payload_A_cond = container_Ain_cond
    payload_A_conv = 2 * (payload_x * payload_z + payload_y * payload_z)
    payload_V = payload_x * payload_y * payload_z
    
    # PCM
    PCM_A_cond = payload_A_cond
    PCM_A_conv = 2 * (PCM_x * PCM_y + PCM_x * PCM_z + PCM_y * PCM_z) - payload_A_cond
    PCM_V = PCM_x * PCM_y * PCM_z

    # air
    air_V = container_V_in - payload_V - PCM_V

    # ------------------------------   
    # OUTPUT
    # ------------------------------   
    
    inputs = {
      "Dx_container": Dx_container,  
      "container_xin": container_xin,
      "container_yin": container_yin,
      "container_zin": container_zin,
      "container_xout": container_xout,
      "container_yout": container_yout,
      "container_zout": container_zout,
      "container_Ain": container_Ain,
      "container_Aout": container_Aout,
      "container_Ain_cond": container_Ain_cond,
      "container_Ain_conv": container_Ain_conv,
      "container_V": container_V,
      "container_k": container_k,
      "container_epsilon": container_epsilon,
      "container_cp": container_cp,
      "container_rho": container_rho,
      
      "payload_x": payload_x,
      "payload_y": payload_y,
      "payload_z": payload_z,
      "payload_A_cond": payload_A_cond,
      "payload_A_conv": payload_A_conv,
      "payload_V": payload_V,
      "payload_k": payload_k,
      "payload_epsilon": payload_epsilon,
      "payload_cp": payload_cp,
      "payload_rho": payload_rho,
      
      "PCM_x": PCM_x,
      "PCM_y": PCM_y,
      "PCM_z": PCM_z,
      "PCM_A_cond": PCM_A_cond,
      "PCM_A_conv": PCM_A_conv,
      "PCM_V": PCM_V,
      "PCM_ks": PCM_ks,
      "PCM_kl": PCM_kl,
      "PCM_epsilon": PCM_epsilon,
      "PCM_cps": PCM_cps,
      "PCM_cpl": PCM_cpl,
      "PCM_rho": PCM_rho,
      "PCM_t1": PCM_t1,
      "PCM_t2": PCM_t2,
      "PCM_h": PCM_h,
     
      "air_V": air_V,
      "air_cp": air_cp,
      "air_rho": air_rho,
      "air_hn": air_hn,
      "air_hf": air_hf,
      }

    # ------------------------------   
    # add ODE MATRICES
    # ------------------------------   
    
    ode_matrices = ODEMatrices(inputs)

    inputs['matrix_C'] = ode_matrices.get_C()
    inputs['matrix_K'] = ode_matrices.get_K()
    inputs['matrix_H'] = ode_matrices.get_H()
    inputs['matrix_R'] = ode_matrices.get_R()
    inputs['matrix_Q'] = ode_matrices.get_Q()

    return inputs






