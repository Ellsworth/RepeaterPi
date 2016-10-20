# RepeaterPi
- Project to monitor sensors inside of a repeater cabinet and alert trustees when a argument is tripped

- [Link to source code](https://github.com/ellsworth/repeaterpi)

- Software and with a matching board to remotely measure voltage and temperature and upload the readings to io.adafruit.com

- Using the existing Raspberry Pi reduces complexity, cost, and redundant hardware. The Pi also allows us to add features via updates to the software.

----------


# Sensors 

 - At heart this project uses the "MCP3008" Analog to Digital Converter (ADC)
 - Using the MCP3008 allows fewer GPIO pins needed for multiple sensors. We can also use it to measure voltages of equipment inside the repeater cabinet
 - NOTE: The MCP3008 ADC has a max input voltage of 3.3v.
	 - This requires ALL sensors to have a maximum output voltage of 3.3v.
	 - we have 8 pins on the ADC to work with; CH0, CH1, CH2, CH3, CH4, CH5, CH6, CH7
		 - They are currently mapped as:
			 - CH0: Voltage Probe 1, max power is 16v
			 - CH1: Voltage Probe 2, max power is 16v
			 - CH2: Unused
			 - CH3: Unused
			 - CH4: Unused
			 - CH5: Unused
			 - CH6: Unused
			 - CH7: TMP36 Temp Sensor
	 - Notice that we have extra channels available, so we could have up to 8 analog sensors, without using any extra GPIO pins on the Pi


----------
# Calculating Sensor Readout
- Because these are not digital readouts, conversion from voltage is required.
	 - The formula for the voltage sensor is as follows:
		 - 'get_voltage(channel) * (61/11)'
