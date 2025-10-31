# Example script using the Tariffs API, comparing design and benchmark APS files.
# You will need to replace the project folder and aps file paths below to make the script run fully.

import iesve

def main():
    # Define project folder and APS path
    # ***Replace these with examples from your computer***
    veProjFolder = r"C:\VE Projects\example project folder"
    apsDesignFilePath = r"C:\VE Projects\example project folder\vista\design results file.aps"
    apsBenchmarkFilePath = r"C:\VE Projects\example project folder\vista\benchmark results file.aps"

    # Create strings for monitoring errors that might occur
    strInfoMessage = iesve.TariffsEngine.String()
    strError = iesve.TariffsEngine.String()

    # Create the tariffs engine and initialise it
    tarEng = iesve.TariffsEngine()
    tarEng.Init(veProjFolder,
                apsDesignFilePath,
                apsBenchmarkFilePath,
                strInfoMessage,
                strError,
                iesve.TariffsEngine.EUnitsSystem.METRIC,
                iesve.TariffsEngine.EModes.MODE_NORMAL,
                iesve.TariffsEngine.EEnergyDataset.ENERGY_DATASET_ASHRAE,
                iesve.TariffsEngine.EComputeCosts.COMPUTE_COSTS_YES)

    # Check for errors/warnings in initialisation
    if not strError.Empty():
        print("Error:", strError.GetString())
        print("***Make sure you have replaced the project folder and file paths with ones available on your computer.***")
        return

    if not strInfoMessage.Empty():
        print("Info:", strInfoMessage.GetString())  # print info but continue anyway

    print("Design net cost:", tarEng.GetDesignNetCost())
    print("Benchmark net cost:", tarEng.GetBenchmarkNetCost())
    print("Improvement:", tarEng.Improvement)

main()