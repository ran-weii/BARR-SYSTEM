#include <MatrixMath.h>

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <EEPROM.h>

/* This driver uses the Adafruit unified sensor library (Adafruit_Sensor),
   which provides a common 'type' for sensor data and some helper functions.

   To use this driver you will also need to download the Adafruit_Sensor
   library and include it in your libraries folder.

   You should also assign a unique ID to this sensor for use with
   the Adafruit Sensor API so that you can identify this particular
   sensor in any data logs, etc.  To assign a unique ID, simply
   provide an appropriate value in the constructor below (12345
   is used by default in this example).

   Connections
   ===========
   Connect SCL to analog 5
   Connect SDA to analog 4
   Connect VDD to 3-5V DC
   Connect GROUND to common ground

   History
   =======
   2015/MAR/03  - First release (KTOWN)
   2015/AUG/27  - Added calibration and system status helpers
   2015/NOV/13  - Added calibration save and restore



   SENSOR CONNECTION:
   =================

   - The sensor with the purple tape must be connected to mux channel 4. This is sensor two.
   - The tapeless sensor must be connected to mux channel 5. This is sensor one.
*/

/* Set the delay between fresh samples */
#define BNO055_SAMPLERATE_DELAY_MS (100)
#define TCAADDR 0x70
#define SENSOR_ONE_ID 55
#define SENSOR_TWO_ID 56

Adafruit_BNO055 bno = Adafruit_BNO055(55);
//Adafruit_BNO055 bnoTwo = Adafruit_BNO055(56);


/**************************************************************************/
/*
    Displays some basic information on this sensor from the unified
    sensor API sensor_t type (see Adafruit_Sensor for more information)
*/
/**************************************************************************/

//State Machine, which sensor are we talking to?
//IMPORTANT:
//Sensor One is connected to Mux output 4, Sensor Two is connected to Mux output 5

enum {X_SENSOR_CONNECTED, Y_SENSOR_CONNECTED, NONE} connectionState;
enum {X_SENSOR, Y_SENSOR} imuSensor;
bool fullyCalibrated = false;
 
void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}


void displaySensorDetails(bool sensorOne)
{
  sensor_t sensor;
  //sensorOne == true ? bno.getSensor(&sensor) : bnoTwo.getSensor(&sensor);
  bno.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print("Sensor:       "); Serial.println(sensor.name);
  Serial.print("Driver Ver:   "); Serial.println(sensor.version);
  Serial.print("Unique ID:    "); Serial.println(sensor.sensor_id);
  Serial.print("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" xxx");
  Serial.print("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" xxx");
  Serial.print("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" xxx");
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
}

/**************************************************************************/
/*
    Display some basic info about the sensor status
*/
/**************************************************************************/
void displaySensorStatus(bool sensorOne)
{
  /* Get the system status values (mostly for debugging purposes) */
  uint8_t system_status, self_test_results, system_error;
  system_status = self_test_results = system_error = 0;
  //sensorOne == true ? bno.getSystemStatus(&system_status, &self_test_results, &system_error) : bnoTwo.getSystemStatus(&system_status, &self_test_results, &system_error);
  bno.getSystemStatus(&system_status, &self_test_results, &system_error);

  /* Display the results in the Serial Monitor */
  Serial.println("");
  Serial.print("System Status: 0x");
  Serial.println(system_status, HEX);
  Serial.print("Self Test:     0x");
  Serial.println(self_test_results, HEX);
  Serial.print("System Error:  0x");
  Serial.println(system_error, HEX);
  Serial.println("");
  delay(500);
}

/**************************************************************************/
/*
    Display sensor calibration status
*/
/**************************************************************************/
void displayCalStatus(bool sensorOne)
{
  /* Get the four calibration values (0..3) */
  /* Any sensor data reporting 0 should be ignored, */
  /* 3 means 'fully calibrated" */
  uint8_t system, gyro, accel, mag;
  system = gyro = accel = mag = 0;
  bno.getCalibration(&system, &gyro, &accel, &mag);

  /* The data should be ignored until the system calibration is > 0 */
  Serial.print("\t");
  if (!system)
  {
    Serial.print("! ");
  }

  /* Display the individual values */
  Serial.print("Sys:");
  Serial.print(system, DEC);
  Serial.print(" G:");
  Serial.print(gyro, DEC);
  Serial.print(" A:");
  Serial.print(accel, DEC);
  Serial.print(" M:");
  Serial.print(mag, DEC);
}

/**************************************************************************/
/*
    Display the raw calibration offset and radius data
*/
/**************************************************************************/
void displaySensorOffsets(const adafruit_bno055_offsets_t &calibData)
{
  Serial.print("Accelerometer: ");
  Serial.print(calibData.accel_offset_x); Serial.print(" ");
  Serial.print(calibData.accel_offset_y); Serial.print(" ");
  Serial.print(calibData.accel_offset_z); Serial.print(" ");

  Serial.print("\nGyro: ");
  Serial.print(calibData.gyro_offset_x); Serial.print(" ");
  Serial.print(calibData.gyro_offset_y); Serial.print(" ");
  Serial.print(calibData.gyro_offset_z); Serial.print(" ");

  Serial.print("\nMag: ");
  Serial.print(calibData.mag_offset_x); Serial.print(" ");
  Serial.print(calibData.mag_offset_y); Serial.print(" ");
  Serial.print(calibData.mag_offset_z); Serial.print(" ");

  Serial.print("\nAccel Radius: ");
  Serial.print(calibData.accel_radius);

  Serial.print("\nMag Radius: ");
  Serial.print(calibData.mag_radius);
}

//Debug only
void clearEEPROM(){
  for (int i = 0 ; i < EEPROM.length() ; i++) {
    EEPROM.write(i, 0);
  }
}


/**************************************************************************/
/*
    Arduino setup function (automatically called at startup)
*/
/**************************************************************************/
void setup(void)
{
    //SENSOR ONE
    //=========
    
    Wire.begin();
    Serial.begin(38400);
    delay(1000);
    clearEEPROM();
    Serial.println("Orientation Sensor Test"); Serial.println("");
    
    tcaselect(5);
    delay(10);
    adafruit_bno055_offsets_t calibrationData;
    adafruit_bno055_offsets_t calibrationDataTwo;
    int sensorOneAddress = 0;
    int sensorTwoAddress = sizeof(long) + sizeof(calibrationData) + sizeof(long);
    
    /* Initialise the sensor */
    while (!bno.begin(Adafruit_BNO055::OPERATION_MODE_NDOF))
    {
        /* There was a problem detecting the BNO055 ... check your connections */
        Serial.println("Ooops, Sensor 5 not detected ... Check your wiring or I2C ADDR!");
        delay(2000);
    }

    //getSensorCalibrationData(SENSOR_ONE_ID, sensorOneAddress, calibrationData);

    tcaselect(4);
    delay(10);
    while (!bno.begin(Adafruit_BNO055::OPERATION_MODE_NDOF))
    {
        /* There was a problem detecting the BNO055 ... check your connections */
        Serial.println("Ooops, Sensor 4 not detected ... Check your wiring or I2C ADDR!");
        delay(2000);
    }
    //getSensorCalibrationData(SENSOR_TWO_ID, sensorTwoAddress, calibrationDataTwo);
    fullyCalibrated = true;
}

/**
 * 
 * return true if sensor is found and calibrated based on what is in memory
 */
 
bool getSensorCalibrationData(long correctID, 
                              int sensorAddress, 
                              const adafruit_bno055_offsets_t &calibrationData){
                                
    //clearEEPROM();
    long bnoID;
    bool foundCalib = false;
    long originalAddress = sensorAddress;
    EEPROM.get(sensorAddress, bnoID);                            

    if (bnoID != correctID)
    {
        Serial.println("\nNo Calibration Data for Sensor One exists in EEPROM");
        delay(500);
    }
    else
    {
        Serial.println("\nFound Calibration for Sensor One in EEPROM.");
        sensorAddress += sizeof(long);
        EEPROM.get(sensorAddress, calibrationData);

        displaySensorOffsets(calibrationData);

        Serial.println("\n\nRestoring Calibration data to the BNO055...");
        bno.setSensorOffsets(calibrationData);

        Serial.println("\n\nCalibration data loaded into BNO055");
        foundCalib = true;
    }

    delay(1000);

    /* Display some basic information on this sensor */
    displaySensorDetails(true);

    /* Optional: Display current status */
    displaySensorStatus(true);

   //Crystal must be configured AFTER loading calibration data into BNO055.
    bno.setExtCrystalUse(true);

    sensors_event_t event;
    bno.getEvent(&event);
    if (foundCalib){
        Serial.println("Move Sensor One slightly to calibrate magnetometers");
        uint8_t system, gyro, accel, mag;
        system = gyro = accel = mag = 0;
        bno.getCalibration(&system, &gyro, &accel, &mag);
        while (!bno.isFullyCalibrated() )
        {
            bno.getEvent(&event);
            displayCalStatus(true);
            Serial.println("");
            bno.getCalibration(&system, &gyro, &accel, &mag);
            delay(BNO055_SAMPLERATE_DELAY_MS);
        }
    }
    else
    {
        Serial.println("Please Calibrate Sensor One: ");
        while (!bno.isFullyCalibrated())
        {
            bno.getEvent(&event);

            Serial.print("X: ");
            Serial.print(event.acceleration.x, 4);
            Serial.print("\tY: ");
            Serial.print(event.acceleration.y, 4);
            Serial.print("\tZ: ");
            Serial.print(event.acceleration.z, 4);

            /* Optional: Display calibration status */
            displayCalStatus(true);

            /* New line for the next sample */
            Serial.println("");

            /* Wait the specified delay before requesting new data */
            delay(BNO055_SAMPLERATE_DELAY_MS);
        }
    }

    Serial.println("\nFully calibrated Sensor One!");
    Serial.println("--------------------------------");
    Serial.println("Calibration Results: ");
    adafruit_bno055_offsets_t newCalib;
    bno.getSensorOffsets(newCalib);
    displaySensorOffsets(newCalib);

    Serial.println("\n\nStoring calibration data to Sensor One EEPROM...");

    sensorAddress = originalAddress;

    EEPROM.put(sensorAddress, correctID);

    sensorAddress += sizeof(long);
    EEPROM.put(sensorAddress, newCalib);
    Serial.println("Data stored to EEPROM.");

    Serial.println("\n--------------------------------\n");
    delay(500);                              
    fullyCalibrated = true;
}


void loop() {
  
  if(fullyCalibrated == true) {
  
  // Get a new sensor event  
  tcaselect(4);
  sensors_event_t event; 
  bno.getEvent(&event);

  String sendBack = "";
  long t = millis();
  //Serial.println(currentTime);
  
  imu::Vector<3> ac1 = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  imu::Vector<3> gy1 = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> linacc1 = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
  imu::Vector<3> euler1 = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  imu::Quaternion quat1 = bno.getQuat();

    /* Get a new sensor event */
  tcaselect(5);  
  sensors_event_t eventTwo;
  bno.getEvent(&eventTwo);

  imu::Vector<3> ac2 = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  imu::Vector<3> gy2 = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> linacc2 = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
  imu::Vector<3> euler2 = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  imu::Quaternion quat2 = bno.getQuat();
  
  
  sendBack += (String(t));
  sendBack += (" ");
  sendBack += (String(ac1.x()));
  sendBack += (" ");
  sendBack += (String(ac1.y()));
  sendBack += (" ");
  sendBack += (String(ac1.z()));
  sendBack += (" ");
  sendBack += (String(linacc1.x()));
  sendBack += (" ");
  sendBack += (String(linacc1.y()));
  sendBack += (" ");
  sendBack += (String(linacc1.z()));
  sendBack += (" ");
  sendBack += (String(gy1.x()));
  sendBack += (" ");
  sendBack += (String(gy1.y()));
  sendBack += (" ");
  sendBack += (String(gy1.z()));
  sendBack += (" ");
  sendBack += (String(euler1.x()));
  sendBack += (" ");
  sendBack += (String(euler1.y()));
  sendBack += (" ");
  sendBack += (String(euler1.z()));
  sendBack += (" ");
  sendBack += (String(quat1.w()));
  sendBack += (" ");
  sendBack += (String(quat1.x()));
  sendBack += (" ");
  sendBack += (String(quat1.y()));
  sendBack += (" ");
  sendBack += (String(quat1.z()));

  //sensor two
  sendBack += (" ");
  sendBack += (String(ac2.x()));
  sendBack += (" ");
  sendBack += (String(ac2.y()));
  sendBack += (" ");
  sendBack += (String(ac2.z()));
  sendBack += (" ");
  sendBack += (String(linacc2.x()));
  sendBack += (" ");
  sendBack += (String(linacc2.y()));
  sendBack += (" ");
  sendBack += (String(linacc2.z()));
  sendBack += (" ");
  sendBack += (String(gy2.x()));
  sendBack += (" ");
  sendBack += (String(gy2.y()));
  sendBack += (" ");
  sendBack += (String(gy2.z()));
  sendBack += (" ");
  sendBack += (String(euler2.x()));
  sendBack += (" ");
  sendBack += (String(euler2.y()));
  sendBack += (" ");
  sendBack += (String(euler2.z()));
  sendBack += (" ");
  sendBack += (String(quat2.w()));
  sendBack += (" ");
  sendBack += (String(quat2.x()));
  sendBack += (" ");
  sendBack += (String(quat2.y()));
  sendBack += (" ");
  sendBack += (String(quat2.z()));
  Serial.println(sendBack);
  }

  if(fullyCalibrated == false) {
  // Get a new sensor event
    tcaselect(5);
    delay(20); 
    sensors_event_t event;
    bno.getEvent(&event);

    // Display the floating point data 
 imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);

  // Display the floating point data 
  Serial.print("X1: ");
  Serial.print(euler.x());
  Serial.print(" Y1: ");
  Serial.print(euler.y());
  Serial.print(" Z1: ");
  Serial.print(euler.z());
  Serial.print("\t\t");
  double value = euler.x()*euler.x() + euler.y()*euler.y() + euler.z()*euler.z();
  double magnitude = sqrt(value);
  Serial.println(String(magnitude));

    // Optional: Display calibration status 
    displayCalStatus(true);

    // Optional: Display sensor status (debug only) 
    //displaySensorStatus(true);

    // New line for the next sample 
    Serial.println("");

    tcaselect(4);
    delay(20); 
    bno.getEvent(&event);

    // Display the floating point data 
    euler = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);

  // Display the floating point data 
  Serial.print("X2: ");
  Serial.print(euler.x());
  Serial.print(" Y2: ");
  Serial.print(euler.y());
  Serial.print(" Z2: ");
  Serial.print(euler.z());
  Serial.print("\t\t");
  value = euler.x()*euler.x() + euler.y()*euler.y() + euler.z()*euler.z();
  magnitude = sqrt(value);
  Serial.println(String(magnitude));

    // Optional: Display calibration status 
    displayCalStatus(true);

    // Optional: Display sensor status (debug only) 
    //displaySensorStatus(true);

    // New line for the next sample 
    Serial.println("");

    // Wait the specified delay before requesting new data 
    delay(BNO055_SAMPLERATE_DELAY_MS);
    
  }
}
