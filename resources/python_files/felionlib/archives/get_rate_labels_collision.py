
import sys, json
from felionlib.utils.FELion_definitions import sendData

def get_label(total_level):
    N = [i for i in range(total_level)]
    print(f"{N=}")
    if spin:
        J = total_level*[0]
        for level in N:
            if level == 0: J[level] = [level+0.5]
            else: J[level] = [level+0.5, level-0.5]

        print(f"{J=}")
        
    transition_labels = []

    if spin:
    
    
        for index_N, current_N in enumerate(J[:-1]):
            for index_J, current_J in enumerate(current_N):
                for index_next, next_N in enumerate(J[index_N+1:]):
                    for next_J in next_N:
                        label = f"{index_N}_{current_J} --> {index_next+index_N+1}_{next_J}"
                        transition_labels.append(label)

    else:
        for index_N, current_N in enumerate(N[:-1]):
            for next_N in N[index_N+1:]:
                label = f"{current_N} --> {next_N}"
                transition_labels.append(label)
            
    return transition_labels


if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")

    conditions = json.loads(", ".join(args))
    print(conditions,  flush=True)
    numberOfLevels = int(conditions["numberOfLevels"])
    spin=conditions["electronSpin"]

    transition_labels = get_label(numberOfLevels)

    sendData({"transition_labels" : transition_labels})