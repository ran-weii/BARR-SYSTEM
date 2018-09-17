#include "Wire.h"
extern "C" { 
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}
 
#define TCAADDR 0x70
 
void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



#include <MPU9250_asukiaaa.h>
#ifdef _ESP32_HAL_I2C_H_
#define SDA_PIN 19
#define SCL_PIN 18
#endif

MPU9250 mySensor;

uint8_t sensorId;
float tnow, a1X, a1Y, a1Z, g1X, g1Y, g1Z, m1X, m1Y, m1Z, a2X, a2Y, a2Z, g2X, g2Y, g2Z, m2X, m2Y, m2Z;

void setup() {
  while(!Serial);
  Serial.begin(115200);

#ifdef _ESP32_HAL_I2C_H_ // For ESP32
  Wire.begin(SDA_PIN, SCL_PIN); // SDA, SCL
#else
  Wire.begin();
#endif
  tcaselect(1);
  tcaselect(2);
  tcaselect(6);
  mySensor.setWire(&Wire);
  mySensor.beginAccel();
  mySensor.beginGyro();

}



////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



void loop() {
  
  tcaselect(1); //input pin number 
  mySensor.accelUpdate();
  a1X = mySensor.accelX();
  a1Y = mySensor.accelY();
  a1Z = mySensor.accelZ();
  
  mySensor.gyroUpdate();
  g1X = mySensor.gyroX();
  g1Y = mySensor.gyroY();
  g1Z = mySensor.gyroZ();
  
  mySensor.magUpdate();
  m1X = mySensor.magX();
  m1Y = mySensor.magY();
  m1Z = mySensor.magZ();
  
  tcaselect(2); //input pin number 
  mySensor.accelUpdate();
  a2X = mySensor.accelX();
  a2Y = mySensor.accelY();
  a2Z = mySensor.accelZ();
  
  mySensor.gyroUpdate();
  g2X = mySensor.gyroX();
  g2Y = mySensor.gyroY();
  g2Z = mySensor.gyroZ();

  mySensor.magUpdate();
  m2X = mySensor.magX();
  m2Y = mySensor.magY();
  m2Z = mySensor.magZ();  



////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



  Serial.println(String("x") + "," + String("a:") + String(a1X) + "," + String("b:") + String(a1Y) + "," + String("c:") + String(a1Z) + "," + 
  String("d:") + String(g1X) + "," + String("e:") + String(g1Y) + "," + String("f:") + String(g1Z) + "," + 
  String("g:") + String(m1X) + "," + String("h:") + String(m1Y) + "," + String("i:") + String(m1Z)+ "," + 
  String("y") + "," + String("a:") + String(a2X) + "," + String("b:") + String(a2Y) + "," + String("c:") + String(a2Z) + "," + 
  String("d:") + String(g2X) + "," + String("e:") + String(g2Y) + "," + String("f:") + String(g2Z) + "," + 
  String("g:") + String(m2X) + "," + String("h:") + String(m2Y) + "," + String("i:") + String(m2Z)); 

 
  delay(5);
}
