import configparser
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import time

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

config = configparser.ConfigParser()
config.read('config.ini')

print("RepeaterPi v.1 by KG5KEY on " + config['Basic']['repeater_name'])


def get_voltage(channel):
  return (mcp.read_adc(channel) * 3.25) / 1023

# nominal voltage should be 13.8v aka 2.502v as read directly by the ADC...
def scale_voltage(channel):
    return round(((get_voltage(channel) * 16) / 2.9), 2)

def calc_temp(channel):
    return round(((((get_voltage(7) * 1000) - 500) / 10)) * 9 / 5 + 32, 1)
 
def gen_Telemetry():
    return ("-------------------------------------- \nTelemetry for " +
          str(time.asctime(time.localtime(time.time()))) +
          "\nPrimary: " + str(scale_voltage()) +
          "v Amplifier: " + str(0) +
          "v" + "\nTemperature: " + str(calc_temp(7)) + " Degrees Fahrenheit" + "\n--------------------------------------")

