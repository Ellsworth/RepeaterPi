import configparser
import time
import smtplib
import serial
from Adafruit_IO import Client

# reading config, don't ask please.
config = configparser.ConfigParser()
config.read('/root/RepeaterPi/config.ini')
aio = Client(config['AdafruitIO']['AIO_Key'])
repeater_location = config['Basic']['repeater_location']
main_cal = config['Basic']['main_cal']
amplifier_cal = config['Basic']['amplifier_cal']

# email config
email_username = config['Email']['username']
email_password = config['Email']['password']
email_list = config['Email']['email_list']
email_raw = config['Email']['email_raw']
email_raw = email_raw.split()

# Serial setup
serialPort = serial.Serial('/dev/ttyUSB0')  # open serial port


# average is 0, most recent 1, least recent 0
serialdata = ""
arduinoData = [0, 0, 0, 0] # temp, main, amp, 5v ref voltage
tempHistory = [0, 0, 0, 0, 0, 0]
voltage = [0, 0, 0, 0]
x = 0
startup = True
sent_amp_alert_email = False

print("RepeaterPi 2.0v by KG5KEY on " + config['Basic']['repeater_name'])


# gets the data from the ADC and converts it to raw voltage
def getVoltage(channel):
    return (float(arduinoData[channel]) * (float(arduinoData[3]) * .001) / float(1023))


def scaleVoltage(channel):
    return (getVoltage(channel) * (61/11))


# calculates temp
def calcTemp(channel):
    return round(float(((((getVoltage(channel) * 1000) - 500) / 10) * 9 / 5 + 32)), 2)


def genTelemetry():
    return ("-------------------------------------- \nTelemetry for " +
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
        aio.send(repeater_location + '-arduino-supply', arduinoData[3])
        voltage[2] = voltage[0]
        voltage[3] = voltage[1]
        print(Updating Adafruit IO...)
    except:
        print("An error occurred trying to upload data to Adafruit IO")

def calibrateTemp(temp):
    return ([temp, temp, temp, temp, temp, temp])
    updateAdafruit()


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
    tempHistory[0] = round((tempHistory[1] + tempHistory[2] + tempHistory[3] + tempHistory[4] + tempHistory[5]) / 5, 2)
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

print("\nStarting RepeaterPi service...")

x = 0
y = 0
startup = False
outage = False
outage_start = ''

arduinoData = getSerialData()
tempHistory = calibrateTemp(calcTemp(0))
updateAdafruit()


while True:
    arduinoData = getSerialData()

    tempAverage(calcTemp(0))
    voltage[0] = (round(float(scaleVoltage(1)) * float(main_cal), 2))
    voltage[1] = (round(float(scaleVoltage(2)) * float(amplifier_cal), 2))



    if abs(voltage[0] - voltage[2]) > .05 or abs(voltage[1] - voltage[3]) > .05 or x > 14:
        updateAdafruit()
        x = 0
    else:
        x += 1



    if voltage[1] == 0:
        if outage == False:
            print("Warning, Possible outage detected.")
            outage_start = str(time.asctime(time.localtime(time.time())))
        outage = True
        y += 1

    if voltage[1] != 0 and outage:
        sendMail(email_username, email_password, "There was an outage for " + str(y) + " minutes at the " +
                  config['Basic']['repeater_name'] + " repeater site that began at " + outage_start + ".\n" +
                  genTelemetry(), email_raw, "Possible outage ended at " + config['Basic']['repeater_name'])
        print("There was an outage for " + str(y) + " minutes.")
        outage = False
        y = 0
    if y == 1:
        sendMail(email_username, email_password, "There is an outage detected at the " +
                  config['Basic']['repeater_name'] + " repeater site that began at " + outage_start + ".\n" +
                  genTelemetry(), email_raw, "Possible outage detected at " + config['Basic']['repeater_name'])

    print(genTelemetry())
    time.sleep(60)
