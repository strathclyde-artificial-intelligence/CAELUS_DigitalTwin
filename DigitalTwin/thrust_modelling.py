from math import pi, atan

AIR_DENSITY_IMPERIAL = 0.0739 # standard air density at 25 deg (lb / ft**3)
cm_to_inch = 1/2.54

bucketise = lambda buckets, fs, v: \
    buckets[[f(v) for f in fs].index(True)]

getTheta = lambda prop_pitch, prop_diameter: \
    atan(prop_pitch / (pi * prop_diameter))

getEd = lambda prop_pitch, prop_diameter: \
    bucketise(
        [0.91, 0.88, 0.83, 0.80],
        [
            lambda v: v < 0.4,
            lambda v: v >= 0.4 and v < 0.8,
            lambda v: v >= 0.8 and v < 0.9,
            lambda v: v >= 0.9
        ],
        prop_pitch / prop_diameter)

getK = lambda blades_n, c_d_ratio: \
    blades_n * 1/2 * c_d_ratio

getCt = lambda k, theta, e_d: \
    4/3 * k * theta * (1 - ((1 - e_d) ** 3)) - k * ((k * (1 + k))**0.5 - k**0.5) * (1 - ((1 - e_d) ** 2))

getKf = lambda rho, prop_radius, e_d, c_t: \
    1/16 * rho * pi * prop_radius**4 * e_d**4 * c_t

getCdRatio = lambda prop_diameter: \
    bucketise(
        [0.09, 0.1, 0.11, 0.12, 0.13, 0.14],
        [
            lambda v: v < 5,
            lambda v: v >= 5 and v < 7, 
            lambda v: v >= 7 and v < 10,
            lambda v: v >= 10 and v < 13,
            lambda v: v >= 13 and v < 15,
            lambda v: v >= 15 and v < 17
        ],
        prop_diameter)

def get_thrust_coefficient(propeller_specs):
    prop_diameter_inches = propeller_specs['diameter_cm'] * cm_to_inch
    prop_pitch_inches = propeller_specs['pitch_cm'] * cm_to_inch
    prop_blades_n = propeller_specs['blades_n']
    e_d = getEd(prop_pitch_inches, prop_diameter_inches)
    theta = getTheta(prop_pitch_inches, prop_diameter_inches)
    cd_ratio = getCdRatio(prop_diameter_inches)
    k = getK(prop_blades_n, cd_ratio)
    c_t = getCt(k, theta, e_d)
    return getKf(AIR_DENSITY_IMPERIAL, prop_diameter_inches / 2.0, e_d, c_t)