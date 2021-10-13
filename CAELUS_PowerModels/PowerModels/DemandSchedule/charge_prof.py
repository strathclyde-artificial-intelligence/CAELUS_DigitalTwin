from math import e as e_const
from .batt_chg import batt_chg
from decimal import Decimal

def charge_prof(t_start, depth_of_discharge, c_rate) -> []:
    Q = 22             # Capacity: Ah
    I_1C = 22          # 1C rating of battery: A
    Vnom = 3.7         # Nominal Voltage: V
    Vmax = 4.2         # Max/Charge Voltage: V
    Vcut = 2.75        # Battery  cut-off voltage
    Nseries = 6        # Number of cells in series

    base_param = [Q, I_1C, Vnom, Vmax, Vcut]

    GC_temp = []
    tstamp = t_start

    ## Compute Battery Charge Profile: CC - CV
    Icc = c_rate*I_1C           # Constant Current: C-rating

    # Build Constant Voltage Charge Array: Charge Current (C-rating), Tau (when t = 3tau, I = 1C/20)
    CVprof = [
        [1, 10/60],
        [2, 6/60]
    ]

    CVprof = [
        [CVprof[0][0], CVprof[0][1], (CVprof[0][0] * CVprof[0][1]), CVprof[0][0]**2, CVprof[0][1]**2],
        [CVprof[1][0], CVprof[1][1], (CVprof[1][0] * CVprof[1][1]), CVprof[1][0]**2, CVprof[1][1]**2]
    ]
    
    Ex = sum([row[0] for row in CVprof]); # Sum of x values
    Ey = sum([row[1] for row in CVprof]); # Sum of y values
    Exy = sum([row[2] for row in CVprof]); # Sum of x.y values
    Ex2 = sum([row[3] for row in CVprof]); # Sum of x2 values
    Ey2 = sum([row[4] for row in CVprof]); # Sum of y2 values

    c = ( (Ey*Ex2)-(Ex*Exy) )/ ( (len(CVprof)*Ex2)-(Ex**2) ); # Calculate tau intercept
    m = ( (len(CVprof)*Exy) - (Ex*Ey) ) / ( (len(CVprof)*Ex2)-(Ex**2) ); # calculate tau gradient

    tau = (m*(Icc/I_1C)) + c

    Xmax = -c/m # Maximum Charging current to allow

    ## Set up time
    T = 6  # hours
    dT = 1/3600     #model sample time: seconds
    t = 0

    ## Constant Current Period
    DoDinit = depth_of_discharge #Battery depth_of_discharge at start: #
    Vbatt = 2.76

    while (Vbatt < (Vmax*Nseries)):
        If = -Icc
        It = ((DoDinit/100)*Q)+(If*t)     # Extracted Capacity: Ah
        
        Vbatt = batt_chg(It, If, Nseries)
        Ibatt = Icc
        Pbatt = Vbatt*Ibatt
        Ebatt = Pbatt*dT               #Extracted Energy for timestep: Wh
        
        tstamp[5] += int(dT*3600)   #updating the timestamp 
        GC_temp.append([[e for e in tstamp], round(Pbatt, 4), round(Ebatt, 4)])
        
        tcc = t
        t = t+dT


    Icv = Icc
    tcv = 0
    while Icv > (I_1C/20):
        Icv = Icc*e_const**(-tcv/tau)
        It = ((DoDinit/100)*Q)-(Icv*t)
        Vbatt = Vmax
    
        Pbatt = Vbatt*Icv
        Ebatt = Pbatt*dT
    
        tstamp[5] += int(dT*3600)
        GC_temp.append([[e for e in tstamp], round(Pbatt, 4), round(Ebatt, 4)])
    
        tcv = tcv+dT
        t = t+dT
    return GC_temp


