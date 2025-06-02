# Isotope Detection Process Protocol

> Isotope Detection Process does depend on the sensor process to get both sensordata and settings from Sensor Process (
> device/sensor).
> Sensor settings is required to retrieve the calibration constants (`CALIB_ENERGY_CONSTANTS`) and sensordata is
> required for spectrum data.

### Heartbeat / Status

> Purpose
>
> Periodically send a heartbeat to all other subscribed processes to indicate that the process is still running.
>

- Topic: device/isotopedetection
- Packet Data
  ```json
  {
    "type": "status",
    "data": {},
    "timestamp": "2024-04-15 14:01:50"
  }
  ```

### Detection Settings (Get)

> Purpose
>
> Allow other processes to query and retrieve the settings of the sensor script.

#### Query

- Topic: device/isotopedetection/query
- Packet Data
  ```json
  {
    "type": "settings"
  }
  ```

#### Response

- Topic: device/isotopedetection
- Packet Data
  ```json
  {
    "type": "settings",
    "data": {
      "MODE": 0,
      "INTERVAL": 1,
      "ENERGY_MIN": 250,
      "ENERGY_MAX": 2700,
      "SMOOTH_WINDOW": 51,
      "TOLERANCE": 10,
      "HEIGHT": 1,
      "PROMINENCE": 1,
      "WIDTH": 20,
      "REL_HEIGHT": 0.5,
      "MAX_ISOTOPE_MATCH": 20,
      "MIN_ACQ_TIME": 8,
      "ISOTOPES": {
        "Co-60": {"peaks": [{"energy": 1173.0, "width": 58.7, "prominence": 1, "height": 1},
                            {"energy": 1332.0, "width": 66.6, "prominence": 1, "height": 1}],
                  "enabled": true}
      }
    },
  "timestamp": "2024-01-30 19:26:45"
  }
  ```

### Detection Settings (Set)

> The following parameters can be changed using this query. The whole settings will be returned.

#### Query

- Topic: device/isotopedetection/edit
- Packet Data
  ```json
  {
  "type": "edit",
  "data": {
    "ENERGY_MIN": 250
  },
  "timestamp": "2024-01-30 19:26:45"
  }
  ```

#### Response

- Topic: device/isotopedetection
- Packet Data
  ```json
  {
    "type": "settings",
    "data": {
  
    },
    "timestamp": "2024-01-30 19:26:45"
  }
  ```

### Inference Results

- Topic: device/isotopedetection
- Packet Data
  ```json
  {
    "type": "inferences",
    "data": {
      "MATCHED_ISOTOPES": {
        "Cs-137": {
          "energy": [662.0],
          "channel": [2000],
          "height": [2.0]},
        "Co-60": {
          "energy": [1173.0, 1332.0],
          "channel": [3550, 4040],
          "height": [1.6, 1.8]}
      },
      "PEAKS": {
        "energy": [662.0, 1173.0, 1332.0],
        "channel": [2000, 3550, 4040],
        "height": [2.0, 1.6, 1.8],
        "width": [32.6, 58.7, 66.6],
        "prominence": [2.1, 1.0, 1.0]
      }
    },
    "timestamp": "2024-01-30 19:26:45"
  }
  ```