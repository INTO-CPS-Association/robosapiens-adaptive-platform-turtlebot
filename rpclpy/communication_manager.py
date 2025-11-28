import threading
import redis
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# import rclpy  # Commented out for now
# from rclpy.node import Node  # Commented out for now

class CommunicationManager:
    def __init__(self, config, knowledge, logger):
        self.config = config
        self.knowledge = knowledge
        self.logger = logger
        self.mqtt_client = mqtt.Client(CallbackAPIVersion.VERSION2)
        self.redis_client = None
        # self.ros2_node = None  # Commented out for now
        self.redis_thread = None  # Redis thread for listening
        self.event_callbacks = {}  # Store callbacks for MQTT, Redis
        self.mqtt_subscribe_topics = []
        self.mqtt_publish_topics = []
        # MQTT and Redis topics/keys from config

        # Get the subscribe topics from the config file
        if 'eventIn' in config and 'properties' in config['eventIn']:
            properties = config['eventIn']['properties']
            for item in properties:
                if 'property' in item and 'name' in item['property']:
                    self.mqtt_subscribe_topics.append(item['property']['name'])

        # Get publish topic list from the config file 
        if 'eventOut' in config and 'properties' in config['eventIn']:
            properties = config['eventOut']['properties']
            for item in properties:
                if 'property' in item and 'name' in item['property']:
                    self.mqtt_publish_topics.append(item['property']['name'])

        self.redis_keys = self.config.get("redis_keys", [])

        # self.ros2_subscribe_topics = self.config.get("ros2_subscribe_topics", [])  # Commented out for now
        # self.ros2_publish_topics = self.config.get("ros2_publish_topics", [])  # Commented out for now
        


    ### Event Registration and Handling ###
    def start(self):
                # Setup MQTT
        self.initialize_mqtt()

        # Setup Redis
        if self.config.get('redis_host'):
            self.initialize_redis()

        # Setup ROS2 (if needed) -- Commented out for now
        # if self.config.get("use_ros2", False):
        #     rclpy.init(args=None)
        #     self.ros2_node = Node('Event_Handler_node')
        #     self.initialize_ros2()

    def subscribe(self, event_key, callback):
        """
        Register a callback for a given event key (MQTT topic, Redis key).
        :param event_key: The event key (MQTT topic, Redis key, etc.)
        :param callback: The function to call when the event is triggered
        """
        if event_key not in self.event_callbacks:
            self.event_callbacks[event_key] = []
        self.event_callbacks[event_key].append(callback)
        self.logger.info(f"Registered callback for event: {event_key}")
        
    def send(self, topic, message = "TRUE"):
        """Publish an event to an MQTT topic."""
        if topic in self.mqtt_publish_topics:
            self.mqtt_client.publish(topic, message)
            self.logger.info(f"Published to MQTT topic {topic}: {message}")
        else:
            self.logger.warning(f"Cannot publish to {topic}: Not configured in yaml")

    def trigger_callbacks(self, event_key, data):
        """
        Trigger all callbacks associated with an event.
        :param event_key: The event key (MQTT topic, Redis key, etc.)
        :param data: The data to pass to the callbacks
        """
        if event_key in self.event_callbacks:
            for callback in self.event_callbacks[event_key]:
                callback(data)

    ### MQTT Methods ###

    def initialize_mqtt(self):
        """Initialize MQTT subscriptions based on the config file."""
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.connect(self.config['mqtt_broker'], self.config['mqtt_port'])
        
        for topic in self.mqtt_subscribe_topics:
            self.mqtt_client.subscribe(topic)
            self.logger.info(f"Subscribed to MQTT topic: {topic}")
        
        self.mqtt_client.loop_start()

    def on_mqtt_message(self, client, userdata, message):
        """Handle incoming MQTT messages and trigger any registered callbacks."""
        payload = message.payload.decode("utf-8")
        topic = message.topic
        self.logger.info(f"Received MQTT message: {payload} on topic: {topic}")
        
        # Trigger any registered callbacks for this topic
        self.trigger_callbacks(topic, payload)

    def publish_mqtt(self, topic, message):
        """Publish a message to an MQTT topic."""
        if topic in self.mqtt_publish_topics:
            self.mqtt_client.publish(topic, message)
            self.logger.info(f"Published to MQTT topic {topic}: {message}")
        else:
            self.logger.warning(f"Cannot publish to {topic}: Not configured in yaml")

    ### Redis Methods ###

    def initialize_redis(self):
        """Initialize Redis and subscribe to keys."""
        self.redis_client = redis.StrictRedis(host=self.config['redis_host'], port=self.config['redis_port'], db=0)
        self.pubsub = self.redis_client.pubsub()
        
        for key in self.redis_keys:
            self.pubsub.subscribe(key)
            self.logger.info(f"Subscribed to Redis key: {key}")

        # Start listening to Redis events in a separate thread
        self.redis_thread = threading.Thread(target=self.listen_to_redis)
        self.redis_thread.daemon = True  # Ensure the thread stops when the main program exits
        self.redis_thread.start()

    def listen_to_redis(self):
        """Listen for Redis events and trigger any registered callbacks."""
        for message in self.pubsub.listen():
            self.on_redis_message(message)

    def on_redis_message(self, message):
        """Handle incoming Redis messages and trigger any registered callbacks."""
        key = message['channel'].decode('utf-8')
        data = message['data']
        self.logger.info(f"Received Redis message on key {key}: {data}")
        
        # Store the message in knowledge
        self.knowledge.write(key, data)

        # Trigger any registered callbacks for this Redis key
        self.trigger_callbacks(key, data)

    def publish_redis(self, key, data):
        """Publish a message to Redis key."""
        self.redis_client.set(key, data)
        self.logger.info(f"Published to Redis key {key}: {data}")

    ### Helper Methods ###

    def shutdown(self):
        """Shut down the Event Handler."""
        self.mqtt_client.loop_stop()
        # Commenting out ROS2-related shutdown
        # if self.ros2_node:
        #     rclpy.shutdown()
        # Optionally wait for the Redis thread to finish
        if self.redis_thread:
            self.redis_thread.join()
        self.logger.info("Event Handler shut down.")
