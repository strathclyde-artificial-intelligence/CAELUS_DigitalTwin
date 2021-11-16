lines = []
with open('acoustic.ost', 'r') as f:
    lines = f.readlines()
lines = [l[5:-1] for l in lines]
with open('acoustic.ost', 'w') as f:
    f.writelines(lines)