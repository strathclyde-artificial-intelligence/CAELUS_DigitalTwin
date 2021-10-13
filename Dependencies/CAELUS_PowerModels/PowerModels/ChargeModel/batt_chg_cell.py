from math import e as e_const, inf

def batt_chg_cell(capacity: float, current: float) -> float:
    """
        param capacity: [Ah]
        param capacity: [Amps]
        returns: Voltage [V]
    """
    # Battery Parameters Extracted from Datasheet
    # Input arguments
    #DoD: The current battery DoD: %
    #E: Energy extracted from battery: Ah
    #If: Current flowing out of the battery (LPF filtered): A
        
    Eo = 4.05  # Exponential voltage 25deg: Volts
    K = 0.0001843      # Polarization constant: V/Ah, or polarization resistance, in Ohms.
    Q =  22     # maximum battery capacity, in Ah.
    A = 0.1      # exponential voltage: V
    B = 2.2      # exponential capacity, in Ah−1
    R = 2/1000 # Battery internal resistance, ohms

    Vcut_off = 2.75   # Cut-off Voltage, in V
    Vcharge = 4.2     # Charge Voltage, in V
    
    Nseries = 1   #Number of cells in series
    Nparr = 1     #Number of cells in parallel
    Q = Q * Nparr
    # Battery Charge (Cell)
    It = capacity
    # print(f"Q {Q} Capacity {capacity} B {B}")
    try:
        Ebatt = Eo - (K * ( Q/(It+(0.1*Q) ) ) * current) - (K * ( Q/(Q-It) ) * It ) + (A * (e_const ** (-B*It)) )
    except Exception as e:
        pass
        Ebatt = -inf
    # Scaling for Battery Pack
    Vbatt = (Ebatt - current*R)*Nseries
        
    # BMS functions (Housekeeping)
    if (Vbatt < Vcut_off*Nseries):
        Vbatt = Vcut_off*Nseries;  # BMS system disconnects battery from sink
    
    if (Vbatt >= Vcharge*Nseries):
        Vbatt = Vcharge*Nseries    # BMS system disconnects battery from source
    return Vbatt
