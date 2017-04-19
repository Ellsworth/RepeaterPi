int tempPin = 1;
int mainPin = 6;
int ampPin = 7;
String output;

void setup()
{
  Serial.begin(9600);  //Start the serial connection to the Pi
  while (!Serial) {
  ; // wait for serial port to connect. Needed for native USB port only
}

}

void loop()
{
  // prepare to cringe
  Serial.print(analogRead(tempPin));
  Serial.print(",");
  Serial.print(analogRead(mainPin));
  Serial.print(",");
  Serial.println(analogRead(ampPin));
  delay(6000);
}
