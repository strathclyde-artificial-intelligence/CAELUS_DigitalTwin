from math import e as e_k, exp, inf
#DoD: The current battery DoD: #
#capacity: Energy extracted from battery: Ah
#current: Current flowing out of the battery (LPF filtered): A
# returns: battery voltage
def batt_chg(capacity, current, n_series) -> float:

    Eo = 4.05   # Exponential voltage 25deg: Volts
    K = 0.0001843       # Polarization constant: V/Ah, or polarization resistance, in Ohms.
    Q =  22      # maximum battery capacity, in Ah.
    A = 0.1       # exponential voltage: V
    B = 2.2       # exponential capacity, in Ah−1
    R = 2/1000  # Battery internal resistance, ohms

    Vcut_off = 2.75    # Cut-off Voltage, in V
    Vcharge = 4.2      # Charge Voltage, in V
    
    Nparr = 1      #Number of cells in parallel
    Q = Q * Nparr
    ## Battery Charge (Cell)
    It = capacity

    try:
        aux = (A * exp(-B* It) )
        Ebatt = Eo - (K * ( Q/(It+(0.1*Q) ) ) * current) - (K * ( Q/(Q-It) ) * It ) + aux
    except Exception as e:
        Ebatt = -inf

        
    ## Scaling for Battery Pack
    v_batt = (Ebatt - current*R)*n_series
        
    ## BMS functions (Housekeeping)
    if (v_batt < Vcut_off*n_series):
        v_batt = Vcut_off*n_series  # BMS system disconnects battery from sink
    
    if (v_batt >= Vcharge*n_series):
        v_batt = Vcharge*n_series    # BMS system disconnects battery from source

    return v_batt
