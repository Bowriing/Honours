from flask_login import current_user

def ZoneFilter(devices):
    
    return_devices = []

    for device in devices:
        if 'morning' in device.timeZones:
            return_devices.append(device)
            print("Added device to filtered device list")

    return return_devices