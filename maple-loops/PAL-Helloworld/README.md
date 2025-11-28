# PAL-Helloworld

# Project Docker Compose Setup

This project uses Docker Compose to orchestrate multiple services, including an MQTT broker, Redis, and custom application components.

## Services

### emqx-enterprise
Communication Backbone 

### redis
Provides the KnowledgeBase 

### maple-k
This service runs the MAPLE-K loop to enable self-adaptive application.
Check the ManagingSystem repo to check how it is developed. 

### rosmqttbridge(Commented Out)

This service converts the ROS messages to MQTT and also MQTT messages to ROS.
This service is commented out because you need to launch you specific ros launch files in the Docker file. 
Just got to the folder 'bridge' and change the ROS2MQTTBridge.py code based on the ros2 interfaces and libraries that you developed. This is how they did it with turtlebot4: https://github.com/INTO-CPS-Association/robosapiens-adaptive-platform-turtlebot/blob/main/docker/Dockerfile.rosmqttbridge


### Simulator (Commented Out)
- A simulator service configuration is provided but commented out. 
You can run the simulation code from ManagedSystem repo to check weather the MAPLE-K is working.

##  testing the Maple-k loop with simulator: 
Before running the simulator, ensure that all services are up and running by executing the following command:

```bash
docker-compose up
```
then run the following command:
```bash
python ManagedSystem/Turtlebotsim.py
```

This will start the Turtlebot simulator and allow you to test the MAPLE-K loop with the simulated environment.(press the lidar occlusion botton and see the changes in navigation plan)

##  testing the Maple-k loop with your robot(simulation or real robot): 
First ensure that all services are up and running by executing the following command:

```bash
docker-compose up
```
start the bridge to send messages to MAPLE-K

```bash
python Bridge/ROS2MqttBridge.py
```
Make sure you are publishing the lidar data to "/Scan" topic in Mqtt and subscribe to spin configs in ""/spin_config" topic through the bridge. 
The current Bridge is a template and may not work with your code because I am not including your libraries. If you want to check how they did in Turtlebot4 you can check this: https://github.com/INTO-CPS-Association/robosapiens-adaptive-platform-turtlebot/tree/main/turtlebotrossim