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
        aio.send(config['Basic']['repeater_location'] + '-temp', RepeaterPi.calc_temp(7))
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
    sleep(300)
    print('Updating AdafruitIO...')
    updateAdafruitIO()
    