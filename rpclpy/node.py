import yaml
import logging
from rpclpy.CommunicationManager import CommunicationManager
from rpclpy.KnowledgeManager import KnowledgeManager
import json

class Node:
    def __init__(self, config, verbose = False):
        self.config = self.load_config(config)
        self.logger = self._initialize_logger()
        # 'memcached': {"host": "127.0.0.1", "port": 11211},
        # self.knowledge = self._initialize_knowledge()  # Initialize knowledge within the component
        self.knowledge = KnowledgeManager("redis", {"host": "localhost", "port": 6379, "db": 0})
        # self.knowledge = KnowledgeManager('memcached', {"host": "127.0.0.1", "port": 11211})
        # self.communication_manager = CommunicationManager("mqtt", {"broker": "localhost", "port": 1883})
        self.communication_manager = CommunicationManager("rabbitmq", {"host": "localhost", "port": 5672})
        # self.communication_manager = CommunicationManager("redis", {"host": "localhost", "port": 6379})
        # self.communication_manager = self._initialize_communication_manager()  # Initialize Event manager
        
        

        # Initialize MQTT and ROS2 Event
        if self.communication_manager:
            self.logger.info(f"{self.__class__.__name__} is using Communication Manager")

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def _initialize_logger(self):
        """Initialize the logger (same as before)."""
        log_config = self.config.get("logging", {})
        logger = logging.getLogger(self.__class__.__name__)
        log_level = log_config.get("level", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_file = log_config.get("file", None)
        
        formatter = logging.Formatter(log_format)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def _initialize_knowledge(self):
        """Initialize the Knowledge object based on the config."""
        self.logger.info(f"Initializing Knowledge: {self.config['knowledge_config']['storage_type']} knowledge")
        return KnowledgeManager(self.config['knowledge_config'])

    def _initialize_communication_manager(self):
        """Initialize the Event Manager based on the config."""
        self.logger.info("Initializing Event Manager")
        return CommunicationManager(self.config, self.knowledge, self.logger)

    def start(self):
        """Start the component and enable Event."""
        self.logger.info(f"{self.__class__.__name__} is starting...")
        if self.communication_manager:
            self.communication_manager.start()

    def shutdown(self):
        """Shutdown the component and stop Event."""
        self.logger.info(f"{self.__class__.__name__} is shutting down...")
        if self.communication_manager:
            self.communication_manager.stop()

    def publish_event(self, event_key, message = True):
        """Publish Event using the Event manager."""
        if self.communication_manager:
            self.communication_manager.publish(event_key, message)
        else:
            self.logger.warning("Event manager is not set for Event publishing.")


    def register_event_callback(self, event_key, callback):
        """Register a callback for Event manager events (MQTT or Redis)."""
        if self.communication_manager:
            self.communication_manager.subscribe(event_key, callback)
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