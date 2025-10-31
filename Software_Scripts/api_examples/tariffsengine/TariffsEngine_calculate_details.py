# Example script using the Tariffs API to get tariff/supplier/cost/currency information.
# You will need to replace the project folder and aps file paths below to make the script run fully.

veProjFolder = "" # Replace this with your project folder
apsFilePath = "" # Replace this with the path to your aps file

import iesve

def main():
    # Define project folder and APS path
    # ***Replace these with examples from your computer***
    #veProjFolder = r"C:\VE Projects\example project folder"
    #apsFilePath = r"C:\VE Projects\example project folder\vista\design results file.aps"

    # Create strings for monitoring errors that might occur
    strInfoMessage = iesve.TariffsEngine.String()
    strError = iesve.TariffsEngine.String()

    # Create the tariffs engine
    tarEng = iesve.TariffsEngine()
    tarEng.Init(veProjFolder, apsFilePath, "", strInfoMessage, strError)

    # Check for errors/warnings in initialisation
    if not strError.Empty():
        print("Error:", strError.GetString())
        print("***Make sure you have replaced the project folder and file path with ones available on your computer.***")
        return

    if not strInfoMessage.Empty():
        print("Info:", strInfoMessage.GetString())  # print info but continue anyway

    # All utilities
    utilityNameIds = tarEng.GetUtilitiesNamesAndIds()
    print("Utility names and IDs:", utilityNameIds, "\n")

    # Current currency
    currencyData = tarEng.GetSelectedCurrency()  # name, id, location, symbol
    print("Currency data:", currencyData, "\n")
    if not currencyData:
        print("No currency data found. Stopping.")
        return

    # Examine some supplier/tariff info for the electricity utility
    elecId = tarEng.EUtilities.ELECTRICITY

    # Check the cost of using the flat rate
    tarEng.ComputeWithFlatRate(elecId)  # Uses rate from engine, but a different rate can be provided as a second argument.
    flatCost = tarEng.GetDesignNetCost(elecId)
    print("Cost to use flat rate:", flatCost, "\n")

    # Get all electricity suppliers
    elecSuppliers = tarEng.GetSuppliersForUtility(elecId)
    print("Electricity suppliers:", elecSuppliers)

    # Choose the first supplier and look at the available tariffs
    if not elecSuppliers:
        print("No suppliers found. Stopping.")
        return

    chosenSupplierId = elecSuppliers[0][1]
    sampleTariffs = tarEng.GetTariffsForSupplier(chosenSupplierId, currencyData[1])  # Using the currency ID - or use "" instead for all currencies.

    print("Sample electricity tariffs:", sampleTariffs)

    # Choose the first tariff and compute the cost to use this
    if not sampleTariffs:
        print("No sample tariffs found. Stopping.")
        return

    chosenTariff = sampleTariffs[0][1]
    print("Sample tariff's name:", tarEng.GetTariffName(elecId, chosenTariff))
    print("Sample tariff's currency units:", tarEng.GetTariffCurrencyUnits(elecId, chosenTariff))

    tarEng.ComputeWithTariff(elecId, chosenSupplierId, chosenTariff)
    cost = tarEng.GetDesignNetCost(elecId)

    print("Cost to use sample supplier/tariff:", cost, "\n")

    # Timestep data - use the results reader to get the length of the APS file
    file1 = iesve.ResultsReader.open(apsFilePath)
    assert file1 is not None, "Error opening results file"
    startDay = file1.first_day
    endDay = file1.last_day
    print("First & last days:", startDay, ",", endDay)
    file1.close()

    data = tarEng.GetRatesTimeSeries(elecId, startDay, endDay)  # The last two parameters are optional, so can be omitted.
    print("Length of timestep data:", len(data))
    print("Data instances per day:", len(data) / (1 + endDay - startDay))
    print("Snippet of timestep data:", data)

main()