import configparser
# mport spidev
import time
# import os

config = configparser.ConfigParser()
config.read('config.ini')

print("RepeaterPi v.1 by KG5KEY on " + config['Basic']['repeater_name'])

# nominal voltage should be 13.8v aka 2.502v as read directly by the ADC...
raw_sensor_CH0_voltage = 2.502
raw_sensor_CH1_voltage = 2.9
temp = 95


def calc_voltage(sensor_readout):
    return round((sensor_readout * 16) / 2.9, 2)

def calc_temp(data):
    return (data * (9/5)) + 32  # converts C to F cause MURICA

def gen_Telemetry():
    return ("-------------------------------------- \nTelemetry for " +
          str(time.asctime(time.localtime(time.time()))) +
          "\nPrimary: " + str(calc_voltage(raw_sensor_CH0_voltage)) +
          "v Amplifier: " + str(calc_voltage(raw_sensor_CH1_voltage)) +
          "v" + "\nTemperature: " + str(temp)) + " Degrees Fahrenheit" + "\n--------------------------------------"


print(gen_Telemetry())
