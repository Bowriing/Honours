from flask_login import current_user
from flask import flash
from datetime import datetime

class Log:
    def __init__(self, totalPower, date, time, zone, season):
        self.totalPower = totalPower
        self.date = date
        self.time = time
        self.zone = zone
        self.season = season

class Device:
    def __init__(self, name, type, powerRating, age, zones, counter = 0, final_power = 0):
        self.name = name
        self.type = type
        self.powerRating = powerRating
        self.age = age
        self.zones = zones
        self.counter = counter
        self.final_power = final_power

def main(date):
    if checkUserCSVcontent() == False:
        return 
    
    date = datetime.strptime(date, "%Y-%m-%d")
    date = date.strftime("%d-%m-%Y")
    #returns a log object
    logs_list = get_logs_by_date(date=date)#this gets all logs for a day as defined in function 48 logs - 1 day = 48 logs
    devices_list = get_devices()#gets all devices from users database field and create a list of device objects
    eligible_devices_object_list = []#contains a list of a list of device objects which have matching zones per log
    daily_power_use:float
    daily_power_use = 0

    for log in logs_list:
        log_power:float
        log_power = float(log.totalPower)
        daily_power_use = daily_power_use + log_power
        daily_power_use = round(daily_power_use, 2)
        rawDevices = check_device_in_log_zone(devices=devices_list, zone=log.zone)
        eligible_devices_object_list.append(rawDevices)

    for device in devices_list:
        device.final_power = total_device_usage(device=device)

        print("Total Day Power Usage: ", daily_power_use)
        print("Name:",device.name, "\nTotal Energy Usage (in day):",device.final_power,"kWh", "\nCount:", device.counter,"\n\n")

    return devices_list, daily_power_use, date

def get_devices():
    devices = []
    for device in current_user.devices:
        name = device.deviceName
        type = device.deviceType
        powerRating = device.powerRating
        age = device.deviceAge
        zones = []
        for zone in device.timeZones:
            zones.append(zone)

        deviceObj = Device(name=name, type=type, powerRating=powerRating, age=age, zones=zones)
        devices.append(deviceObj)
    return devices

def total_device_usage(device):
    count = device.counter
    power_rating = device.powerRating #this also represents the devices watt-hour usage
    type = device.type
    max_usage = power_rating / 2#as the log is 30 min the maximum device usage in watt-hours can only be its power rating divided by 2
    rel_max_usage = max_usage*count#have to multiply by how many times the device has appeared in the logs

    match type:
        #Kitchen Devices
        case 'kettle':#kettle used for 2 minutes at full load at a time
            time_in_use_percent = 2 / 30#2 minutes out of the 30 min log
            total_usage = rel_max_usage * time_in_use_percent
            total_usage = float(total_usage / 1000)#divide by 1000 to convert to kwh not wh 
            total_usage = round(total_usage, 2)

            return total_usage # divide by 1000 as we need kWh not wH
        case 'computer':
            normal_load_percent = 0.925 # amount of time in percent the device is under normal load
            full_load_percent = 0.075 # amount of time in percent the device is under full load
            normal_load_total = normal_load_percent * rel_max_usage #get power consumption of normal load 
            normal_load_total = normal_load_total * 0.151 #the device will use 15.1% of original power rating on normal workloads
            full_load_total = rel_max_usage * full_load_percent #get total power for amount of time device is under full load
            total_usage = normal_load_total + full_load_total # combine calculations of power for both full and normal loads over period of time
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'hob':#electrical hob, used no more then usually 20 mins maximum per use, chances are user cooks using hob no more then 2 times a day
            time_in_use_percent = 20 / 30
            total_usage = max_usage * time_in_use_percent
            if count > 2:
                count = 2
            total_usage = total_usage * count
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'tv':#tv usually used for hours at time, or left on so we take full 30min as constantly in use, europe avg is 3-4 hours a day so we say 3.5hours which = 7 logs
            if count > 7:
                count = 7 # if the count says the tv appears more then 7 logs in a day then we reduce as it is unlikely the tv to be used more then 3.5 hours          
            total_usage = max_usage * count
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'microwave':# aorund 6ish minuted for general cooked meal in microwave, only can be used 2/3 times per cooking meals - three eating times a day so 4/5 logs
            time_in_use_percent = 6 / 30
            if count > 5:
                count = 5
            total_usage = max_usage * time_in_use_percent
            total_usage = total_usage * count
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'fridge':#constant device so energy calculation is easy, compressor switches on around 4-8 times per hour and 10-20 mins per cycle - 3 times per log, 15 mins per log (approx)
            time_in_use_percent = 15 / 30
            night_load_total = power_rating / 10
            night_load_total = night_load_total * 18#18 logs for night period where fridge door will not be opened to boot up compressor
            max_usage = max_usage * 30 # 30 logs for the rest of the day, 48 logs compromise of a day
            day_load_total = max_usage * time_in_use_percent # times 
            total_usage = night_load_total + day_load_total
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        #Bedroom Devices
        #Living Room Devices
        #Misc Devices

def checkUserCSVcontent():
    #check if user has csv data, if not inform them and return
    if not hasattr(current_user.csv_data, 'csv_content'):
        flash('You have no CSV Content', category='error')
        print("Users CSV content is empty")
        return False
    
    else:
        return True
    
#checks if a devices timezone is the same as passsed in zone from log.zone    
def check_device_in_log_zone(devices, zone):
    returndevices = []
    for device in devices:
        if zone in device.zones:
            returndevices.append(device)
            device.counter += 1

    return(returndevices)

def get_logs():
    log = current_user.csv_data.csv_content
    csvRow = [] 
    logList = []

    for row in log.split('\n')[2:]:
        if row:
            csvRow.append(row) 

    for i, row in enumerate(csvRow):
        count = len(csvRow)
        if(i == count):
            break

        csvItem = csvRow[i]
        csvItemSplit = csvItem.split(',')
        #split 1 = kwgh, split 2 = datetime]
        totalpower = csvItemSplit[1]
        datetimeString = csvItemSplit[2]
        dt_object = datetime.strptime(datetimeString, "%Y-%m-%dT%H:%M:%S.%fZ")
        date = dt_object.strftime("%d-%m-%Y")
        time = dt_object.strftime("%H:%M")
        hour = dt_object.hour
        month = dt_object.month
        zone = getZone(hour)
        season = getSeason(month)

        newLog = Log(totalPower=totalpower, date=date, time=time, zone=zone, season=season)
        logList.append(newLog)

    return logList

def get_logs_by_date(date):
    logs = get_logs()
    return_logs = []
    for log in logs:
        if log.date == date:
            return_logs.append(log)

    return return_logs

def getSeason(month):
    if 3 <= month <= 5:
        return "spring"
    elif 6 <= month <= 8:
        return "summer"
    elif 9 <= month <= 11:
        return "autumn"
    elif month == 12 or month == 1 or month == 2:
        return "winter"
    else:
        print("Invalid Month")
        return "Invalid Month"
    
def getZone(hour):
    if 6 <= hour < 11:
        return "morning"
    elif 11 <= hour < 17:
        return "midday"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"