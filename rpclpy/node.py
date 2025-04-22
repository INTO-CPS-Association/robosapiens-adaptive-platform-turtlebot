import yaml
import logging
import json
import uuid
import pickle
from datetime import datetime
from rpclpy.CommunicationManager import CommunicationManager
from rpclpy.KnowledgeManager import KnowledgeManager
from rpclpy.LoggingAndTracking import LoggingAndTrackingHandler

# ---------------------------------------------------------------------------
# Configuration Keys
# ---------------------------------------------------------------------------
KEY_EVENT_MANAGER_CONFIG = "Event_Manager_Config"
KEY_MESSAGE_MANAGER_CONFIG = "Message_Manager_Config"
KEY_LOGGER_CONFIG = "Logger_Config"
KEY_KNOWLEDGE_CONFIG = "Knowledge_Config"
KEY_LOG_LEVEL = "log_level"
KEY_LOG_FORMAT = "format"
KEY_PROTOCOL = "protocol"

# ---------------------------------------------------------------------------
# Default Values and Messages
# ---------------------------------------------------------------------------
DEFAULT_EVENT_MESSAGE = {}
ENCODING_UTF8 = "utf-8"

WARN_EVENT_MANAGER_NOT_SET = "Event manager is not set for Event publishing."
WARN_REGISTER_EVENT_CALLBACK_NOT_SET = "Event manager is not set for registering event callbacks."

MSG_INITIALIZING_KNOWLEDGE = "Initializing Knowledge: {} knowledge"
MSG_INITIALIZING_EVENT_MANAGER = "Initializing Event Manager"
MSG_INITIALIZING_IO_MANAGER = "Initializing IO Manager"
MSG_USING_COMMUNICATION_MANAGER = "{} is using {} Communication Manager"
MSG_STARTING = "{} is starting..."
MSG_SHUTTING_DOWN = "{} is shutting down..."
MSG_REGISTER_EVENT_CALLBACK = "Registered callback for event: {}"


class Node:
    def __init__(self, config, verbose=False):
        # self.config = self.load_config(config)
        self.config = config
        self.logger = self._initialize_logger()
        self.knowledge = self._initialize_knowledge()  # Initialize knowledge within the component
        self.event_manager = self._initialize_event_manager()
        self.message_manager = self._initialize_message_manager()

        # Initialize MQTT and ROS2 Event
        if self.event_manager:
            self.logger.info(
                MSG_USING_COMMUNICATION_MANAGER.format(
                    self.__class__.__name__,
                    self.config[KEY_EVENT_MANAGER_CONFIG][KEY_PROTOCOL]
                )
            )
        if self.message_manager:
            self.logger.info(
                MSG_USING_COMMUNICATION_MANAGER.format(
                    self.__class__.__name__,
                    self.config[KEY_MESSAGE_MANAGER_CONFIG][KEY_PROTOCOL]
                )
            )

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)

    def _initialize_logger(self):
        # Create the main logger.
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(self.config[KEY_LOGGER_CONFIG][KEY_LOG_LEVEL])
        # Instantiate the custom logging handler.
        custom_handler = LoggingAndTrackingHandler(self.config[KEY_LOGGER_CONFIG])
        formatter = logging.Formatter(self.config[KEY_LOGGER_CONFIG][KEY_LOG_FORMAT])
        custom_handler.setFormatter(formatter)
        logger.addHandler(custom_handler)
        return logger

    def _initialize_knowledge(self):
        """Initialize the Knowledge object based on the config."""
        self.logger.info(
            MSG_INITIALIZING_KNOWLEDGE.format(
                self.config[KEY_KNOWLEDGE_CONFIG]["knowledge_type"]
            )
        )
        return KnowledgeManager(self.config[KEY_KNOWLEDGE_CONFIG])

    def _initialize_event_manager(self):
        """Initialize the Event Manager based on the config."""
        self.logger.info(MSG_INITIALIZING_EVENT_MANAGER)
        return CommunicationManager(config=self.config[KEY_EVENT_MANAGER_CONFIG])

    def _initialize_message_manager(self):
        """Initialize the IO Manager based on the config."""
        self.logger.info(MSG_INITIALIZING_IO_MANAGER)
        return CommunicationManager(config=self.config[KEY_MESSAGE_MANAGER_CONFIG])

    def start(self):
        """Start the component and enable Event."""
        self.logger.info(MSG_STARTING.format(self.__class__.__name__))
        if self.event_manager:
            self.event_manager.start()
        if self.message_manager:
            self.message_manager.start()

    def shutdown(self):
        """Shutdown the component and stop Event."""
        self.logger.info(MSG_SHUTTING_DOWN.format(self.__class__.__name__))
        if self.event_manager:
            self.event_manager.stop()
        if self.message_manager:
            self.message_manager.stop()
            

    def publish_event(self, event_key, message=DEFAULT_EVENT_MESSAGE):
        """Publish Event using the Event manager."""
        if isinstance(event_key, str):
            # Generate a unique ID for the message
            message_id = str(uuid.uuid4().hex[:8])
            # Get the current timestamp in ISO 8601 format
            timestamp = datetime.now().isoformat()
            
            message['uid'] = message_id
            message['timestamp'] = timestamp
        
            if self.event_manager:
                self.event_manager.publish(event_key,  json.dumps(message))
            else:
                self.logger.warning(WARN_EVENT_MANAGER_NOT_SET)
        else: 
            event_cls = event_key()
            event_cls.uid = str(uuid.uuid4().hex[:8])
            event_cls.timestamp = datetime.now().isoformat()
            value = json.dumps(event_cls.__dict__)
            self.event_manager.publish(event_cls.topic, value)



    def publish_message(self, event_key, message=DEFAULT_EVENT_MESSAGE):
        """Publish Event using the Event manager."""
        if self.message_manager:
            self.message_manager.publish(event_key, message)
        else:
            self.logger.warning(WARN_EVENT_MANAGER_NOT_SET)

    def register_event_callback(self, event_key, callback):
        """Register a callback for Event manager events (MQTT or Redis)."""
        if self.event_manager:
            self.event_manager.subscribe(event_key, callback)
            self.logger.info(MSG_REGISTER_EVENT_CALLBACK.format(event_key))
        else:
            self.logger.warning(WARN_REGISTER_EVENT_CALLBACK_NOT_SET)

    def register_message_callback(self, event_key, callback):
        """Register a callback for Event manager events (MQTT or Redis)."""
        if self.message_manager:
            self.message_manager.subscribe(event_key, callback)
            self.logger.info(MSG_REGISTER_EVENT_CALLBACK.format(event_key))
        else:
            self.logger.warning(WARN_REGISTER_EVENT_CALLBACK_NOT_SET)

    def read_knowledge(self, key, queueSize=1):
        """Read a value from the Knowledge Manager."""
        if isinstance(key, str):
            value = self.knowledge.read(key, queueSize)
            if value is not None:
                value = value.decode(ENCODING_UTF8)  # Convert bytes to string
                try:
                    value = json.loads(value)  # Try to deserialize the value if it's a JSON string
                except json.JSONDecodeError:
                    pass  # If it's not JSON, return it as a string
            
            return value
        else:
            return self.read_knowledge_as_object(key)
    
    def read_knowledge_as_object(self, cls):
        _cls = cls()
        value = self.knowledge.read(_cls.name)
        # if isinstance(value, str):
        #     value = json.loads(value)
        #     # Extract matching arguments based on class __init__
        # try:
        #     obj = cls(**value)
        # except TypeError:
        #     # Fallback: create empty object and manually set attributes
        #     obj = cls.__new__(cls)

        #     for key, value in value.items():
        #         setattr(obj, key, value)
        #     if hasattr(obj, '__init__'):
        #         try:
        #             obj.__init__()
        #         except TypeError:
        #             pass  # if __init__ expects parameters we skip calling it
        # return obj
        return pickle.loads(value)

    def write_knowledge(self, key, value = None):
        """Write a value to the Knowledge Manager."""
        if isinstance(key, str):
            if isinstance(value, str):
                value = str(value)
            return self.knowledge.write(key, value)
        else:
            return self.write_knowledge_as_object(key)
        
    def write_knowledge_as_object(self, cls):
        # """Write a class instance to the Knowledge Manager."""
        # value = json.dumps(cls.__dict__)
        cls.uid = str(uuid.uuid4().hex[:8])
        cls.timestamp = datetime.now().isoformat()
        value = pickle.dumps(cls)
        return self.knowledge.write(cls.name, value)

