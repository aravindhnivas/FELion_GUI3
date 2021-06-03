
import sys, json
import numpy as np
from FELion_definitions import sendData

def get_energy_levels(total_level=3):

    N = [i for i in range(total_level)]
    J = []
    mJ = []
    mN = []
    
    print(f"{N=:}")

    if spin:
        J = total_level*[0]
        for level in N:
            if level == 0: J[level] = [level+0.5]
            else: J[level] = [level+0.5, level-0.5]

        print(f"{J=:}")


    if zeeman:

        if spin:
            mJ = total_level*[0]
            for index, level in enumerate(J):

                current_level = []
                for j in level:
                    total_mJ = int(2*j + 1)
                    temp = np.linspace(-j, j, total_mJ).tolist()
                    current_level.append(temp)
                mJ[index] = current_level
            print(f"{mJ=:}")
        else:
            mN = total_level*[0]
            for index, level in enumerate(N):
                total_mJ = int(2*level + 1)
                mN[index] = np.linspace(-level, level, total_mJ, dtype=int).tolist()

            print(f"{mN=:}")

    energy_level_info = None
    if spin and zeeman: energy_level_info = mJ
    elif spin and not zeeman: energy_level_info = J
    elif not spin and zeeman: energy_level_info = mN
    else: energy_level_info = N
    print(f"{energy_level_info=:}")
    
    return energy_level_info, N, J

def get_energy_labels(energy_level_info, N, J):
    
    transition_labels = []
    transition_labels_J0 = []
    transition_labels_J1 = []

    total_transition = 0
    for index_N, current_N in enumerate(energy_level_info):

        if index_N>0:

            ground_levels = energy_level_info[index_N-1]

            
            if not spin and not zeeman:
                temp_transition_labels = f"{current_N} --> {ground_levels}"
                transition_labels.append(temp_transition_labels)
                total_transition += 1

            if spin:

                print("###############################################################\n")
                print(f"Current N: {N[index_N]} splitted into J: {J[index_N]}")
                print("-------\n")

                for index_J, current_J in enumerate(current_N):

                    total_transition = 0
                    
                    if zeeman:
                        total_transition_J1 = 0
                        total_transition_J0 = 0
                        print(f"Current J: {index_N}_{max(current_J)} splitted into mJ: {current_J}")
                        print(f"each mJ {current_J} in {index_N} level will undergo transition with {ground_levels=:}")
                        print(f"Selection rule: del_M = 0, 1, -1\n")

                        temp_transition_labels = []
                        temp_transition_labels_J0 = []
                        temp_transition_labels_J1 = []
                        
                        for index_mJ, current_mJ in enumerate(current_J):

                            current_mJ_label = f"{index_N}_{max(current_J)}__{current_mJ}"
                            print(f"\n==={current_mJ_label=:}===")

                            for index_ground_J, ground_J in enumerate(ground_levels):

                                if index_N>1: print(f"\nFor {ground_J=:}")
                                for ground_mJ in ground_J:

                                    del_M = current_mJ-ground_mJ

                                    if del_M==0 or del_M==1 or del_M==-1:

                                        ground_mJ_label = f"{index_N-1}_{max(ground_J)}__{ground_mJ}"

                                        current_transition_label = f"{current_mJ_label} --> {ground_mJ_label}"
                                        temp_transition_labels.append(current_transition_label)
                                        print(f"{current_transition_label=:}")

                                        total_transition += 1

                                        if index_ground_J == 0: 
                                            total_transition_J1 += 1
                                            temp_transition_labels_J1.append(current_transition_label)

                                        else: 
                                            total_transition_J0 += 1
                                            temp_transition_labels_J0.append(current_transition_label)

                                if index_N>1: print(f"-.-.-.-.-.-.-.-.-.-.\n")

                            if index_N>1: print(f"===Close current mJ===\n")
                    
                        transition_labels.append(temp_transition_labels)
                        transition_labels_J0.append(temp_transition_labels_J0)
                        transition_labels_J1.append(temp_transition_labels_J1)

                        if index_N>1:
                            print(f"{total_transition_J0=:} for {index_N}_{max(current_J)} --> {index_N-1}_{max(ground_levels[1])}")
                            print(f"{total_transition_J1=:} for {index_N}_{max(current_J)} --> {index_N-1}_{max(ground_levels[0])}")
                        
                    else:
                        print(f"{ground_levels=:}")
                        for ground_J in ground_levels:

                            del_J = current_J-ground_J
                            if del_J==0 or del_J==1 or del_J==-1:
                                
                                temp_transition_labels = f"{index_N}_{current_J} --> {index_N-1}_{ground_J}"
                                transition_labels.append(temp_transition_labels)
                                print()
                                total_transition += 1

                    print(f"\n{total_transition=:}")
                    print("==========================================\n")
                    
    return transition_labels, transition_labels_J0, transition_labels_J1


if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")

    conditions = json.loads(", ".join(args))
    print(conditions,  flush=True)
    numberOfLevels = int(conditions["numberOfLevels"])
    spin=conditions["electronSpin"]
    zeeman=conditions["zeemanSplit"]

    energy_level_info, N, J = get_energy_levels(numberOfLevels)
    transition_labels = get_energy_labels(energy_level_info, N, J)

    sendData(
        {

            "transition_labels" : transition_labels[0], 
            "transition_labels_J0": transition_labels[1], 
            "transition_labels_J1": transition_labels[2]
        }
    )