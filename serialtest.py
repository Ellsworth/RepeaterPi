import serial
import configparser

config = configparser.ConfigParser()
config.read('/root/RepeaterPi/config.ini')

main_cal = config['Basic']['main_cal']
amplifier_cal = config['Basic']['amplifier_cal']

print("RepeaterPi Serial Tester...")
print("Reading data from Arduino, this may take up to 60 seconds.")

ser = serial.Serial('/dev/ttyUSB0')  # open serial

serialdata = str(ser.readline())

for char in "b'rn":
        serialdata = serialdata.replace(char,'')
for char in "\\":
        serialdata = serialdata.replace(char,'')

arduinoData = serialdata.split(",")

def getVoltage(channel):
    return (float(arduinoData[channel]) * (float(arduinoData[3]) * .001) / float(1023))

def calcTemp(channel):
    return round(float(((((getVoltage(channel) * 1000) - 500) / 10) * 9 / 5 + 32)), 2)

def scaleVoltage(channel):
    rv = (getVoltage(channel) * (61/11))
    if rv < 1:
        return 0
    else:
        return rv

print("\nRaw Arduino Data: " + str(arduinoData))
print("Temperature: " + str(calcTemp(0)) + "F")
print("Main: " + str((float(scaleVoltage(1)) * float(main_cal))) + "Amp: " + str(float((scaleVoltage(2)) * float(main_cal))))
print("Arduino Supply Voltage : " + str(arduinoData[3]) + "mV")
