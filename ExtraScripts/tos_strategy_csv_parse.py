import csv

def main():
    filep = "StrategyReports_LABU_51921-35t-3D"
    filen = "C:/Users/strat/Documents/"+filep+".csv"
    with open(filen, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter = ";")
        percentGain = 0.00
        lastBuyPrice = 0.00
        totalPL = 0.00
        totalPowerUsed = 0.00

        percentBA_Adjust = 0.01/92
        dollarBA_Adjust = 0.01

        for row in reader: 
            if row['Side'] != None:
                #print(row)
                if 'Buy' in row['Side']:
                    lastBuyPrice = float(row['Price'].replace("$",""))
                    totalPowerUsed = totalPowerUsed + lastBuyPrice
                else:
                    sellPrice = float(row['Price'].replace("$",""))
                    percentGain = percentGain - percentBA_Adjust + ((sellPrice) - lastBuyPrice)/lastBuyPrice
                    totalPL = totalPL + sellPrice - lastBuyPrice - dollarBA_Adjust

        print("percent gain: ", percentGain*100.0, "%")
        print("PL: ", totalPL)
        print("Total Power: ", totalPowerUsed)

if __name__=="__main__":
    main()