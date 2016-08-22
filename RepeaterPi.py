import configparser
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import time
from Adafruit_IO import Client

# Hardware SPI configuration:
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(0, 0))

# Config configuration
config = configparser.ConfigParser()
config.read('config.ini')
aio = Client(config['AdafruitIO']['AIO_Key'])

print("RepeaterPi v.1 by KG5KEY on " + config['Basic']['repeater_name'])


# defining core funtions
def get_voltage(channel):
  return (mcp.read_adc(channel) * float(config['Basic']['voltage33'])) / 1023

# nominal voltage should be 13.8v aka 2.502v as read directly by the ADC...
def scale_voltage(channel):
    return round(((get_voltage(channel) * 16) / 2.9), 2)

def calc_temp(channel):
    return round(((((get_voltage(7) * 1000) - 500) / 10)) * 9 / 5 + 32, 1)
 
def gen_Telemetry():
    return ("-------------------------------------- \nTelemetry for " +
          str(time.asctime(time.localtime(time.time()))) +
          "\nPrimary: " + str(scale_voltage(0)) +
          "v Amplifier: " + str(scale_voltage(1)) +
          "v" + "\nTemperature: " + str(calc_temp(7)) + " Degrees Fahrenheit" + "\n--------------------------------------")

def updateAdafruitIO():
    aio.send(config['Basic']['repeater_location'] + '-temp', calc_temp(7))
    aio.send(config['Basic']['repeater_location'] + '-main-power', scale_voltage(0))
    aio.send(config['Basic']['repeater_location'] + '-amplifier-power', scale_voltage(1))
    print("Updating AdafruitIO...")
    print(gen_Telemetry())


print("\nStarting RepeaterPi service...")

while True:
    updateAdafruitIO()
    time.sleep(300)
