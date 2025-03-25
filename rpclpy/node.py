import yaml
import logging
from rpclpy.CommunicationManager import CommunicationManager
from rpclpy.KnowledgeManager import KnowledgeManager
from rpclpy.LoggingAndTracking import LoggingAndTrackingHandler
import json

class Node:
    def __init__(self, config, verbose = False):
        # self.config = self.load_config(config)
        self.config = config
        self.logger = self._initialize_logger()
        self.knowledge = self._initialize_knowledge()  # Initialize knowledge within the component
        self.event_manager = self._initialize_event_manager()
        self.message_manager = self._initialize_message_manager()

        # Initialize MQTT and ROS2 Event
        if self.event_manager:
            self.logger.info(f"{self.__class__.__name__} is using {self.config['Event_Manager_Config']['protocol']} Communication Manager")
        if self.message_manager:
            self.logger.info(f"{self.__class__.__name__} is using {self.config['Event_Manager_Config']['protocol']} Communication Manager")

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def _initialize_logger(self):

        # Create the main logger.
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(self.config['Logger_Config']['log_level'])
        # Instantiate the custom logging handler.
        custom_handler = LoggingAndTrackingHandler(self.config['Logger_Config'])
        formatter = logging.Formatter(self.config['Logger_Config']['format'])
        custom_handler.setFormatter(formatter)
        logger.addHandler(custom_handler)

        return logger

    def _initialize_knowledge(self):
        """Initialize the Knowledge object based on the config."""
        self.logger.info(f"Initializing Knowledge: {self.config['Knowledge_Config']['knowledge_type']} knowledge")
        return KnowledgeManager(self.config['Knowledge_Config'])
    
    def _initialize_event_manager(self):
        "Initialize the Event Manager based on the config."""
        self.logger.info("Initializing Event Manager")
        return CommunicationManager(config=self.config['Event_Manager_Config'])
    
    def _initialize_message_manager(self):
        """Initialize the IO Manager based on the config."""
        self.logger.info("Initializing IO Manager")
        return CommunicationManager(config=self.config['Message_Manager_Config'])

    def start(self):
        """Start the component and enable Event."""
        self.logger.info(f"{self.__class__.__name__} is starting...")
        if self.event_manager:
            self.event_manager.start()
        if self.message_manager:
            self.message_manager.start()

    def shutdown(self):
        """Shutdown the component and stop Event."""
        self.logger.info(f"{self.__class__.__name__} is shutting down...")
        if self.event_manager:
            self.event_manager.stop()
        if self.message_manager:
            self.message_manager.stop()

    def publish_event(self, event_key, message = "True"):
        """Publish Event using the Event manager."""
        if self.event_manager:
            self.event_manager.publish(event_key, message)
            # print (f"Event Key: {event_key}, Message: {message}")
        else:
            self.logger.warning("Event manager is not set for Event publishing.")

    def publish_message(self, event_key, message = "True"):
        """Publish Event using the Event manager."""
        if self.message_manager:
            self.message_manager.publish(event_key, message)
        else:
            self.logger.warning("Event manager is not set for Event publishing.")

    def register_event_callback(self, event_key, callback):
        """Register a callback for Event manager events (MQTT or Redis)."""
        if self.event_manager:
            self.event_manager.subscribe(event_key, callback)
            self.logger.info(f"Registered callback for event: {event_key}")
        else:
            self.logger.warning("Event manager is not set for registering event callbacks.")

    def register_message_callback(self, event_key, callback):
        """Register a callback for Event manager events (MQTT or Redis)."""
        if self.message_manager:
            self.message_manager.subscribe(event_key, callback)
            self.logger.info(f"Registered callback for event: {event_key}")
        else:
            self.logger.warning("Event manager is not set for registering event callbacks.")

    def read_knowledge(self, key, queueSize=1):
        """Read a value from the Knowledge Manager."""
        value = self.knowledge.read(key, queueSize)
        if value is not None:
            value = value.decode('utf-8')  # Convert bytes to string
            try:
                value = json.loads(value)  # Try to deserialize the value if it's a JSON string
            except json.JSONDecodeError:
                pass  # If it's not JSON, return it as a string
        return value

    def write_knowledge(self, key, value):
        """Write a value to the Knowledge Manager."""
        if isinstance(key, str):
            if isinstance(value, str):
                value = str(value)
                # print(f"type of the {key} value:{type(value)}")
            return self.knowledge.write(key, value)
        else:
            # Convert the class instance to a dictionary
            class_dict = {}
            for key, value in key.__dict__.items():

                # Remove leading underscore for protected attributes
                public_key = key.lstrip('_')

                # Add the attribute to the dictionary
                class_dict[public_key] = value

            value = json.dumps(class_dict)  # Serialize the dictionary to a JSON string
            return self.knowledge.write(key.name, value)