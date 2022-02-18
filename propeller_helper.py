from DigitalTwin.thrust_modelling import get_thrust_coefficient
import matplotlib.pyplot as plt

RPM_TO_RAD = 0.10472

# A propeller has diameter_cm, pitch_cm, and blades_n.
def propeller(diameter_cm, pitch_cm, blades_n):
    prop = {
        'diameter_cm': round(diameter_cm, 2),
        'pitch_cm': round(pitch_cm, 2),
        'blades_n': blades_n,
    }
    prop.update({'thrust_coefficient': get_thrust_coefficient(prop)})
    return prop

def stringify_prop(prop):
    return '<{}x{}x{} (kf: {})>'.format(prop['diameter_cm'], prop['pitch_cm'], prop['blades_n'], round(prop['thrust_coefficient'], 8))

def generate_data_for_propellers(max_rpm, propellers):
    max_rad_s = round(max_rpm * RPM_TO_RAD)
    xs = [rpm for rpm in range(0, max_rad_s, 100)]
    coefficients = [prop['thrust_coefficient'] for prop in propellers]
    yss = []
    for coefficient in coefficients:
        yss.append([coefficient * x**2 for x in xs])
    return xs, yss

def plot_graphs(propellers, max_rpm):
    xs, yss = generate_data_for_propellers(max_rpm, propellers)
    for i, ys in enumerate(yss):
        plt.plot(xs, ys, label=stringify_prop(propellers[i]))
        plt.ylabel('Thrust (N)')
        plt.xlabel('Ω (Rad/s)')
    plt.title(f'Thrust Coefficient vs RPM (Max RPM: {max_rpm})')
    plt.legend()
    plt.show()

def inch_to_cm(inch):
    return inch * 2.54

diameters_cm = [
18
]

pitches_cm = [
    13
]

def generate_propeller_combinations(diameters_cm, pitches_cm, blades_n=3):
    return [propeller(diameter_cm, pitch_cm, blades_n) for diameter_cm in diameters_cm for pitch_cm in pitches_cm]

props = generate_propeller_combinations(diameters_cm, pitches_cm)
MAX_RPM = 13000
plot_graphs(props, MAX_RPM)