from flask_login import current_user
from flask import flash

class CsvLog:
    def __init__(self, pkwh, pdateTime):
        self.kwh = pkwh
        self.datetime = pdateTime

class Device:
    def __init__(self, deviceType, powerRating, constant, age, timeZones):
        self.deviceType = deviceType
        self.powerRating = powerRating
        self.constant = constant
        self.age = age
        self.timeZones = timeZones

def processingMain():
    if hasattr(current_user.csv_data, 'csv_content'):
        #get interval (line) of csv and put into object
        logInstance = getCsvLog()

        devices = []
        filteredDevices = [] 

        for device in current_user.devices:
            deviceObj = Device(device.deviceType, device.powerRating, device.constantDevice, device.deviceAge, device.timeZones)
            devices.append(deviceObj)

            if 'morning' in device.timeZones:
                filteredDevices.append(device.deviceType)
                print("Added device to filtered device list")

        dt = logInstance.datetime
        kwh = float(logInstance.kwh)
        wh = (kwh*1000)
        whFloat = float(wh)
        watts = (whFloat*0.5)
        cost  = costConverter(kwh)

        #method which is uploaded to the home render template for user to see information
        output = generate_report(dt, kwh, watts, wh, cost, filteredDevices)

        ZoneFilter(dt)

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
def generate_report(dt, kwh, watts, wattHours, cost, devices):
    report = "For the 30 min interval concluding on " + str(dt) + "\n"
    report += "Your total kWh usage was: " + str(kwh) + " kWh\n"
    report += "This means your total wH (watt hour) usage was: " + str(wattHours) + " wH\n"
    report += "Therefore in total, you used " + str(watts) + " Watts\n"
    report += "The total cost for this interval was £" + str(cost) + "\n"
    report += "Possible devices used in this interval: " + str(devices)
    
    return report

#return a decimal which figures out cost of the 30min interval based of a cost taken from public website been referenced in doc 
def costConverter(kWh):
    avgrate = 0.245 #in pound
    cost = (kWh*avgrate)

    return cost

def ZoneFilter(dateTime):
    splitTime = dateTime.split('T')
    gamer = splitTime[1]

    splitgamer = gamer[:5]
    print(splitgamer)