import yaml
import logging
from rpclpy.communication_manager import CommunicationManager
from rpclpy.knowledge import KnowledgeManager

class Node:
    def __init__(self, config, verbose = False):
        self.config = self.load_config(config)
        self.logger = self._initialize_logger()
        self.knowledge = self._initialize_knowledge()  # Initialize knowledge within the component
        self.communication_manager = self._initialize_communication_manager()  # Initialize Event manager
        
        

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
            self.communication_manager.shutdown()

    def publish_event(self, event_key, message = True):
        """Publish Event using the Event manager."""
        if self.communication_manager:
            self.communication_manager.send(event_key, message)
        else:
            self.logger.warning("Event manager is not set for Event publishing.")


    def register_event_callback(self, event_key, callback):
        """Register a callback for Event manager events (MQTT or Redis)."""
        if self.communication_manager:
            self.communication_manager.subscribe(event_key, callback)
            self.logger.info(f"Registered callback for event: {event_key}")
        else:
            self.logger.warning("Event manager is not set for registering event callbacks.")
