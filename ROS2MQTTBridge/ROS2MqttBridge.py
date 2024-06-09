import paho.mqtt.client as mqtt
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import json

class ROS2MQTTBridge(Node):
    def __init__(self):
        super().__init__('ros2_mqtt_bridge')

        # ROS2 Subscriber to /scan topic
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            10
        )

        # ROS2 Publisher to /cmd_vel topic
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.get_logger().info('ROS2 Node started and ready to bridge messages.')

    def lidar_callback(self, msg):
        # Convert LaserScan message to JSON
        lidar_data = {
            'angle_min': msg.angle_min,
            'angle_max': msg.angle_max,
            'angle_increment': msg.angle_increment,
            'scan_time': msg.scan_time,
            'range_min': msg.range_min,
            'range_max': msg.range_max,
            'ranges': list(msg.ranges),
            # 'intensities': list(msg.intensities)
        }
        json_data = json.dumps(lidar_data)
        # Publish JSON data to MQTT
        mqtt_client.publish(mqtt_lidar_topic, json_data)
        self.get_logger().info('Published LiDAR data to MQTT.')

    def publish_twist(self, twist_msg):
        twist = Twist()
        twist.linear.x = twist_msg['linear']['x']
        twist.linear.y = twist_msg['linear']['y']
        twist.linear.z = twist_msg['linear']['z']
        twist.angular.x = twist_msg['angular']['x']
        twist.angular.y = twist_msg['angular']['y']
        twist.angular.z = twist_msg['angular']['z']
        self.publisher.publish(twist)
        self.get_logger().info('Published Twist message to ROS2.')

# MQTT Callback for incoming messages
def on_message(client, userdata, msg):
    try:
        twist_msg = json.loads(msg.payload.decode())
        bridge.publish_twist(twist_msg)
        print(f"Received Twist message from MQTT and published to ROS2: {twist_msg}")
    except json.JSONDecodeError:
        print("Failed to decode MQTT message as JSON")

# Initialize ROS2
rclpy.init()
bridge = ROS2MQTTBridge()

# Initialize MQTT client
mqtt_client = mqtt.Client()

# Set MQTT callback
mqtt_client.on_message = on_message

# MQTT Broker information
broker_address = "127.0.0.1"  # Example broker address
port = 1883

# MQTT Topics
mqtt_lidar_topic = "ros2/lidar"
mqtt_twist_topic = "mqtt/twist"

# Connect to MQTT broker
mqtt_client.connect(broker_address, port)

# Subscribe to the MQTT topic for Twist messages
mqtt_client.subscribe(mqtt_twist_topic)

# Start the MQTT client loop
mqtt_client.loop_start()

# Run the ROS2 node
try:
    while rclpy.ok():
        rclpy.spin_once(bridge, timeout_sec=0.1)
except KeyboardInterrupt:
    print("Shutting down bridge.")
finally:
    # Stop MQTT client loop and disconnect
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    # Shutdown ROS2
    bridge.destroy_node()
    rclpy.shutdown()