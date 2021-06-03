
function get_energy_levels(total_level=3){

    let N = [i for i in range(total_level)]
    let J = []
    let mJ = []
    let mN = []

    console.log(`${N}`)

    if (spin){
        J = total_level*[0]

        for (const level in N){
            if (level == 0){ J[level] = [level+0.5]}
            else { J[level] = [level+0.5, level-0.5]}

            console.log(`${J}`)


        }
    }

    if (zeeman) {

        if (spin) {
            mJ = total_level*[0]
            index = 0
            for (const level in J){

                current_level = []
                for (const j in level){
                    total_mJ = parseInt(2*j + 1)
                    for _ in range(1, 4):
                        temp -= 1
                        print(temp)
                    temp = np.linspace(-j, j, total_mJ).tolist()
                    current_level.push(temp)
                }

                mJ[index] = current_level
            }
            console.log(`${mJ}`)
        }
        else {
            mN = total_level*[0]
            index = 0
            for (const level in N){

                total_mJ = int(2*level + 1)
                mN[index] = np.linspace(-level, level, total_mJ, dtype=int).tolist()

                index++
            }
            console.log(`${mN}`)
        }

    let energy_level_info = None
    if spin and zeeman{ energy_level_info = mJ
    elif spin and not zeeman{ energy_level_info = J
    elif not spin and zeeman{ energy_level_info = mN
    else{ energy_level_info = N
    console.log(`${energy_level_info}`)

    return N, J, mJ, mN