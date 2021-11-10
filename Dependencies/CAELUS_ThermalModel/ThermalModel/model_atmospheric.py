def model_atmospheric(t):
    temperature = 0

    if t < 12 * 60:
        temperature = 14
    if 12 * 60 <= t < 45 * 60:
        temperature = 12
    if 45 * 60 <= t < 105 * 60:
        temperature = 16
    if 105 * 60 <= t < 131 * 60:
        temperature = 12
    if t > 131 * 60:
        temperature = 16

    return temperature
