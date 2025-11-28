# ROS2MQTTBridge

The bridge lives in the `ros2mqttbridge` folder. It connects ROS 2 and MQTT by subscribing to ROS topics (such as `/scan_safe`) and publishing messages to MQTT (and vice versa). The project enforces strict JSON validation for incoming MQTT messages.

## Development

This project has its own devcontainer so you can work on it in isolation. Inside the devcontainer you can:

- **Build** the bridge with:
  ```bash
  cargo build
  ```
- Run the tests with:
  ```bash
  cargo test
  ```

## Docker Compose Integration

The bridge also builds and runs as part of the overall Docker Compose configuration for the TurtleBot demo. When you open the devcontainer for the full demo, the bridge with run as the `rosmqttbridge` service.

- To watch the logs of the running bridge, use:
  ```bash
  docker compose logs -f rosmqttbridge
  ```
- To stop the bridge, use:
  ```bash
  docker compose down rosmqttbridge
  ```
- To start the bridge, use:
  ```bash
  docker compose up rosmqttbridge
  ```
- To restart the bridge in DEBUG logging mode use:
  ```bash
  docker compose run --env RUST_LOG=ros2mqttbridge::bridge=INFO rosmqttbridge```

The version of the bridge used in the overall demo is built via the dockerfile `docker/DockerfileDeploy`. You can rebuild the container using:
  ```bash
  docker compose build rosmqttbridge
  ```

