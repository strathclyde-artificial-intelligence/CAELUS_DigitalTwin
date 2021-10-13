from csv import reader

charge_prof_validation = None
with open('tests/charge_prof_validation.csv', 'r') as f:
    data = reader(f)
    charge_prof_validation = [[[int(dp) for dp in row[:6]]] + [round(float(dp),4) for dp in row[6:]] for row in data]
