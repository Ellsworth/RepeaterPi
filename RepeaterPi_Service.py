import RepeaterPi
import configparser
from time import sleep
from Adafruit_IO import Client

print("\nStarting RepeaterPi service...")

config = configparser.ConfigParser()
config.read('config.ini')

aio = Client(config['AdafruitIO']['AIO_Key'])

temp = 73
main_power = 13.8
amplifier_power = 13.8

# purely testing
new_temp = 73
new_main_power = 13.8
new_amplifier_power = 0


def updateAdafruitIO():
    try:
        aio.send(config['Basic']['repeater_location'] + '-temp', temp)
        aio.send(config['Basic']['repeater_location'] + '-main-power', main_power)
        aio.send(config['Basic']['repeater_location'] + '-amplifier-power', amplifier_power)
    except:
        print("no internets :C")

# while True:
#    print(RepeaterPi.gen_Telemetry())
#    updateAdafruitIO()
#    sleep(300)

updateAdafruitIO()

while True:
    sleep(5)
    if new_temp != temp or new_main_power != main_power or new_amplifier_power != amplifier_power:
        print("Data out of date, running updateAdafruitIO() to fix that...")
        temp = new_temp
        main_power = new_main_power
        amplifier_power = new_amplifier_power
        updateAdafruitIO()
    