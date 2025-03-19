import logging
import redis
import paho.mqtt.client as mqtt

# Custom logging handler for MQTT.
class MQTTLoggingHandler(logging.Handler):
    def __init__(self, broker='localhost', port=1883, topic='logs'):
        super().__init__()
        self.topic = topic
        self.client = mqtt.Client()
        # Connect to the MQTT broker.
        self.client.connect(broker, port)
        # Start a background network loop.
        self.client.loop_start()

    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.client.publish(self.topic, log_entry)
        except Exception:
            self.handleError(record)

# Custom logging handler for Redis.
class RedisLoggingHandler(logging.Handler):
    def __init__(self, host='localhost', port=6379, channel='logs'):
        super().__init__()
        self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
        self.channel = channel

    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.redis_client.publish(self.channel, log_entry)
        except Exception:
            self.handleError(record)

# Logging and Tracking Handler that wraps one active handler based on configuration.
class LoggingAndTrackingHandler(logging.Handler):
    def __init__(self, config):
        """
        Initialize the handler based on the provided configuration.

        :param config: Dictionary with logging configuration.
            Example:
            {
                'log_level': 'DEBUG',
                'logger_type': 'file',  # Options: 'terminal', 'file', 'mqtt', 'redis'
                'terminal': {},
                'file': {'filename': 'app.log'},
                'mqtt': {'broker': 'localhost', 'port': 1883, 'topic': 'logs'},
                'redis': {'host': 'localhost', 'port': 6379, 'channel': 'logs'}
            }
        """
        super().__init__()
        self.config = config
        self.level = getattr(logging, config.get('log_level', 'INFO').upper(), logging.INFO)
        self.active_handler = self._setup_handler()

    def _setup_handler(self):
        active_type = self.config.get('logger_type', 'terminal').lower()
        if active_type == 'terminal':
            handler = logging.StreamHandler()
        elif active_type == 'file':
            file_config = self.config.get('file', {})
            if 'filename' not in file_config:
                raise ValueError("File handler selected but no filename provided in config.")
            handler = logging.FileHandler(file_config['filename'])
        elif active_type == 'mqtt':
            mqtt_config = self.config.get('mqtt', {})
            handler = MQTTLoggingHandler(
                broker=mqtt_config.get('broker', 'localhost'),
                port=mqtt_config.get('port', 1883),
                topic=mqtt_config.get('topic', 'logs')
            )
        elif active_type == 'redis':
            redis_config = self.config.get('redis', {})
            handler = RedisLoggingHandler(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                channel=redis_config.get('channel', 'logs')
            )
        else:
            raise ValueError(f"Unknown logger_type specified: {active_type}")
        return handler

    def setFormatter(self, fmt):
        """Override setFormatter to also set the formatter on the active handler."""
        super().setFormatter(fmt)
        self.active_handler.setFormatter(fmt)

    def emit(self, record):
        """Delegate emit to the wrapped active handler."""
        self.active_handler.emit(record)

# Example usage:
if __name__ == '__main__':
    config = {
        'log_level': 'DEBUG',
        'logger_type': 'redis',  # Change to 'terminal', 'file', 'mqtt', or 'redis' as needed.
        'terminal': {},
        'file': {'filename': 'app.log'},
        'mqtt': {'broker': 'localhost', 'port': 1883, 'topic': 'logs'},
        'redis': {'host': 'localhost', 'port': 6379, 'channel': 'logs'}
    }

    # Create the main logger.
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)

    # Instantiate the custom logging handler.
    custom_handler = LoggingAndTrackingHandler(config)

    # Set the formatter here in main (instead of inside the class).
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)
    custom_handler.setFormatter(formatter)

    logger.addHandler(custom_handler)

    # Log some test messages.
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
