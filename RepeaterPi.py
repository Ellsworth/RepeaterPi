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
    return (float(arduinoData[channel]) * (float(arduinoData[3]) * .0001) / float(1023))


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
        voltage[2] = voltage[0]
        voltage[3] = voltage[1]
    except:
        print("An error occurred trying to upload data to Adafruit IO")


def updateSensors():
    serialdata = str(serialPort.readline())
    for char in "b'rn":
        serialdata = serialdata.replace(char,'')
    for char in "\\":
        serialdata = serialdata.replace(char,'')
    arduinoData = serialdata.split(",")
    print(arduinoData)


    voltage[0] = (round(float(scaleVoltage(1)) * float(main_cal), 2))
    voltage[1] = (round(float(scaleVoltage(2)) * float(amplifier_cal), 2))

    temp = calcTemp(0)
    if abs(temp - tempHistory[0]) > 7:
        tempAverage(tempHistory[0])
    else:
        tempAverage(temp)


def tempAverage(var):
    tempHistory[5] = tempHistory[4]
    tempHistory[4] = tempHistory[3]
    tempHistory[3] = tempHistory[2]
    tempHistory[2] = tempHistory[1]
    tempHistory[1] = var
    tempHistory[0] = round((tempHistory[1] + tempHistory[2] + tempHistory[3] + tempHistory[4] + tempHistory[5]) / 5, 2)


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
            "Subject: Repeater Pi Alert @ " + repeater_location + "\n" \
            "To: " + str(email_list) + "\n" \
            + message

print("\nStarting RepeaterPi service...")

print(getVoltage(0))
print(calcTemp(0))
