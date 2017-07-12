import serialtest

print("RepeaterPi Calibration Tool v1.0\nLoading serialtest.py...\n")

print("Current Main Calibration Value: " + str(serialtest.main_cal))
print("Current Amp Calibration Value:  " + str(serialtest.amplifier_cal))
print("Hit the control and C key to cancel...\n")

main_val = input("Please enter the current main voltage: ")
amp_val = input("Please enter the current amp voltage: ")

new_main_cal = float(main_val) / float(serialtest.scaleVoltage(1))
new_amp_cal = float(amp_val) / float(serialtest.scaleVoltage(2))

serialtest.config['Basic']['main_cal'] = str(new_main_cal)
serialtest.config['Basic']['amplifier_cal'] = str(new_amp_cal)

with open('config.ini', 'w') as configfile:
    serialtest.config.write(configfile)
