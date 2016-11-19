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

# average is 0, most recent 1, least recent 0
tempHistory = [0, 0, 0, 0, 0, 0]
voltage = [0, 0, 0, 0]  # primary 0, amp, 1, old primary 2, old amp 3
x = 0
startup = True

print("RepeaterPi 1.3v by KG5KEY on " + config['Basic']['repeater_name'])


# gets the data from the ADC and converts it to raw voltage
def get_voltage(channel):
    return (mcp.read_adc(channel) * 3.3) / float(1023)


# scales the raw voltage to the true value read by the voltage probes
def scale_voltage(channel):
    rv = (get_voltage(channel) * (61/11))
    if rv < 1:
        return 0
    else:
        return rv


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
    if startup:
        temp_average(calc_temp(7))
    else:
        temp = calc_temp(7)
        if abs(temp - temp_average[0]) > 7:
            temp_average[1] = temp_average[0]

    voltage[0] = (round(float(scale_voltage(0)) * float(main_cal), 2))
    voltage[1] = (round(float(scale_voltage(1)) * float(amplifier_cal), 2))


def temp_average(var):
    tempHistory[4] = tempHistory[5]
    tempHistory[3] = tempHistory[4]
    tempHistory[2] = tempHistory[3]
    tempHistory[1] = tempHistory[2]
    tempHistory[1] = var
    tempHistory[0] = (tempHistory[1] + tempHistory[2] + tempHistory[3] + tempHistory[4] + tempHistory[5]) / 5


print("\nStarting RepeaterPi service...")

# calibrating the temp sensor so we can throw out the bad eggs...
print("Calibrating temperature sensor...")
while x < 5:
    update_sensors()
    x += 1
    time.sleep(1.5)
print("Finished calibrating temperature sensor.")
update_adafruit_io()
x = 0
startup = False

while True:
    if abs(voltage[0] - voltage[2]) > .05 or abs(voltage[1] - voltage[3]) > .05 or x > 14:
        update_adafruit_io()
        x = 0
    else:
        x += 1
    time.sleep(60)
    update_sensors()
