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

# nominal voltage should be 13.8v aka 2.502v as read directly by the ADC...


def get_voltage(channel):
    return (mcp.read_adc(channel) * 3.3) / 1023

def scale_voltage(sensor_readout):
    return round((sensor_readout * 16) / 2.9, 2)

def calc_temp(channel):
    #return ((mcp.read_adc(channel) / 1023) * 150) * (9/5) + 32
    return round(((get_voltage(7) * 1000) - 500 / 10))
 
    #return (get_voltage(channel) * (9/5)) + 32  # converts C to F cause MURICA

def gen_Telemetry():
    return ("-------------------------------------- \nTelemetry for " +
          str(time.asctime(time.localtime(time.time()))) +
          "\nPrimary: " + str("0") +
          "v Amplifier: " + str(0) +
          "v" + "\nTemperature: " + str(calc_temp(7))) + " Degrees Fahrenheit" + "\n--------------------------------------"




## Testing  Raspberry Spy code
def ConvertVolts(data):
  volts = (data * 3.3) / float(1023)
  return volts
 
# Function to calculate temperature from
# TMP36 data, rounded to specified
# number of decimal places.
def ConvertTemp(data,places):
 
  # ADC Value
  # (approx)  Temp  Volts
  #    0      -50    0.00
  #   78      -25    0.25
  #  155        0    0.50
  #  233       25    0.75
  #  310       50    1.00
  #  465      100    1.50
  #  775      200    2.50
  # 1023      280    3.30
 
  temp = ((data * 330)/float(1023))-50
  return temp
  
 