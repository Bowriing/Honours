from flask_login import current_user

class CsvLog:
    def __init__(self, pkwh, pdateTime):
        self.kwh = pkwh
        self.datetime = pdateTime

def processingMain():
    timeFilter()

def timeFilter():
    devices = current_user.devices
    csvData = current_user.csv_data.csv_content
    csvRow = [] 

    for row in csvData.split('\n')[1:]:
        csvRow.append(row)

    csvItem = csvRow[0]
    csvItemSplit = csvItem.split(',')

    newLog = CsvLog(csvItemSplit[1], csvItemSplit[2])
    
    print(newLog.datetime)



