// Para el arduino
#include <MQ135.h>

const int APIN = 0;
MQ135 gasSensor = MQ135(APIN);

void setup() {
  // Lo usamos para comunicarnos
  // con el ESP8266
  Serial.begin(9600);
}

void loop() {
  float sensor1 = gasSensor.getRZero();
  Serial.println(String(sensor1));
  delay(10000);
}
