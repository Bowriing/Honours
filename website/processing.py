from flask_login import current_user
from flask import flash

class CsvLog:
    def __init__(self, pkwh, pdateTime):
        self.kwh = pkwh
        self.datetime = pdateTime

def processingMain():
    if hasattr(current_user.csv_data, 'csv_content'):
        #get interval (line) of csv and put into object
        logInstance = getCsvLog()

        dt = logInstance.datetime
        kwh = float(logInstance.kwh)
        wh = (kwh*1000)
        whFloat = float(wh)
        watts = (whFloat*0.5)
        cost  = costConverter(kwh)

        #method which is uploaded to the home render template for user to see information
        output = generate_report(dt, kwh, watts, wh, cost)
        print (output)
        return (output)

    elif not hasattr(current_user.csv_data, 'csv_content'):
        flash('No CSV Content to read.', category='error')
        print ("User's CSV Content Is Empty")
        return ("No CSV to process")


def getCsvLog():
    csvData = current_user.csv_data.csv_content
    csvRow = [] 
    for row in csvData.split('\n')[1:]:
        csvRow.append(row)  
    csvItem = csvRow[0]
    csvItemSplit = csvItem.split(',')
    newLog = CsvLog(csvItemSplit[1], csvItemSplit[2])

    return newLog


#generates the output to the home page
def generate_report(dt, kwh, watts, wattHours, cost):
    report = "For the 30 min interval concluding on " + str(dt) + "\n"
    report += "Your total kWh usage was: " + str(kwh) + " kWh\n"
    report += "This means your total wH (watt hour) usage was: " + str(wattHours) + " wH\n"
    report += "Therefore in total, you used " + str(watts) + " Watts\n"
    report += "The total cost for this interval was £" + str(cost)
    
    return report

#return a decimal which figures out cost of the 30min interval based of a cost taken from public website been referenced in doc 
def costConverter(kWh):
    avgrate = 0.245 #in pound
    cost = (kWh*avgrate)

    return cost


def timeFilter():
    #to be made
    return