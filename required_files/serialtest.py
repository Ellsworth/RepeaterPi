import serial
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

main_cal = config['Basic']['main_cal']
amplifier_cal = config['Basic']['amplifier_cal']
serial_port = config['Basic']['serial_port']

print("RepeaterPi Serial Tester...")
print("Reading data from Arduino, this may take up to 60 seconds.")

ser = serial.Serial(serial_port)  # open serial

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
print("Temperature: " + str(calcTemp(0)) + "F " + str(getVoltage(0)) + "v")
print("Main: " + str((float(scaleVoltage(1)) * float(main_cal))) + " Amp: " + str(float((scaleVoltage(2)) * float(main_cal))))
print("Main Raw: " + str(getVoltage(1)) + "v Amp Raw: " + str(getVoltage(2)) + "v")
print("Arduino Supply Voltage : " + str(arduinoData[3]) + "mV")
