from pathlib import Path as pt
import numpy as np


def var_find(fname: pt, time=False):

    if not fname: raise Exception("Invalid filename")
    findVar = {
        'res': 'm03_ao13_reso', 
        'b0': 'm03_ao09_width',
        'trap': 'm04_ao04_sa_delay'
    }

    foundVar: dict[str, float] = {}

    with open(fname, 'r') as fp:
        read_lines: list = fp.readlines()

        for line in read_lines:
            if not len(line.strip()) == 0 and line.split()[0] == '#':
                for j in findVar:
                    if findVar[j] in line.split():
                        foundVar[j] = float(line.split()[-3])

        res, b0 = round(foundVar['res'], 1), int(foundVar['b0']/1000)
        return res, b0


def get_skip_line(scanfile: str, location: pt):
    with open(location/scanfile, 'r') as f:
        skip = 0
        for line in f:
            if len(line) > 1:
                line = line.strip()
                if line == 'ALL:':
                    return skip + 1
            skip += 1
    return 0


def get_iterations(scanfile: str, location: pt):
    
    iterations: list = []
    with open(location/scanfile, 'r') as f:

        for line in f:
            if line.startswith('#mass'):
                iteration: int = int(line.split(':')[-1])
                iterations.append(iteration)
            else:
                continue
    iterations: np.ndarray = np.array(iterations, dtype=int)
    print(f"{iterations=}", flush=True)

    return iterations