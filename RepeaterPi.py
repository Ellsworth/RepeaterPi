import configparser
import Adafruit_GPIO.SPI
import Adafruit_MCP3008
import time
from Adafruit_IO import Client

# Hardware SPI configuration:
mcp = Adafruit_MCP3008.MCP3008(spi=Adafruit_GPIO.SPI.SpiDev(0, 0))

# Config configuration
config = configparser.ConfigParser()
config.read('/root/RepeaterPi/config.ini')
aio = Client(config['AdafruitIO']['AIO_Key'])
repeater_location = config['Basic']['repeater_name']
main_cal = config['Basic']['main_cal']
amplifier_cal = config['Basic']['amplifier_cal']

print("RepeaterPi v.1 by KG5KEY on " + repeater_location)

# don't mess with this please
temp = 0.0
main_power = 0.0
amplifier_power = 0.0

# defining core funtions
def get_voltage(channel):
  return (mcp.read_adc(channel) * float(config['Basic']['voltage33'])) / 1023

# nominal voltage should be 13.8v aka 2.502v as read directly by the ADC...
def scale_voltage(channel):
    voltage = round(((get_voltage(channel) * 16) / 2.615), 2) # not sure why this works... but it does so im going to let it be
    if (voltage < 1):
        voltage = 0.0
    else:
        return voltage

def calc_temp(channel):
    return round(((((get_voltage(7) * 1000) - 500) / 10)) * 9 / 5 + 32, 1) # I actually understand this, unlike scale_voltage()
 
def gen_Telemetry():
    return ("-------------------------------------- \nTelemetry for " +
          str(time.asctime(time.localtime(time.time()))) +
          "\nPrimary: " + str(main_power) +
          "v Amplifier: " + str(amplifier_power) +
          "v" + "\nTemperature: " + str(temp) + " Degrees Fahrenheit" + "\n--------------------------------------")

def updateAdafruitIO():
    temp = calc_temp(7)
    main_power = float(scale_voltage(0)) * float(main_cal)
    amplifier_power = float(scale_voltage(1)) * float(main_cal)
    aio.send(repeater_location + '-temp', temp)
    aio.send(repeater_location + '-main-power', main_power)
    aio.send(repeater_location + '-amplifier-power', amplifier_power)
    print("[" + str(time.asctime(time.localtime(time.time()))) + "] Updating AdafruitIO...")


print("\nStarting RepeaterPi service...")

while True:
    updateAdafruitIO()
    time.sleep(300)

