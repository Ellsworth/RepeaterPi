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
    return (arduinoData[channel] * 3.3) / float(1023)


# scales the raw voltage to the true value read by the voltage probes
def scale_voltage(channel):
    rv = (getVoltage(channel) * (61/11))
    if rv < 1:
        return 0
    else:
        return rv


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
        print(genTelemetry())
        voltage[2] = voltage[0]
        voltage[3] = voltage[1]
    except:
        print("An error occurred trying to upload data to Adafruit IO")



def updateSensors(): # redo this
    serialdata = str(serialPort.readline())
    for char in "b'rn":
            serialdata = serialdata.replace(char,'')
    for char in "\\":
            serialdata = serialdata.replace(char,'')
    arduinoData = serialdata.split(",")

    temp = calcTemp(0)
    if abs(temp - tempHistory[0]) > 7:
        tempAverage(tempHistory[0])
    else:
        tempAverage(temp)

    voltage[0] = (round(float(scale_voltage(1)) * float(main_cal), 2))
    voltage[1] = (round(float(scale_voltage(2)) * float(amplifier_cal), 2))


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

# calibrating the temp sensor so we can throw out the bad eggs...
print("Calibrating temperature sensor...")
while x < 6:
    updateSensors()
    x += 1
    time.sleep(1)
    print(arduinoData)
    print(tempHistory)
print("Finished calibrating temperature sensor.")
updateAdafruit()
x = 0
y = 0
startup = False
outage = False
outage_start = ''

while True:
    # Update stuff...
    if abs(voltage[0] - voltage[2]) > .05 or abs(voltage[1] - voltage[3]) > .05 or x > 14:
        updateAdafruit()
        x = 0
    else:
        x += 1

    if voltage[1] == 0:
        print("Warning, Possible outage detected. ")
        if outage == False:
            outage_start = str(time.asctime(time.localtime(time.time())))
        outage = True
        y += 1

    if voltage[1] != 0 and outage:
        sendMail(email_username, email_password, "There was an outage for " + str(y) + " minutes at the " +
                  config['Basic']['repeater_name'] + " repeater site that began at " + outage_start + ".\n" +
                  genTelemetry(), email_raw, "Possible outage ended at " + config['Basic']['repeater_name'])
        print("There was an outage for " + str(y) + " minutes!")
        outage = False
        y = 0
    if y == 1:
        sendMail(email_username, email_password, "There is an outage detected at the " +
                  config['Basic']['repeater_name'] + " repeater site that began at " + outage_start + ".\n" +
                  genTelemetry(), email_raw, "Possible outage detected at " + config['Basic']['repeater_name'])



    time.sleep(60)
    updateSensors()
