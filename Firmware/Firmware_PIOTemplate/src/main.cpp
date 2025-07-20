#include <Arduino.h>
#include "firmware.h"

void setup()
{
  Serial.begin(115200);

  Serial.println("Firmware Version: " FIRMWARE_VERSION);
}

void loop()
{
  Serial.println("Hello, World!");
  delay(1000);
}