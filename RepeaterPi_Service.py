import RepeaterPi
import configparser
from time import sleep
from Adafruit_IO import Client

print("\nStarting RepeaterPi service...")

config = configparser.ConfigParser()
config.read('config.ini')

aio = Client(config['AdafruitIO']['AIO_Key'])

main_power = 13.8
amplifier_power = 13.8




def updateAdafruitIO():
    try:
        aio.send(config['Basic']['repeater_location'] + '-temp', int(round(RepeaterPi.calc_temp(7), 0))
        aio.send(config['Basic']['repeater_location'] + '-main-power', main_power)
        aio.send(config['Basic']['repeater_location'] + '-amplifier-power', amplifier_power)
        print("Updating AdafruitIO...")
        print(RepeaterPi.gen_Telemetry())
    except:
        print("no internets :C")


updateAdafruitIO()

while True:
    sleep(5)
    updateAdafruitIO()
