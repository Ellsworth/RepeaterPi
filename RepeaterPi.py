from Adafruit_IO import Client
from subprocess import check_output
import configparser
import time
import smtplib
import serial
import sys

__version__ = "2.4"
__author__ = "Erich Ellsworth"
__contact__ = "erich.ellsworth@g.austincc.edu"

# reading config, don't ask please.
config_file = '/root/RepeaterPi/config.ini'

if len(sys.argv) > 1 and sys.argv[1] == "--test":
        config_file = 'config_example.ini'

config = configparser.ConfigParser()
config.read(config_file)

# Config stuff
aio = Client(config['AdafruitIO']['AIO_Key'])
repeater_location = config['Basic']['repeater_location']
repeater_name = config['Basic']['repeater_name']
main_cal = config['Basic']['main_cal']
amplifier_cal = config['Basic']['amplifier_cal']
serial_port = config['Basic']['serial_port']

# email config
email_username = config['Email']['username']
email_password = config['Email']['password']
email_list = config['Email']['email_list']
email_raw = config['Email']['email_raw']
email_raw = email_raw.split()

# Serial setup
serialPort = serial.Serial()  # open serial port

# average is 0, most recent 1, least recent 0
serialdata = ""
arduinoData = [0, 0, 0, 0] # temp, main, amp, 5v ref voltage
tempHistory = [0, 0, 0, 0, 0, 0]
voltage = [0, 0, 0, 0]
x = 0
startup = True
sent_amp_alert_email = False

# Intro message
print("RepeaterPi %sv by KG5KEY on %s\n" % (__version__, repeater_name))
print("Copyright (C) 2017 Erich Ellsworth\n" +
    "Contact: " + __contact__)

# gets the data from the ADC and converts it to raw voltage
def getVoltage(channel):
    return (float(arduinoData[channel]) * (float(arduinoData[3]) * .001) / float(1023))


def scaleVoltage(channel):
    rv = (getVoltage(channel) * (61/11))
    if rv < 1:
        return 0
    else:
        return rv


# calculates temp
def calcTemp(channel):
    temp = round(float(((((getVoltage(channel) * 1000) - 500) / 10) * 9 / 5 + 32)), 2)
    if abs(temp - tempHistory[0]) > 4:
        temp = tempHistory[0]
    return temp


def getPiTemp():
    cputemp = check_output(['/opt/vc/bin/vcgencmd', 'measure_temp'])
    cputemp = str(cputemp[5:9])
    for char in "b'":
        cputemp = cputemp.replace(char,'')
    return cputemp


def genTelemetry():
    return("-------------------------------------- \nTelemetry for " +
            str(time.asctime(time.localtime(time.time()))) +
            "\nPrimary: " + str(voltage[0]) +
            "v Amplifier: " + str(voltage[1]) +
            "v" + "\nTemperature: " + str(tempHistory[0]) +
            " Degrees Fahrenheit\nTemperature History: " + str(tempHistory))



def updateAdafruit():
    try:
        aio.send(repeater_location + '-temp', tempHistory[0])
        aio.send(repeater_location + '-main-power', voltage[0])
        aio.send(repeater_location + '-amplifier-power', voltage[1])

        aio.send(repeater_location + '-arduino-supply', (int(arduinoData[3]) / 1000))
        aio.send(repeater_location + '-cpu-temp', getPiTemp())
        print("Updating Adafruit IO...")
    except:
        print("An error occurred trying to upload data to Adafruit IO")


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


def updateSensors():
    arduinoData = getSerialData()
    tempAverage(calcTemp(0))

    voltage[0] = (round(float(scaleVoltage(1)) * float(main_cal), 2))
    voltage[1] = (round(float(scaleVoltage(2)) * float(amplifier_cal), 2))


def tempAverage(var):
    tempHistory[5] = tempHistory[4]
    tempHistory[4] = tempHistory[3]
    tempHistory[3] = tempHistory[2]
    tempHistory[2] = tempHistory[1]
    tempHistory[1] = var
    tempHistory[0] = round((tempHistory[1] + tempHistory[2] +
        tempHistory[3] + tempHistory[4] + tempHistory[5]) / 5, 2)
    return tempHistory


def sendMail(user, password, msg, recipient, subject):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        msg = 'Subject: %s\n\n%s' % (subject, msg)
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.sendmail(user, recipient, msg)
        smtplib.SMTP()
    except:
        print("Error sending the email. Possible internet outage detected...")


def formatEmail(message):
    return "From: RepeaterPi <" + email_username + ">\n" \
            "Subject: RepeaterPi Alert @ " + repeater_location + "\n" \
            "To: " + str(email_list) + "\n" \
            + message

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


serialPort.baudrate = 9600
serialPort.port = serial_port
serialPort.open()

x = 0
y = 0

startup = True
outage = False

outage_start = ''


print("Reading data from Arduino, this may take up to 60 seconds.")

arduinoData = getSerialData()
tempHistory = calibrateTemp(0)

voltage[0] = (round(float(scaleVoltage(1)) * float(main_cal), 2))
voltage[1] = (round(float(scaleVoltage(2)) * float(amplifier_cal), 2))
voltage[2] = voltage[0]
voltage[3] = voltage[1]
updateAdafruit()

startup = False

if __name__ == '__main__':
    print("\nStarting RepeaterPi service...")

    while True:
        arduinoData = getSerialData()
        tempAverage(calcTemp(0))

        voltage[0] = (round(float(scaleVoltage(1)) * float(main_cal), 2))
        voltage[1] = (round(float(scaleVoltage(2)) * float(amplifier_cal), 2))

        if abs(voltage[0] - voltage[2]) > .3 or abs(voltage[1] - voltage[3]) > .3 or x > 14:
            updateAdafruit()
            voltage[2] = voltage[0]
            voltage[3] = voltage[1]
            x = 0
        else:
            x += 1

        if voltage[1] == 0 and outage == False:
            print("Warning, Possible outage detected.")
            outage_start = str(time.asctime(time.localtime(time.time())))
            outage = True
            sendMail(email_username, email_password, "There is an outage detected at the " +
                repeater_name + " repeater site that began at " + outage_start + ".\n" +
                genTelemetry(), email_raw, "Possible outage detected at " + repeater_name)
            y += 1


        if voltage[1] != 0 and outage:
            sendMail(email_username, email_password, "There was an outage for " + str(y) + " minutes at the " +
                repeater_name + " repeater site that began at " + outage_start + ".\n" +
                genTelemetry(), email_raw, "Possible outage ended at " + repeater_name)
            print("There was an outage for " + str(y) + " minutes.")
            outage = False
            y = 0


        print(genTelemetry())
        time.sleep(60)
