from flask_login import current_user
from flask import flash
from datetime import datetime
from .filters import ZoneFilter

class CsvLog:
    def __init__(self, pkwh, pdateTime):
        self.kwh = pkwh
        self.datetime = pdateTime

class Device:
    def __init__(self, deviceName, deviceType, powerRating, constant, age, timeZones):
        self.name = deviceName
        self.deviceType = deviceType
        self.powerRating = powerRating
        self.constant = constant
        self.age = age
        self.timeZones = timeZones

def processingMain():
    if hasattr(current_user.csv_data, 'csv_content'):
        #get interval (line) of csv and put into object
        logInstance = getCsvLog()

        #list of all users devices as device obj
        devices = []

        #list of devices after filtration has processed
        filteredDevices = []

        #create device objects from current_user device list
        for device in current_user.devices:
            deviceObj = Device(device.deviceName, device.deviceType, device.powerRating, device.constantDevice, device.deviceAge, device.timeZones)
            devices.append(deviceObj)

        #run zone filter which returns a filtered devices list and append to filtered devices
        filteredDevices = ZoneFilter(devices)

        dt = logInstance.datetime
        kwh = float(logInstance.kwh)
        wh = (kwh*1000)
        cost  = costConverter(kwh)

        #get custom datetime format
        output_dt= format_dt_output(dt)

        #method which is uploaded to the home render template for user to see information
        output = generate_report(output_dt, kwh, wh, cost, filteredDevices)

        return (output)

    elif not hasattr(current_user.csv_data, 'csv_content'):
        flash('No CSV Content to read.', category='error')
        print ("User's CSV Content Is Empty")
        return ("No CSV to process")


def getCsvLog():
    csvData = current_user.csv_data.csv_content
    csvRow = [] 
    for row in csvData.split('\n')[50:]:
        csvRow.append(row)  
    csvItem = csvRow[0]
    csvItemSplit = csvItem.split(',')
    newLog = CsvLog(csvItemSplit[1], csvItemSplit[2])

    return newLog

#return a decimal which figures out cost of the 30min interval based of a cost taken from public website been referenced in doc 
def costConverter(kWh):
    avgrate = 0.245 #in pound
    cost = (kWh*avgrate)

    return cost

def format_dt_output(dt):
    timestamp = dt
    datetime_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    formatted_time = datetime_obj.strftime("%I:%M%p st %B %Y")

    day = datetime_obj.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    formatted_time = formatted_time.replace("st", str(day) + suffix)

    return formatted_time

#generates the output to the home page
def generate_report(dt, kwh, wattHours, cost, devices):
    report = "Interval Conluding: " + dt + "\n"
    report += "kWh Usage: " + str(kwh) + " kWh\n"
    report += "Wh Usage: " + str(wattHours) + " wH\n"
    report += "Cost: £" + str(cost) + "\n"
    report += "Possible Devices Used: " + ", ".join(devices)
    
    return report