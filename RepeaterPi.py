import serial

import time
from math import sqrt

from subprocess import check_output
from influxdb import InfluxDBClient

import configparser

__version__ = "3"
__author__ = "Erich Ellsworth, KG5KEY"
__contact__ = "kg5key@kg5key.com"

# Need to tell where to find the cfg if running from systemd
config_file = 'config.ini'

config = configparser.ConfigParser()
config.read(config_file)

# Config stuff
repeater_location = config['Basic']['repeater_location']
repeater_name = config['Basic']['repeater_name']
serial_port = config['Basic']['serial_port']

serial_calibration = [(config['calibration']['temp_cal']),
    (config['calibration']['pres_cal']),
    (config['calibration']['main_cal']),
    (config['calibration']['amplifier_cal']),
    (config['calibration']['pwr_fwd']),
    (config['calibration']['pwr_rev'])]


# InfluxDB Login
hostname = config['Grafana']['hostname']
port = config['Grafana']['port']
username = config['Grafana']['username']
password = config['Grafana']['password']
database = config['Grafana']['database']

# Setup InfluxDB client
client = InfluxDBClient(hostname, port, username, password, database)

# Load serial library
serialPort = serial.Serial()

# average is 0, most recent 1, least recent 0
serialdata = ""
# temp_f, pressure, main.voltage, amp.voltage, fwd.voltage, rev.voltage
arduinoData = [0, 0, 0, 0, 0, 0] # 0 temp_f, 1 pressure_mb, 2 main, 3 amp, 4 fwd, 5 rev,
voltage = [0, 0, 0, 0]
x = 0

converted_data = [0,0,0,0,0,0]

# Intro message
print("RepeaterPi %sv by KG5KEY on %s\n" % (__version__, repeater_name))

def scaleVoltage(voltage):
    rv = (voltage * (61/11))
    if rv < 1:
        rv = 0
    return rv

def scaleWattage(voltage):
    return ((75 * voltage) / 3.3)


def getPiTemp():
    #cputemp = check_output(['/opt/vc/bin/vcgencmd', 'measure_temp'])
    #cputemp = str(cputemp[5:9])
    #for char in "b'":
    #    cputemp = cputemp.replace(char,'')
    cputemp = 0
    return cputemp

def calc_swr(fwd, rev):
    if fwd <= 0 or rev <= 0 or (fwd - rev) <= 0:
        return float(1.00)
    else:
        swr = (1 + sqrt(rev / fwd)) / (1 - sqrt(rev / fwd))
        return round(float(swr), 2)

def getSerialData():
    serialdata = str(serialPort.readline())
    for char in "b'rn":
        serialdata = serialdata.replace(char,'')
    for char in "\\":
        serialdata = serialdata.replace(char,'')
    return(serialdata.split(" "))

def convertData(data):

    converted_data[0] = data[0] # Temperature
    converted_data[1] = data[1] # Pressure

    converted_data[2] = round(scaleVoltage(data[2]), 2) # Primary Voltage
    converted_data[3] = round(scaleVoltage(data[3]), 2) # Amp Voltage

    converted_data[4] = round(scaleWattage(data[4]), 1) # Forward Power
    converted_data[5] = round(scaleWattage(data[5]), 1) # Reverse Power

    return converted_data


def updateDashboard(info):
    json_body = [
        {
            "measurement": repeater_location,
            "tags": {
                "use": "null",
            },
            "fields": {
                "temperature": float(info[0]),
                "pressure": float(info[1]),
                "temperature_pi": float(getPiTemp()),
                "voltage_main": float(info[2]),
                "voltage_amp": float(info[3]),
                "arduino": 0,
                "pwr_fwd": info[4],
                "pwr_rev": info[5],
                "SWR": calc_swr(info[4], info[5]),
            }
        }
    ]
    print("Sending data to " + hostname + "...", end="")

    client.write_points(json_body)
    print(" Done sending data.")

def printData(info):
    print("Temperature: %s F, Pressure: %s mb" % (info[0], info[1]))
    print("Main Supply: %s V, Amplifier Supply: %s V" % (info[2], info[3]))
    print("Forward Power: %s W, Reverse Power: %s W, SWR: %s" % (info[4], info[5], calc_swr(info[4],info[5])))



if __name__ == '__main__':

    print("\nStarting RepeaterPi service...")

    # Serial setup
    serialPort.baudrate = 9600
    serialPort.port = serial_port
    serialPort.open()

    while True:
        #"temperature,voltage_main,voltage_amp,forward_power,reverse_power")
        serial_raw = getSerialData()
        print('-----------------------------------------------------')

        data = [float(serial_raw[i]) + float(serial_calibration[i]) for i in range(len(serial_raw))]

        converted_data = convertData(data)

        updateDashboard(converted_data)
        print(serial_raw)
        printData(converted_data)
