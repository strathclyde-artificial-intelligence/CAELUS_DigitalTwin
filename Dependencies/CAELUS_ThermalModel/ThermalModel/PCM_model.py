#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 14:38:17 2021

@author: gianlucafilippi
"""

def PCM_model(T, params, C, K, H):



    # PCM interpolation
    K4 = []
    L = (T[3]-params["PCM_t1"]) / (params["PCM_t2"]-params["PCM_t1"])
    # PCM properties
    if L < 0:
        Ln = 0
        Mass_pcm = params["PCM_rho"] * params["PCM_V"]
        cp = params["PCM_cps"]
        K4 = params["PCM_ks"] * params["PCM_A_cond"] / (params["PCM_z"]/2)

    elif (0 <= L < 1):
        Ln = L
        Mass_pcm = params["PCM_rho"] * params["PCM_V"]
        cp = (params["PCM_cpl"] * (T[3] - params["PCM_t1"]) + params["PCM_h"] + params["PCM_cps"] * ((params["PCM_t2"] - T[3])) ) / (params["PCM_t2"] - params["PCM_t1"])
        # keff =   (pcm_prop.k_l*(T[4]-pcm_prop.Tm1) + pcm_prop.k_s*(pcm_prop.Tm2-T[4]) )/ (pcm_prop.Tm2-pcm_prop.Tm1)
        keff = params["PCM_ks"] + L * (params["PCM_kl"] - params["PCM_ks"])
        K4 = keff * params["PCM_A_cond"] / (params["PCM_z"]/2)

    else:
        Ln = 1
        Mass_pcm = params["PCM_rho"] * params["PCM_V"]
        cp = params["PCM_cpl"]
        K4 = params["PCM_kl"] * params["PCM_A_cond"] / (params["PCM_z"]/2)

    
    Kpartial = K[3,2]
    Hpartial = H[3,4]
    
    # update 
    K4new = pow((1/Kpartial + 1/K4), -1)
    K[2,3] = K4new
    K[3,2] = K4new

    C[3] = Mass_pcm * cp

    H45new = pow((1/Hpartial + 1/K4), -1)
    H[3,4] = H45new
    H[4,3] = H45new
    
    
    return K, H