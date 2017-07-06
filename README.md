# RepeaterPi [![Build Status](https://travis-ci.org/Ellsworth/RepeaterPi.svg?branch=master)](https://travis-ci.org/Ellsworth/RepeaterPi)
- Project to monitor sensors inside of a repeater cabinet and alert trustees
when a argument is tripped

- [Link to source code](https://github.com/Ellsworth/repeaterpi)

----------

## The sensor board
- The sensor board is a small Arduino based device that has two voltage probes and
- All three of the sensors are analog therefor requiring that they be connected
to the Arduino via it's analog pins.
  - It's up to the user to deicide how they want their sensor board to be hooked
  up.
  - The only requirement is that the TMP36 be connected to A1, the main voltage
  probe be connected to A6, and the amplifier probe to A7.
  - However it is easy to change this to your discretion. Just edit the first

----------
## Calculating Sensor Readout
- Because these are not digital readouts, conversion from voltage is required.
  - The formula for the voltage probe:
    - (V * (61/11))
  - The formula for the TMP36 temperature probe:
    - ((mV- 500) / 10)
