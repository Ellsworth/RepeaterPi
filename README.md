# RepeaterPi
Program to monitor sensors inside of a repeater cabinet and alert trustees when a argument is tripped

Github: github.com/ellsworth/repeaterpi


----------

# Calculating sensor readouts

 - This project uses the "MCP3008" Analog to Digital Converter (ADC), with a max input voltage of 3.3v.
	 - This requires ALL sensors to have a maximum output voltage of 3.3v.
	 - we have 8 pins on the ADC to work with; CH0, CH1, CH2, CH3, CH4, CH5, CH6, CH7
		 - They are currently mapped as:
			 - CH0: TMP36 temperature sensor
			 - CH1: Voltage monitor; will be a 16v input, stepped down to 3.3v to the ADC can handle it safely
			 - CH2: Unplanned
			 - CH3: Unplanned
			 - CH4: Unplanned
			 - CH5: Unplanned
			 - CH6: Unplanned
			 - CH7: Unplanned
		 - Because these are not digital readouts, conversion from voltage is required.
			 - The formula for the voltage sensor is as follows: 
				 -  (CHANNEL_VOLTAGE/3.3v) = (VOLTAGE/MAX_VOLTAGE)
					 - CHANNEL_VOLTAGE: The voltage read by the ADC
					 - VOLTAGE: This is the voltage, the exact amount scaled up to the correct value.
					 - MAX_VOLTAGE: The maximum power that will be read. NOTE: YOU MUST STEP THIS DOWN 3.3V OR RISK DAMAGING THE MCP3008 ADC
					 - 
			 

