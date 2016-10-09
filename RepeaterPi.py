import configparser
import Adafruit_GPIO.SPI
import Adafruit_MCP3008
import time
from Adafruit_IO import Client

# Hardwa re SPI configuration:
mcp = Adafruit_MCP3008.MCP3008(spi=Adafruit_GPIO.SPI.SpiDev(0, 0))

# Config reading, dont ask please.
config = configparser.ConfigParser()
config.read('/root/RepeaterPi/config.ini')
aio = Client(config['AdafruitIO']['AIO_Key'])
repeater_location = config['Basic']['repeater_location']
main_cal = config['Basic']['main_cal']
amplifier_cal = config['Basic']['amplifier_cal']

print("RepeaterPi 1.2v by KG5KEY on " + config['Basic']['repeater_name'])


# defining core funtions
def get_voltage(channel):
    return (mcp.read_adc(channel) * 3.3) / float(1023)

def scale_voltage(channel):
    voltage = ((get_voltage(channel) * 16) / float(3.3))
    if voltage < 1:
        return 0.0
    else:
        return float(voltage)

def calc_temp(channel):
    return float(((((get_voltage(7) * 1000) - 500) / 10)) * 9 / 5 + 32)

temp = 0
old_temp = 0
main_power = 0
amplifier_power = 0


def gen_Telemetry():
    return ("-------------------------------------- \nTelemetry for " +
          str(time.asctime(time.localtime(time.time()))) +
          "\nPrimary: " + str(main_power) +
          "v Amplifier: " + str(amplifier_power) +
          "v" + "\nTemperature: " + str(temp) + " Degrees Fahrenheit\n")

def updateAdafruitIO():
    aio.send(repeater_location + '-temp', temp)
    aio.send(repeater_location + '-main-power', main_power)
    aio.send(repeater_location + '-amplifier-power', amplifier_power)
    print(gen_Telemetry())

def isValid(current, previous):
    return abs(((current - previous) / previous) * 100) < 8

def updateSensors():
    temp = (round(calc_temp(7), 2))
    main_power = (round(float(scale_voltage(0)) * float(main_cal), 2))
    amplifier_power = (round(float(scale_voltage(1)) * float(amplifier_cal), 2))


print("\nStarting RepeaterPi service...")

while True:
    updateSensors()
    if isValid(temp, old_temp) == True:
        updateAdafruitIO()
    else:
        updateSensors()
        updateAdafruitIO()
    old_temp = temp
    time.sleep(300)
