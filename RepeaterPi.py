import configparser
#import spidev
import time
import os

config = configparser.ConfigParser()
config.read('config.ini')

print("RepeaterPi v.1 by KG5KEY on " + config['Basic']['RepeaterName'])

# nominal voltage should be 13.8v aka 2.502v as read directly by the ADC...
raw_sensor_CH0_voltage = 2.502
raw_sensor_CH1_voltage = 3.3


def calc_voltage(sensor_readout):
    return round((sensor_readout * 16) / 2.9, 2)


print("--------------------------------------")
print("Telemetry for " + str(time.asctime(time.localtime(time.time())))) # comrade
print("Primary: " + str(calc_voltage(raw_sensor_CH0_voltage)) +
      "v Amplifier: " + str(calc_voltage(raw_sensor_CH1_voltage)) + "v")
print("--------------------------------------")


