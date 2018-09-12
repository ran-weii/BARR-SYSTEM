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
float tnow, a1X, a2X, a3X, a1Y, a2Y, a3Y, a1Z, a2Z, a3Z, g1X, g2X, g3X, g1Y, g2Y, g3Y, g1Z, g2Z, g3Z;

void setup() {
  while(!Serial);
  Serial.begin(115200);

#ifdef _ESP32_HAL_I2C_H_ // For ESP32
  Wire.begin(SDA_PIN, SCL_PIN); // SDA, SCL
#else
  Wire.begin();
#endif
  tcaselect(2);
  tcaselect(4);
  tcaselect(6);
  mySensor.setWire(&Wire);
  mySensor.beginAccel();
  mySensor.beginGyro();

}



////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



void loop() {
  
  tcaselect(2); //input pin number 
  mySensor.accelUpdate();
  a1X = mySensor.accelX();
  a1Y = mySensor.accelY();
  a1Z = mySensor.accelZ();
  
  mySensor.gyroUpdate();
  g1X = mySensor.gyroX();
  g1Y = mySensor.gyroY();
  g1Z = mySensor.gyroZ();
  
  tcaselect(4); //input pin number 
  mySensor.accelUpdate();
  a2X = mySensor.accelX();
  a2Y = mySensor.accelY();
  a2Z = mySensor.accelZ();
  
  mySensor.gyroUpdate();
  g2X = mySensor.gyroX();
  g2Y = mySensor.gyroY();
  g2Z = mySensor.gyroZ();

  
  
  // tcaselect(4);
  // mySensor.accelUpdate();
  // a2X = mySensor.accelX();

  // tcaselect(6);
  // mySensor.accelUpdate();
  // a3X = mySensor.accelX();

  // tcaselect(2);
  // mySensor.accelUpdate();
  // a1Y = mySensor.accelY();
  
  // tcaselect(4);
  // mySensor.accelUpdate();
  // a2Y = mySensor.accelY();

  // tcaselect(6);
  // mySensor.accelUpdate();
  // a3Y = mySensor.accelY();


  // tcaselect(2);
  // mySensor.accelUpdate();
  // a1Z = mySensor.accelZ();
  
  // tcaselect(4);
  // mySensor.accelUpdate();
  // a2Z = mySensor.accelZ();

  // tcaselect(6);
  // mySensor.accelUpdate();
  // a3Z = mySensor.accelZ();










  // tcaselect(2);
  // mySensor.gyroUpdate();
  // g1X = mySensor.gyroX();
  
  // tcaselect(4);
  // mySensor.gyroUpdate();
  // g2X = mySensor.gyroX();

  // tcaselect(6);
  // mySensor.gyroUpdate();
  // g3X = mySensor.gyroX();

  // tcaselect(2);
  // mySensor.gyroUpdate();
  // g1Y = mySensor.gyroY();
  
  // tcaselect(4);
  // mySensor.gyroUpdate();
  // g2Y = mySensor.gyroY();

  // tcaselect(6);
  // mySensor.gyroUpdate();
  // g3Y = mySensor.gyroY();


  // tcaselect(2);
  // mySensor.gyroUpdate();
  // g1Z = mySensor.gyroZ();
  
  // tcaselect(4);
  // mySensor.gyroUpdate();
  // g2Z = mySensor.gyroZ();

  // tcaselect(6);
  // mySensor.gyroUpdate();
  // g3Z = mySensor.gyroZ();


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



  Serial.println(String(1) + "," + String(a1X) + "," + String(a1Y) + "," + String(a1Z) + "," + 
  String(g1X) + "," + String(g1Y) + "," + String(g1Z));
  Serial.println(String(2) + "," + String(a2X) + "," + String(a2Y) + "," + String(a2Z) + "," + 
  String(g2X) + "," + String(g2Y) + "," + String(g2Z));




 // Serial.println("at " + String(millis()) + "ms");
 // Serial.println(""); // Add an empty line

 
  delay(5);
}
