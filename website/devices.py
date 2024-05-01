def calculate_power(type, power_rating):
    #formulas for each devices behaviour for a use in a 30 min log
    time_in_use = 0#variable used for decimal representation of percentage of time in use in correlation to a 30 min log
    #we are mostly applying a percentage to cut down actual use of device
    #the time in use will be applied onto maximum possible usage to bring realistic average power use

    match type:
        case 'fridge':
            #compressor is on and off continously throughout use so using power only half the time
            power_usage = power_rating / 2
            return convert_to_kWh(power_usage)
        
        case 'oven':
            #used for over 30 mins so will consume max power in log
            return convert_to_kWh(power_rating)
        
        case 'hob':
            #typically no more then 20 mins per use on average for standard cooking
            time_in_use = 20/30
            power_usage = power_rating * time_in_use
            return convert_to_kWh(power_usage)
        
        case 'microwave':
            #typical usage is around 5 - 8 mins for standard meal or preheating
            time_in_use = 6.5 / 30
            power_usage = power_rating * time_in_use
            return convert_to_kWh(power_usage)
        
        case 'dishwasher':
            #use time for 1 hour so will be used for full time of log
            return convert_to_kWh(power_rating)
        
        case 'toaster':
            #2-3mins average use time
            time_in_use = 2.5 / 30
            power_usage = time_in_use * power_rating
            return convert_to_kWh(power_usage)
        
        case 'kettle':
            #3 mins average boil time for a kettle at full load all times
            time_in_use = 3 / 30
            power_usage = time_in_use * power_rating
            return convert_to_kWh(power_usage)
        
        case 'fryer':
            #15-20mins typical use
            time_in_use = 17.5 / 30
            power_usage = time_in_use * power_rating
            return convert_to_kWh(power_usage)
        
        case 'blender':
            #maximum 2 minutes of blend time per use
            time_in_use = 2 / 30
            power_usage = time_in_use * power_rating
            return convert_to_kWh(power_usage)
        
        case 'slowcooker':
            #can be used for hours at a time so full log time
            return convert_to_kWh(power_rating)
        
        case 'computer':
            #very varied use and little time using full power rating
            normal_power_usage = power_rating * 0.151 #only consumes 15.1% of power when in normal use
            normal_total = normal_power_usage * 0.925 #in this state 92.5% of time

            full_power_usage = power_rating
            full_total = full_power_usage * 0.075#only under full load arounf 7.5% of time in use

            #Final Total using the weighted use values
            power_usage = normal_total + full_total
            return convert_to_kWh(power_usage)
        
        case 'sound_system':
            #typical used for longer periods over a log time
            #usage depends on what audio is playing such as music and so
            #when turned on using max power rating 50% of time
            power_usage = power_rating / 2
            return convert_to_kWh(power_usage)
        
        case 'tv':
            #used for extended periods of time
            return convert_to_kWh(power_rating)
        
        case 'console':
            #uses pretty much full power whether gaming or video playback
            return convert_to_kWh(power_rating)
        
        case 'entertainment_system':
            #similar pattern to tv so full time use of log
            return convert_to_kWh(power_rating)
        
        case 'washing_machine':
            #used for full time in log
            #full load in use
            return convert_to_kWh(power_rating)
        
        case 'dryer':
            #used for full time in log
            return convert_to_kWh(power_rating)
        
        case 'fan':
            return convert_to_kWh(power_rating)
        
        case 'heater':
            return convert_to_kWh(power_rating)
        
def convert_to_kWh(power_usage):
    power_usage = power_usage / 2# need to half the value as og rating is in watt hours and we are working with 30 min intervals so for calculations need to half 
    power_usage = float(power_usage / 1000)
    return round(power_usage, 2)

def get_max_use(type):
    #returns the maximum amount of times a device can be used in a zone
    match type:  
        case 'oven':
            return 2
        
        case 'hob':
            return 2
        
        case 'microwave':
            return 3
        
        case 'dishwasher':
            return 1
        
        case 'toaster':
            return 2
        
        case 'kettle':
            return 6
        
        case 'fryer':
            return 2
        
        case 'blender':
            return 4
        
        case 'computer':
            return 6
        
        case 'sound_system':
            return 6
        
        case 'tv':
            return 6
        
        case 'console':
            return 5
        
        case 'entertainment_system':
            return 6
        
        case 'washing_machine':
            return 1
        
        case 'dryer':
            return 1
        
        case _:
            return None