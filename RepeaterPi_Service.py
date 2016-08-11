import RepeaterPi
import configparser
from time import sleep
from Adafruit_IO import Client

print("\nStarting RepeaterPi service...")

config = configparser.ConfigParser()
config.read('config.ini')

aio = Client(config['AdafruitIO']['AIO_Key'])



def updateAdafruitIO():
#    try:
    aio.send(config['Basic']['repeater_location'] + '-temp', RepeaterPi.calc_temp(7))
    aio.send(config['Basic']['repeater_location'] + '-main-power', RepeaterPi.scale_voltage(0))
    aio.send(config['Basic']['repeater_location'] + '-amplifier-power', RepeaterPi.scale_voltage(1))
    print("Updating AdafruitIO...")
    print(RepeaterPi.gen_Telemetry())
#    except:
#        print("no internets :C")


while True:
    updateAdafruitIO()
    sleep(300)

