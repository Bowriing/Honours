from flask_login import current_user
from flask import flash
from datetime import datetime
from .devices import calculate_power

class Log:
    def __init__(self, totalPower, date, time, zone, season):
        self.totalPower = totalPower
        self.date = date
        self.time = time
        self.zone = zone
        self.season = season

class Device:
    def __init__(self, name, type, powerRating, age, zones, counter = 0, final_power = 0, single_use_power = 0, morning_power = 0, midday_power = 0, evening_power = 0, night_power = 0, cap = None):
        self.name = name
        self.type = type
        self.powerRating = powerRating
        self.age = age
        self.zones = zones
        self.counter = counter
        self.single_use_power = single_use_power
        self.final_power = final_power
        
        #used in processing to ensure not every instance of the device will be accounted for as a use
        self.cap = cap

        self.morning_power = morning_power
        self.midday_power = midday_power
        self.evening_power = evening_power
        self.night_power = night_power

class LogDevices:
    def __init__(self, log, devices):
        self.log = log # log object containing the csv log information
        self.devices = devices # a list of device objects eligible for use in that log

        

def main(date):
    if checkUserCSVcontent() == False:
        return 
    
    date = datetime.strptime(date, "%Y-%m-%d")
    month = date.month
    season = getSeason(month=month)
    date = date.strftime("%d-%m-%Y")

    #list of log objects which are in spec date
    logs_list = get_logs_by_date(date=date)

    #list of device objects with all users devices
    devices_list = get_devices()

    eligible_devices_object_list = []#contains a list of a list of device objects which have matching zones per log

    #LOGDEVICES OBJECT LIST
    log_devices_list = []

    #create forced float var as we need to handle decimals and round for output
    daily_power_use:float
    daily_power_use = 0

    #variable will be added to with each devices final output
    overall_power = 0

    for log in logs_list:
        log_power:float
        log_power = float(log.totalPower)
        daily_power_use = daily_power_use + log_power
        daily_power_use = round(daily_power_use, 2)
        rawDevices = check_device_in_log_zone(devices=devices_list, zone=log.zone)
        eligible_devices_object_list.append(rawDevices)
        logdevices = LogDevices(log=log, devices=rawDevices)
        log_devices_list.append(logdevices)

    #for device in devices_list:
        #device.final_power = total_device_usage(device=device, season=season)

        #print("Name:",device.name, "\nTotal Energy Usage (in day):",device.final_power,"kWh", "\nCount:", device.counter,"\n")
        #overall_power += device.final_power 

    morning_zone_list = []
    midday_zone_list = []
    evening_zone_list = []
    night_zone_list = []

    for obj in log_devices_list:
        #print("\n==========",obj.log.time, obj.log.totalPower,"==========")
        for device in obj.devices:
            #call a power reading method to add to devices power based off of appearances of the logs
            final_power = 0
            #returns an addition of 1 instance of usage of a device and goes through every instance of all devices
            final_power += log_device_usage(device, obj.log.totalPower)
            device.final_power += final_power
            device.counter += 1
            #print(device.name, "-", round(device.final_power,2), "-", device.counter)
            
            if obj.log.zone == 'morning':
                device.morning_power += final_power
                morning_zone_list.append(obj)
            
            elif obj.log.zone == 'midday':
                device.midday_power += final_power       
                midday_zone_list.append(obj)

            elif obj.log.zone == 'evening':
                device.evening_power += final_power
                evening_zone_list.append(obj)

            elif obj.log.zone == 'night':
                device.night_power += final_power           
                night_zone_list.append(obj)
    
    zone = "morning"
    morning_devices = check_device_in_log_zone(devices_list, zone)

    zone = "midday"
    midday_devices = check_device_in_log_zone(devices_list, zone)

    zone = "evening"
    evening_devices = check_device_in_log_zone(devices_list, zone)

    zone = "night"
    night_devices = check_device_in_log_zone(devices_list, zone)

    #print("Data Total Usage: ", daily_power_use)
    #print("Estimation Total Usage: ", round(overall_power, 2))
    return devices_list, daily_power_use, date, morning_devices, midday_devices, evening_devices, night_devices

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

def log_device_usage(device, log_total_power):
    log_power_wattage = float(log_total_power) * 1000 #total watt-hour usage in the 30 min log

    #new power rating using compound increase regarding age of device to convert into more accuarate reading
    device_power_rating = calculate_power_increase(original_power=device.powerRating, age=device.age)
    device.powerRating = device_power_rating

    #calculate how much power each device would use in a single instance of a log
    devices_power_usage = calculate_power(device.type, device.powerRating)
    return devices_power_usage


#returns a new value for the power rating of the devices according to its age as efficiency decreases 1-2% per year per device
def calculate_power_increase(original_power, age, increase_rate=1.5):
    rate_decimal = increase_rate / 100
    new_power = original_power * ((1 + rate_decimal) ** age)
    return new_power


#TOTAL DAY DEVICE USAGE
def total_device_usage(device, season):
    count = device.counter
    power_rating = device.powerRating #this also represents the devices watt-hour usage
    type = device.type
    zone_amount = len(device.zones)
    max_usage = power_rating / 2#as the log is 30 min the maximum device usage in watt-hours can only be its power rating divided by 2
    rel_max_usage = max_usage*count#have to multiply by how many times the device has appeared in the logs
    average_household_people = 2.36

    match type:
        #Kitchen Devices
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
        
        case 'oven':
            #no more than 1 hour of use at a time == 2 logs
            #no more than 2 logs per zone as use 1 time per zone
            #use time is complete 2 30min logs
            #uses around max power usage at all time
            total_usage = max_usage * zone_amount # max usage of a log times how many zones the oven has appeared in
            total_usage = total_usage * 2 # times by two as realistically used maximum 2 logs per zone
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

        case 'microwave':# aorund 6ish minuted for general cooked meal in microwave, only can be used 2/3 times per cooking meals - three eating times a day so 4/5 logs
            time_in_use_percent = 6 / 30
            if count > 5:
                count = 5
            total_usage = max_usage * time_in_use_percent
            total_usage = total_usage * count
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'dishwasher':
            #average use time around 1 hour == 2 logs
            #average use 1-2 times a day so 1.5 
            #uses full power rating at all times
            total_usage = zone_amount * max_usage #say used 1 time per zone
            total_usage = total_usage * 1.5 #avg used 1-2 times per day
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'toaster':
            #2-3 mins avg use so 2.5
            time_in_use_percent = 2.5 / 30
            total_usage = zone_amount * max_usage
            total_usage = total_usage * time_in_use_percent
            total_usage = total_usage * average_household_people
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'kettle':#kettle used for 2 minutes at full load at a time
            time_in_use_percent = 2 / 30#2 minutes out of the 30 min log
            total_usage = rel_max_usage * time_in_use_percent
            total_usage = float(total_usage / 1000)#divide by 1000 to convert to kwh not wh 
            total_usage = round(total_usage, 2)
            return total_usage # divide by 1000 as we need kWh not wH
        
        case 'fryer':
            #used between 15 - 20 mins for cooking typical food
            #could be used for multiple elements of meal so x 2 for cooking multiple things
            #can be used for all meals
            time_in_use_percent = 17.5 / 30
            total_usage = zone_amount * max_usage #given it is used one time per zone
            total_usage = total_usage * 2 #given 2 uses for each time it appears for a meal
            total_usage = total_usage * time_in_use_percent # apply the percent of time in the log it would be used for
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage

        case 'blender':
            #used 1-2 times a day
            #actual usage is very low around 2-3 minutes actual blend time
            #max 2 times per zone as preparing things for meal 
            time_in_use_percent = 2.5 / 30
            total_usage = max_usage * time_in_use_percent
            total_usage = total_usage * 2
            total_usage = total_usage * zone_amount
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'slowcooker':
            #average slow cooker cooking time between 6 to 8 hours
            #obviously no more then 1 time a day as left on throughout day for meal at tea time
            total_usage = max_usage
            total_usage = max_usage * 14 # times 7 hours == 14 logs as it is between 6-8 in middle and we need to rely on average trends
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage

        #Bedroom Devices
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
                
        case 'sound_system':
            #usage matched with computer usage time and/or TV usage time
            #since a very low power device can say it is used maybe a little more than probably i
            #give value used for 80% of times it appears in a log
            usage = rel_max_usage * 0.8
            total_usage = usage
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        #Living Room Devices
        case 'tv':#tv usually used for hours at time, or left on so we take full 30min as constantly in use, europe avg is 3-4 hours a day so we say 3.5hours which = 7 logs
            if count > 7:
                count = 7 # if the count says the tv appears more then 7 logs in a day then we reduce as it is unlikely the tv to be used more then 3.5 hours          
            total_usage = max_usage * count
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'console':
            #average usages in uk say 3 hours a day of use
            #6 logs macx usage a day on average - do this for each zone, so 6 max logs per zone
            #most time on cnosole is gaming on full load, not in menus or desktop like a pc can be
            if count > 6:
                count = 6

            total_usage = max_usage * count
            total_usage = total_usage * zone_amount
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'entertainment_system':
            #similar usage pattern to tv usages
            if count > 7:
                count = 7 # matching max count with the same as the tv usages  
            total_usage = max_usage * count
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        #Misc Devices
        case 'washing_machine':
            #1 hour average use == 2 logs
            time_used_in_day = 0.7397260273972602 #this value is a average household in uk uses per year 270 / 365 days in year
            total_usage = max_usage * time_used_in_day
            total_usage = total_usage * zone_amount
            total_usage = total_usage * 2 #to account for 2 logs for an hour typical wash
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'dryer':
            #no information regarding average use of a tumble dryer daily/weekly or yearly
            #lets say an average of 66% of use of the washing machine u also use the dryer and do not hang washing out on clothes line - no information regarding it
            #2.5 hours average dryer time usage
            percentage_use_in_year = 370 * 0.66 # == times used in year
            per = percentage_use_in_year / 365
            total_usage = max_usage * 6 # 6 logs for a 3 hour usage
            total_usage = total_usage * per
            total_usage = float(total_usage / 1000)
            total_usage = round(total_usage, 2)
            return total_usage
        
        case 'fan':
            #only typically used in summer/hot months
            if season != 'summer':
                return 0
            else:
                total_usage = rel_max_usage
                total_usage = float(total_usage / 1000)
                total_usage = round(total_usage, 2)

                return total_usage
        
        case 'heater':
            #no more then 20 mins or so to warm up room when cold
            #only used in winter on average
            #used no more then 1 interval per hour so avg 3/4 times a zone
            if season != 'winter':
                return 0
            else:
                percent = 20 / 30
                total_usage = max_usage
                total_usage = total_usage * percent
                total_usage = zone_amount * total_usage
                total_usage = total_usage * 3.5 # for a use of 3/4 times per day zone
                total_usage = float(total_usage / 1000)
                total_usage = round(total_usage, 2)
                return total_usage


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
            device.final_power = round(device.final_power, 2)
            device.morning_power = round(device.morning_power, 2)
            device.midday_power = round(device.midday_power, 2)
            device.evening_power = round(device.evening_power, 2)
            device.night_power = round(device.night_power, 2)

            returndevices.append(device)

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