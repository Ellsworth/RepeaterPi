import configparser
import Adafruit_GPIO.SPI
import Adafruit_MCP3008
import time
from Adafruit_IO import Client

# Hardware SPI configuration:
mcp = Adafruit_MCP3008.MCP3008(spi=Adafruit_GPIO.SPI.SpiDev(0, 0))

# reading config, don't ask please.
config = configparser.ConfigParser()
config.read('/root/RepeaterPi/config.ini')
aio = Client(config['AdafruitIO']['AIO_Key'])
repeater_location = config['Basic']['repeater_location']
main_cal = config['Basic']['main_cal']
amplifier_cal = config['Basic']['amplifier_cal']

# average: 0, 1:1, 2:2, 3:3, 4:4, 5:5
tempHistory = [0, 0, 0, 0, 0, 0, 0]
voltage = [0, 0, 0, 0]  # primary 0, amp, 1, old primary 2, old amp 3
x = 0

print("RepeaterPi 1.2v by KG5KEY on " + config['Basic']['repeater_name'])


# gets the data from the ADC and converts it to raw voltage
def get_voltage(channel):
    return (mcp.read_adc(channel) * 3.3) / float(1023)


# scales the raw voltage to the true value read by the voltage probes
def scale_voltage(channel):
    return get_voltage(channel) * (61/11)


# calculates temp when given the channel from the ADC
def calc_temp(channel):
    return float(((((get_voltage(channel) * 1000) - 500) / 10) * 9 / 5 + 32))


def gen_telemetry():
    return ("-------------------------------------- \nTelemetry for " +
            str(time.asctime(time.localtime(time.time()))) +
            "\nPrimary: " + str(voltage[0]) +
            "v Amplifier: " + str(voltage[1]) +
            "v" + "\nTemperature: " + str(tempHistory[0]) +
            " Degrees Fahrenheit\nTemperature Average: " + str(tempHistory) + "\n")


def update_adafruit_io():
    aio.send(repeater_location + '-temp', tempHistory[0])
    aio.send(repeater_location + '-main-power', voltage[0])
    aio.send(repeater_location + '-amplifier-power', voltage[1])
    aio.send(repeater_location + '-temp-history', tempHistory)
    print(gen_telemetry())
    voltage[2] = voltage[0]
    voltage[3] = voltage[1]


def is_valid(current, previous):
    return abs(((current - previous) / previous) * 100) < 8


def update_sensors():
    tempHistory[1] = (round(calc_temp(7), 2))
    voltage[0] = (round(float(scale_voltage(0)) * float(main_cal), 2))
    voltage[1] = (round(float(scale_voltage(1)) * float(amplifier_cal), 2))
    kalman(tempHistory)


def kalman(var):
    # 0 and 1 is the new var, and 0 is the rounded amount from vars 2-6
    var[6] = var[5]
    var[5] = var[4]
    var[4] = var[3]
    var[3] = var[2]
    var[2] = var[1]
    var[0] = round((var[2] + var[3] + var[4] + var[5] + var[6]) / 5, 2)
    return var[0]  # return rounded values


print("\nStarting RepeaterPi service...")
print("Calibrating temperature sensor...")
while x < 5:
    update_sensors()
    x += 1
    time.sleep(1.5)
print("Finished calibrating temperature sensor.")
update_adafruit_io()
x = 0

while True:
    if abs(voltage[0] - voltage[2]) > .05 or abs(voltage[1] - voltage[3]) > .05 or x > 14:
        update_adafruit_io()
        x = 0
    else:
        x += 1
    time.sleep(60)
    update_sensors()
