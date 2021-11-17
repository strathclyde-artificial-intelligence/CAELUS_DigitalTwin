def remove_grep_meta():
    lines = []
    with open('acoustic.ost', 'r') as f:
        lines = f.readlines()
    lines = [l[5:-1] for l in lines]
    with open('acoustic.ost', 'w') as f:
        f.writelines(lines)

def fix_time():
    lines = []
    with open('acoustic.ost', 'r') as f:
        lines = f.readlines()
    lines = [', '.join([float(c) if j != 3 else float(c) + ((i * 4) / 1000000) for j,c in enumerate(l.split(', '))]) for i,l in enumerate(lines)]
    with open('acoustic.ost', 'w') as f:
        f.writelines(lines)

fix_time()