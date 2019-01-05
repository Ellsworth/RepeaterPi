from influxdb import InfluxDBClient
from subprocess import check_output
import configparser
import time
import serial
import sys

__version__ = "2.5"
__author__ = "Erich Ellsworth"
__contact__ = "erich.ellsworth@g.austincc.edu"

# Need to tell where to find the cfg if running from systemd
config_file = '/root/RepeaterPi/config.ini'

if len(sys.argv) > 1 and sys.argv[1] == "--test":
        config_file = './config_example.ini'

print(sys.argv)

config = configparser.ConfigParser()
config.read(config_file)

# Config stuff
repeater_location = config['Basic']['repeater_location']
repeater_name = config['Basic']['repeater_name']
main_cal = config['calibration']['main_cal']
amplifier_cal = config['calibration']['amplifier_cal']
fwd_pwr_cal = config['calibration']['pwr_fwd']
rev_pwr_cal = config['calibration']['pwr_rev']
serial_port = config['Basic']['serial_port']

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
arduinoData = [0, 0, 0, 0, 0, 0] # 0 temp, 1 main, 2 amp, 3 fwd, 4 rev, 5 5v ref
tempHistory = [0, 0, 0, 0, 0, 0]
voltage = [0, 0, 0, 0]
x = 0
startup = True

# Intro message
print("RepeaterPi %sv by KG5KEY on %s\n" % (__version__, repeater_name))
print("Copyright (C) 2017 Erich Ellsworth\n" +
    "Contact: " + __contact__)

# gets the data from the ADC and converts it to raw voltage
def getVoltage(channel):
    return (float(arduinoData[channel]) * (float(arduinoData[5]) * .001) / float(1023))
    #return float((float(arduinoData[channel]) * 5.0 / float(1023)))

def scaleVoltage(channel):
    rv = (getVoltage(channel) * (61/11))
    if rv < 1:
        rv = 0
    return rv

def scaleWattage(channel):
    return ((75 * getVoltage(channel)) / 3.3)

# calculates temp
def calcTemp(channel):
    temp = round(float(((((getVoltage(channel) * 1000) - 500) / 10) * 9 / 5 + 32)), 2)
    if abs(temp - tempHistory[0]) > 4:
        temp = tempHistory[0]
    return float(temp)


def getPiTemp():
    cputemp = check_output(['/opt/vc/bin/vcgencmd', 'measure_temp'])
    cputemp = str(cputemp[5:9])
    for char in "b'":
        cputemp = cputemp.replace(char,'')
    return cputemp


def genTelemetry():
    print("--------------------------------------")
    print("Telemetry for " + str(time.asctime(time.localtime(time.time()))))
    print("Temperature: " + str(tempHistory[0]) + " Pi Temp: " + str(getPiTemp()))
    print("Primary: " + str(voltage[0]) + "v Amplifier: " + str(voltage[1]) + "v")
    print("fwd " + str(pwr_fwd) +  " rev " + str(pwr_rev))
    print("Arduino Data: " + str(arduinoData))
    print("x = " + str(x))



def calibrateTemp(channel):
    temp = round(float(((((getVoltage(channel) * 1000) - 500) / 10) * 9 / 5 + 32)), 2)
    return ([temp, temp, temp, temp, temp, temp])



def getSerialData():
    serialdata = str(serialPort.readline())
    for char in "b'rn":
        serialdata = serialdata.replace(char,'')
    for char in "\\":
        serialdata = serialdata.replace(char,'')
    return(serialdata.split(","))


def tempAverage(var):
    tempHistory[5] = tempHistory[4]
    tempHistory[4] = tempHistory[3]
    tempHistory[3] = tempHistory[2]
    tempHistory[2] = tempHistory[1]
    tempHistory[1] = var
    tempHistory[0] = round((tempHistory[1] + tempHistory[2] +
        tempHistory[3] + tempHistory[4] + tempHistory[5]) / 5, 2)
    return tempHistory

def updateDashboard():
    json_body = [
        {
            "measurement": repeater_location,
            "tags": {
                "use": "null",
            },
            "fields": {
                "temp": calcTemp(0),
                "temp_pi": float(getPiTemp()),
                "v_main": voltage[0],
                "v_amp": voltage[1],
                "arduino": str(round(float(arduinoData[5]) * 0.001, 3)),
                "pwr_fwd": pwr_fwd,
                "pwr_rev": pwr_rev,
            }
        }
    ]
    print("Sending data to " + hostname)


    client.write_points(json_body)
    print("Done sending data.")


if len(sys.argv) > 1:
    if sys.argv[1] == "--copyright":
        print("\nThis program is free software: you can redistribute it and/or modify\n" +
            "it under the terms of the GNU General Public License as published by\n" +
            "the Free Software Foundation, either version 3 of the License, or\n" +
            "(at your option) any later version.\n\n" +
            "This program is distributed in the hope that it will be useful,\n" +
            "but WITHOUT ANY WARRANTY; without even the implied warranty of\n" +
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n" +
            "GNU General Public License for more details.\n\n" +
            "You should have received a copy of the GNU General Public License\n" +
            "along with this program. If not, see <http://www.gnu.org/licenses/>.")
    if sys.argv[1] == "--test":
        print("\n--- Start Report  ---")
        print("Python: " + sys.version)
        print("PySerial: " + str(serial.__version__))
        print("RepeaterPi: " + str(__version__))
        print("--- End of Report ---")

    sys.exit(0)

print("To view the copyright information, run RepeaterPi.py with the " +
    "--copyright argument.")


if __name__ == '__main__':

    print("\nStarting RepeaterPi service...")

    # Serial setup
    serialPort.baudrate = 9600
    serialPort.port = serial_port
    serialPort.open()

    x = 0
    startup = True

    print("Reading data from Arduino, this may take up to 15 seconds.")

    arduinoData = getSerialData()
    tempHistory = calibrateTemp(0)

    voltage[0] = (round(float(scaleVoltage(1)) * float(main_cal), 2))
    voltage[1] = (round(float(scaleVoltage(2)) * float(amplifier_cal), 2))
    voltage[2] = voltage[0]
    voltage[3] = voltage[1]
    pwr_fwd = (scaleWattage(3) * float(fwd_pwr_cal))
    pwr_rev = (scaleWattage(4) * float(rev_pwr_cal))
    updateDashboard()

    startup = False

    while True:
        arduinoData = getSerialData()
        tempAverage(calcTemp(0))

        voltage[0] = (round(float(scaleVoltage(1)) * float(main_cal), 2))
        voltage[1] = (round(float(scaleVoltage(2)) * float(amplifier_cal), 2))
        pwr_fwd = (scaleWattage(3) * float(fwd_pwr_cal))
        pwr_rev = (scaleWattage(4) * float(rev_pwr_cal))

        genTelemetry()

        if abs(voltage[0] - voltage[2]) > .3 or abs(voltage[1] - voltage[3]) > .3 or x > 60 or pwr_fwd > 5:

            updateDashboard()
            voltage[2] = voltage[0]
            voltage[3] = voltage[1]
            x = 0
        else:
            x += 1

        time.sleep(15)
