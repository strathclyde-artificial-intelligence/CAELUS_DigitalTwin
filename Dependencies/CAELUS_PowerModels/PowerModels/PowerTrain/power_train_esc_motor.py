from math import sqrt, pi, inf
from cmath import sqrt as csqrt
from typing import Tuple

#   This function is designed to represent the Electronic speed controller
#   and motor for each motor on the Avy Aera Drone. 
#   This function is specific to the Avy Aera drone as it uses the
#   motor parameters and constants provided by Avy for their drone.
#   
#   INPUT ARGUMENTS
#   w_ref:      Motor Speed reference (-1 to 1) provided from Px4 to the ESC
#   m_init:     The last state of Modulation Index from a database
#   v_batt:      The Source (Battery) voltage, provided by a battery
#               discharge function in a feedback loop (or database)
#   dT:         Sample time of the model: in hours (i.e. 1 sec =  1/3600)
#
#   OUTPUTS
#   w:          The motor speed value provided from Px4 to an ESC
#   thrust:     The thrust produced under current conditions
#   mod:        The current state of Modulation Index to store in a database
#   Qcon:       Energy Capacity (Ah) consumed, to be sent to battery model
#   Idis:       The current demand from the system
#   
#   ASSUMPTIONS   
#   tau_electrical << tau_mechanical << tau_aerodynamics
#   Response to a step change in speed is <= 100ms
#   w_ref: 1 = Max motor speed clockwise -1 = Max motor speed anticlockwise
#   
#   All motors (including cruise motor) are identical

def compute_w_max(Mt, Me, Rs, np, Vmax, km):
    return (((-Mt * Me / Rs) + np*csqrt((Mt * Me / Rs)**2 - 4 * km * -Mt / Rs * Vmax)) / (2 * km)).real

# Binary search for Mt values such that compute_w_max(Mt, Me, Rs, np, Vmax, km) = max_omega
def binary_search(Mt, Rs, np, Vmax, km, max_omega):
    Mt_low = Mt*0.0001
    Mt_high = Mt*10000
    while True:
        Mt_mid = (Mt_low + Mt_high)/2
        
        current_w_max = compute_w_max(Mt_mid, Mt_mid, Rs, np, Vmax, km)
        if abs(current_w_max - max_omega) < 10:
            break
        elif current_w_max > max_omega:
            Mt_high = Mt_mid
        else:
            Mt_low = Mt_mid
    return Mt_mid

def powertrain_ESC_Motor(max_omega, propeller_thrust_factor = 6.2e-5):
        
    n_conv = 90 #   ESC Converter Efficiency
    Nseries = 6 #   Number of battery cells in series
    Vcell_max = 4.2 #   %   Maximum cell voltage
    Vmax = Nseries*Vcell_max #   Maximum battery voltage

    kt = propeller_thrust_factor # Thrust Factor: Thrust = kt*omega**2 (N)
    km = kt/42 # Motor Coefficient: Torque = km*omega**2   (Nm)
    np = 3 # Number of poles on the motor 
    Me = 1/(490*np*(pi/30)) # EMF constant: (V / rad/s)
    Mt = Me # Torque constant: (Nm/Amp)
    Rs = 0.10 # Motor resistance: (ohm)

    # Me and Mt need to be corrected
    # Do a binary search for the correct Me such that compute_w_max(Mt, Me, Rs, np, Vmax, km) = max_omega

    print(f'Running binary search to determine a value of Mt such that compute_w_max(Mt, Me, Rs, np, Vmax, km) ~= {max_omega}')
    Mt = binary_search(Mt, Rs, np, Vmax, km, max_omega)
    Me = Mt
    w_max = compute_w_max(Mt, Me, Rs, np, Vmax, km)

    print(f'Power model initialised with:')
    print(f'\t propeller thrust factor = {propeller_thrust_factor}')
    print(f'\t max_omega = {max_omega}')
    print(f'\t w_max = {w_max}')
    print(f'\t Mt = {Mt}')
    print(f'\t km = {km}')

    def _powertrain_ESC_Motor(w_ref, m_init, v_batt, dT) -> Tuple[float, float, float, float, float]:

        Vm = m_init*v_batt # Voltage applied to motor
        w = (  (-Mt*Me/Rs) + np*csqrt( (Mt*Me/Rs)**2 - 4*km*(-Mt/Rs)*Vm ) )/(2*km)
        w_ref_r = w_ref * w_max # motor reference speed in rad/s
        tol = 1 # Tolerance value to allow convergence: rad/s
        mod = m_init

        ii = 0
        while w.real > abs(w_ref_r)+tol or w.real < abs(w_ref_r)-tol:
            dm = (abs(w_ref_r) - w)/w_max
            mod = mod + dm
            Vm = mod*v_batt
            w = ((-Mt * Me / Rs) + np*csqrt(pow((Mt * Me / Rs), 2) - 4.0 * km * -Mt / Rs * Vm)) / (2.0 * km)
            ii+=1
            if ii > 30000:
                print(f"Broke out after 30000 loops (control {w_ref} - {w.real}, {abs(w_ref_r)})")
                break
            
        w = w.real / 9.54
        thrust = kt * pow(w, 2)
        Torque = km * pow(w, 2)

        Idis = Torque/Mt
        # Idis = Torque*w/Vm

        Qcon = (Idis*dT)*(n_conv/100)

        return (w, thrust, mod.real, Qcon, Idis)
    return _powertrain_ESC_Motor