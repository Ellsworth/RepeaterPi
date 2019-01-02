int tempPin = 1;
int fwdPin = 4;
int revPin = 5;
int mainPin = 6;
int ampPin = 7;

long readVcc() {
  long result;
  // Read 1.1V reference against AVcc
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(2); // Wait for Vref to settle
  ADCSRA |= _BV(ADSC); // Convert
  while (bit_is_set(ADCSRA,ADSC));
  result = ADCL;
  result |= ADCH<<8;
  result = 1125300L / result; // Back-calculate AVcc in mV
  return result;
}

void setup()
{
  Serial.begin(9600);  //Start the serial connection to the Pi
  while (!Serial) {
  ; // wait for serial port to connect.
}

}

void loop()
{
  // prepare to cringe
  Serial.print(analogRead(tempPin));
  Serial.print(",");
  Serial.print(analogRead(mainPin));
  Serial.print(",");
  Serial.print(analogRead(ampPin));
  Serial.print(",");
  Serial.print(analogRead(fwdPin));
  Serial.print(",");
  Serial.print(analogRead(revPin));
  Serial.print(",");
  Serial.println(readVcc(), DEC );
  delay(15100);
}
