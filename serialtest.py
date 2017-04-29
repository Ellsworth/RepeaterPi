import serial

print("RepeaterPi Serial Tester...")
print("Reading data from Arduino, this may take up to 60 seconds.")

ser = serial.Serial('/dev/ttyUSB0')  # open serial port

serialdata = str(ser.readline())
print(serialdata)
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
    rv = (get_voltage(channel) * (61/11))
    if rv < 1:
        return 0
    else:
        return rv

print("Raw Arduino Data: " + str(arduinoData))
print("\nTemperature: " + str(calcTemp(0)) + "F")
print("Main: " + str(getVoltage(1))) + "v Amp: " + str(scaleVoltage(1)) + "v")
print("Arduino Supply Voltage : " + str(arduinoData) + "mV")
