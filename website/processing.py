from flask_login import current_user
from flask import flash

class CsvLog:
    def __init__(self, pkwh, pdateTime):
        self.kwh = pkwh
        self.datetime = pdateTime

def processingMain():
    if hasattr(current_user.csv_data, 'csv_content'):
        logInstance = getCsvLog()
        print ("Datetime: " + logInstance.datetime)
        print ("kWh Usage: " + logInstance.kwh + "kWh")
        wattUsage = kwhToWatts(logInstance.kwh)
        print (wattUsage)
        print ("Successfully outputted wattUsage")

    elif not hasattr(current_user.csv_data, 'csv_content'):
        flash('No CSV Content to read.', category='error')
        print ("User's CSV Content Is Empty")



def getCsvLog():
    csvData = current_user.csv_data.csv_content
    csvRow = [] 
    for row in csvData.split('\n')[1:]:
        csvRow.append(row)  
    csvItem = csvRow[0]
    csvItemSplit = csvItem.split(',')
    newLog = CsvLog(csvItemSplit[1], csvItemSplit[2])

    return newLog

def kwhToWatts(pKwh):
    kwh = float(pKwh)
    watts = kwh * 1000
    watts = (watts/0.5)

    return watts


def timeFilter():
    return