import matplotlib.pyplot as plt
import json

def load_file(file_p):
    with open(file_p, 'r') as f:
        return json.loads(f.read())


def plot_battery(temp_data):
    plt.plot([i for i in range(len(temp_data))], temp_data, 'b-', label='battery')

def plot_temp(temp_data):
    plt.plot([i for i in range(len(temp_data))], temp_data, 'r-', label='payload temperature')

plot_temp(load_file('mission_6b00f6e5-aefd-4238-ab13-77e0060982f0.txt')['payload_temp'])
plot_battery(load_file('mission_6b00f6e5-aefd-4238-ab13-77e0060982f0.txt')['battery_level'])
plt.legend()
plt.show()
