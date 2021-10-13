def model_atmosferic(t):

    if (t< 12*60):        
        T = 14
    if (12*60<=t< 45*60):
        T = 12
    if (45*60<=t< 105*60):
        T = 16
    if (105*60<=t< 131*60):
        T = 12
    if (t> 131*60):
        T = 16

    return T