from math import e as e_c

# depth_of_discharge: The current battery depth_of_discharge:
# E: Energy extracted from battery: Ah
# current: Current flowing out of the battery (LPF filtered): A
def batt_disc(depth_of_discharge, capacity, current) -> [float, float]:
        
    Eo = 4.05   # Exponential voltage 25deg: Volts
    K = 0.0001843       # Polarization constant: V/Ah, or polarization resistance, in Ohms.
    It = 0      # extracted capacity: Ah
    Q =  22      # maximum battery capacity, in Ah.
    A = 0.5       # exponential voltage: V
    B = 1       # exponential capacity, in Ah−1
    R = 2/1000  # Battery internal resistance, ohms

    Vcut_off = 2.75    # Cut-off Voltage, in V
    Vcharge = 4.2      # Charge Voltage, in V
    
    Nseries = 6    #Number of cells in series
    Nparr = 1      #Number of cells in parallel
    Q = Q * Nparr

    # Battery Discharge (Cell)
    It = (depth_of_discharge*Q/100)+capacity
    depth_of_discharge = (It/Q)*100
    Ebatt = Eo - (K * ( Q/(Q-It) ) * current) - (K * ( Q/(Q-It) ) * It ) + (A * e_c**(-B* It) ) 
    
    
    # Scaling for Battery Pack
    v_batt = (Ebatt - current*R)*Nseries
        
    # BMS functions (Housekeeping)
    if (v_batt < Vcut_off*Nseries):
        v_batt = Vcut_off*Nseries  # BMS system disconnects battery from sink

    
    if (v_batt >= Vcharge*Nseries):
        v_batt = Vcharge*Nseries    # BMS system disconnects battery from source

    return depth_of_discharge, v_batt