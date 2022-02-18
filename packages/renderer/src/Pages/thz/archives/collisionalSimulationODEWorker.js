// return        
// const ODEWorker = new collisionCoolingODESolver()
// ODEWorker.postMessage({
//     duration,
//     totalSteps,
//     numberDensity,
//     boltzmanDistribution,
//     collisionalRateConstants
// });

// ODEWorker.onmessage = ({data: {finalData, error}}) => {
//     if(error) return window.handleError(error)
//     target.classList.remove("is-loading")
//     if(!finalData) return
    
//     console.log(finalData)

//     plot( 
//         ` Distribution: ${collisionalTemp}K`, 
//         "Time (s)", "Population", finalData, 
//         plotID, 
//     )
//     const boltzmanDistributionCold = boltzman_distribution({
//         trapTemp: collisionalTemp,
//         energyUnit,
//         zeemanSplit,
//         energyLevels,
//         electronSpin,
//     })

//     const boltzmanDataCold = boltzmanDistributionCold.map(f=>f.value)
//     const boltzmanData = {x: energyKeys, y: boltzmanDataCold, name:"boltzman"}

//     const collisionalDataCold = []

//     for (const key in finalData) {
//         const coldValue = finalData[key].y.at(-1)
//         collisionalDataCold.push(coldValue)
//     }

//     const collisionalData = {
//         x: energyKeys, y: collisionalDataCold, name: "collisional"
//     }
//     const combinedData = {collisionalData, boltzmanData}
//     console.log({finalData})
//     plot(
//     ` Distribution: ${collisionalTemp}K`, 
//     "Energy Levels", "Population", combinedData, 
//     `${plotID}_collisionalBoltzman`, 
//     )

//     const differenceFromBoltzman = []
//     for (let i=0; i<boltzmanDataCold.length; i++) {
//         const computeDifference = (boltzmanDataCold[i] - collisionalDataCold[i]).toFixed(2)
//         differenceFromBoltzman.push(computeDifference)
//     }

//     plot(
//         `Difference: Collisional - Boltzmann`, 
//         "Energy Levels", "Difference", 
//         {data: {x: energyKeys, y: differenceFromBoltzman, name:"Difference"}},
//         `${plotID}_collisionalBoltzman_difference`,
//     )
// }