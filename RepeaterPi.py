print("RepeaterPi v.1 by KG5KEY")

raw_sensor_CH1_voltage = 2.3
raw_sensor_CH1_max_voltage = 16


def calc_voltage(sensor_readout, max_voltage):
    return (raw_sensor_CH1_voltage * raw_sensor_CH1_max_voltage) / 3.3

print(calc_voltage(raw_sensor_CH1_voltage, raw_sensor_CH1_max_voltage))

