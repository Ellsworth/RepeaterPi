# RepeaterPi [![BuildStatus](https://travis-ci.org/Ellsworth/RepeaterPi.svg?branch=master)](https://travis-ci.org/Ellsworth/RepeaterPi)
- Project to monitor sensors inside of a repeater cabinet and alert trustees
when a argument is tripped

- [Link to source code](https://github.com/Ellsworth/repeaterpi)

----------
## Software Arguments
- The following arguments may be added to modify the software's behavior.

  - `--copyright` will print out the legal notice for using this software.
  - `--test` will run the software in a 'dry run' mode for the purpose of continuous integration.
----------

## The sensor board
- The sensor board is a small Arduino based device that has two voltage probes and
a TMP36 analog temperature sensor. The diagram can be found [here](https://github.com/Ellsworth/RepeaterPi/blob/master/required_files/MainBoard.png)
- All three of the sensors are analog therefor requiring that they be connected
to the Arduino via it's analog pins.
  - It's up to the user to deicide how they want their sensor board to be hooked
  up.
  - The only requirement is that the TMP36 be connected to A1, the main voltage
  probe be connected to A6, and the amplifier probe to A7.
  - However it is easy to change this to your discretion. Just edit the first
  three lines in the Arduino sketch, named [RepeaterPi.ino](https://github.com/Ellsworth/RepeaterPi/blob/master/required_files/RepeaterPi/RepeaterPi.ino)

----------
## Calculating Sensor Readout
- Because these are not digital readouts, conversion from voltage is required.
  - The formula for the voltage probe:
    - (V * (61/11))
  - The formula for the TMP36 temperature probe:
    - ((mV- 500) / 10)
