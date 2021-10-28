from math import sqrt, pi, inf
from cmath import sqrt as csqrt

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

def powertrain_ESC_Motor(w_ref, m_init, v_batt, dT) -> [float, float, float, float, float]:
    # ESC Config Parameters
    n_conv = 90    #   ESC Converter Efficiency
    Nseries = 7    #   Number of battery cells in series
    Vcell_max = 4.2 #   #   Maximum cell voltage
    Vmax = Nseries*Vcell_max  #   Maximum battery voltage

    # Motor Config Parameters
    kt = 6.2e-5            # Thrust Factor: Thrust = kt*omega^2 (N)
    km = kt/42.0             # Motor Coefficient: Torque = km*omega^2   (Nm)
    np = 6.0                # Number of poles on the motor       (Ask Avy?)   
    Me = 1.0/(490*np*(pi/30)) # back EMF constant: (V / rad/s)
    Mt = Me                # Torque constant: (Nm/Amp)
    Rs = 0.10              # Motor resistance: (ohm)

    # Maximum motor speed
    w_max = ((-Mt * Me / Rs) + np*csqrt((Mt * Me / Rs)**2 - 4 * km * -kt / Rs * Vmax)) / (2 * km)
    w_max = w_max.real
    
    Vm = m_init*v_batt      # Voltage applied to motor
    w = (  (-Mt*Me/Rs) + np*csqrt( pow((Mt*Me/Rs),2) - (4*km*(-Mt/Rs)*Vm) ) )/(2.0*km)
    w = w.real
    w_ref_r = w_ref * w_max    # motor reference speed in rad/s

    tol = 1                # Tolerance value to allow convergence: rad/s
    mod = m_init

    ii = 0
    while w.real > abs(w_ref_r)+tol or w.real < abs(w_ref_r)-tol:
        dm = (abs(w_ref_r) - w)/w_max
        mod = mod + dm
        Vm = mod*v_batt
        w = ((-Mt * Me / Rs) + np*csqrt(pow((Mt * Me / Rs), 2) - 4.0 * km * -kt / Rs * Vm)) / (2.0 * km)
        
    w = w.real
    thrust = kt * pow(w, 2)
    Torque = km * pow(w, 2)

    Idis = Torque/Mt
    # Idis = Torque*w/Vm

    Qcon = (Idis*dT)*(n_conv/100)

    return (w, thrust, mod.real, Qcon, Idis)

