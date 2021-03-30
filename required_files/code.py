import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import adafruit_bmp280

import board

import busio
import analogio

from time import sleep


# init i2c bus
i2c = busio.I2C(board.SCL, board.SDA)

# init bmp280 sensor
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

# init ads1115 sensor
ads = ADS.ADS1115(i2c, address=0x48)

# Assign voltages to vars
main = AnalogIn(ads, ADS.P0)
amp = AnalogIn(ads, ADS.P1)
fwd = AnalogIn(ads, ADS.P2)
rev = AnalogIn(ads, ADS.P3)

while True:
    temp_f = (bmp280.temperature * 1.8) + 32
    pressure = bmp280.pressure

    
    print(temp_f, pressure, main.voltage, amp.voltage, fwd.voltage, rev.voltage)

    sleep(1)
