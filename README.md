# RepeaterPi
- Program to monitor sensors inside of a repeater cabinet and alert trustees when a argument is tripped

- [Link to source code](https://github.com/ellsworth/repeaterpi)

- Tom, N5TW asked me to look into attaching sensors (Primarily voltage and temp) to the existing Raspberry Pi's inside of the N5TT 146.640 and 145.450 repeaters.

- Using the existing Raspberry Pi reduces complexity, cost, and redundant hardware. The Pi also allows us to add features via updates to the software, requiring no modification to the sensor boards. Making it almost completely software defined.

----------

# Sensors 

 - At heart this project uses the "MCP3008" Analog to Digital Converter (ADC)
 - Using the MCP3008 allows fewer GPIO pins needed for multiple sensors. We can also use it to measure voltages of equipment inside the repeater cabinet
 - NOTE: The MCP3008 ADC has a max input voltage of 3.3v.
	 - This requires ALL sensors to have a maximum output voltage of 3.3v.
	 - we have 8 pins on the ADC to work with; CH0, CH1, CH2, CH3, CH4, CH5, CH6, CH7
		 - They are currently mapped as:
			 - CH0: TMP36 temperature sensor
			 - CH1: Voltage monitor; will be a maximum 16v input, stepped down to 3.3v to so the ADC can handle it safely
			 - CH2: Unused
			 - CH3: Unused
			 - CH4: Unused
			 - CH5: Unused
			 - CH6: Unused
			 - CH7: Unused
	 - Notice that we have extra channels available, so we could have up to 8 analog sensors, without using any extra GPIO pins on the Pi


----------
# Calculating Sensor Readout
- Because these are not digital readouts, conversion from voltage is required.
	 - The formula for the voltage sensor is as follows: 
		 - (CHANNEL_VOLTAGE/3.3v) = (VOLTAGE/MAX_VOLTAGE)
			 - CHANNEL_VOLTAGE: The voltage read by the ADC
			 - VOLTAGE: This is the voltage, the exact amount scaled up to the correct value.
			 - MAX_VOLTAGE: The maximum power that will be read. YOU MUST STEP THIS DOWN TO 3.3V OR RISK DAMAGING THE MCP3008 ADC
