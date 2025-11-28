# ROS2MQTTBridge

The `ROS2MQTTBridge` is a Python script that bridges ROS 2 and MQTT. It subscribes to the `/scan` topic in ROS 2, publishes LiDAR messages to an MQTT topic, and subscribes to an MQTT topic to receive `Twist` messages, which it then publishes to the `/cmd_vel` topic in ROS 2.

## Requirements

- Python 3.7 or higher
- ROS 2 (Humble or later)
- `paho-mqtt` library
- `rclpy` library

## Installation

### ROS 2 Installation

Follow the [ROS 2 installation guide](https://docs.ros.org/en/foxy/Installation.html) for your operating system.

Don't forger to Source ROS2 repo
### Python Dependencies

Install the required Python libraries:

```sh
pip install paho-mqtt
pip install rclpy
```

### Run the mqtt broker

```sh
sudo service emqx start
```

### Sample Messages
#### ROS 2 Messages
##### LaserScan Message (Published from ROS 2 to MQTT):

Topic: '/scan'

Message Type: 'sensor_msgs/LaserScan'

Sample Message:
```sh
{
  "header": {
    "stamp": {
      "sec": 1622471125,
      "nanosec": 963492653
    },
    "frame_id": "laser_frame"
  },
  "angle_min": -1.5707963705062866,
  "angle_max": 1.5707963705062866,
  "angle_increment": 0.01745329238474369,
  "time_increment": 2.9880000507131295e-05,
  "scan_time": 0.10000000149011612,
  "range_min": 0.029999999329447746,
  "range_max": 3.5,
  "ranges": [
    1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9,
    2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9
  ],
  "intensities": [
    100.0, 100.1, 100.2, 100.3, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9,
    101.0, 101.1, 101.2, 101.3, 101.4, 101.5, 101.6, 101.7, 101.8, 101.9
  ]
}
```
##### Twist Message (Published from MQTT to ROS 2):

Topic: /cmd_vel

Message Type: geometry_msgs/Twist

Sample Message:
```json
{
  "linear": {
    "x": 1.0,
    "y": 0.0,
    "z": 0.0
  },
  "angular": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.5
  }
}
```
#### MQTT Messages
##### LaserScan Message (Published from ROS 2 to MQTT):

Topic: ros2/lidar

Message Type: JSON

Sample Message:
```json

{
  "angle_min": 0.0,
  "angle_max": 6.28000020980835,
  "angle_increment": 0.01749303564429283,
  "scan_time": 0.0,
  "range_min": 0.11999999731779099,
  "range_max": 20.0,
  "ranges": [
    1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9,
    2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9
  ],
  "intensities": [
    100.0, 100.1, 100.2, 100.3, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9,
    101.0, 101.1, 101.2, 101.3, 101.4, 101.5, 101.6, 101.7, 101.8, 101.9
  ]
}
```
##### Twist Message (Published from MQTT to ROS 2):

Topic: mqtt/twist

Message Type: JSON

Sample Message:

```json
{
  "linear": {
    "x": 1.0,
    "y": 0.0,
    "z": 0.0
  },
  "angular": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.5
  }
}
```

