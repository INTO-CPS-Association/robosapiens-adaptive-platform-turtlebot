import redis
import json

class KnowledgeManager:
    def __init__(self, config):
        """
        Initialize the Knowledge object.
        :param config: Configuration for knowledge storage (local or global)
        """
        self.config = config
        self.storage_type = config.get('storage_type', 'local')  # 'local' or 'global'

        if self.storage_type == 'global':
            self.redis_client = redis.StrictRedis(
                host=config['redis_host'], 
                port=config['redis_port'], 
                db=config.get('redis_db', 0)
            )
        else:
            self.local_store = {}

    def write(self, cls, value = True):
        """
        Store a cls in the knowledge base. If the value is a dictionary, it will be serialized.
        :param key: The key for storing the data
        :param value: The value to store (can be a dict, str, int, etc.)
        """
        if isinstance(cls, str):
            if self.storage_type == 'global':
                self.redis_client.set(cls, value)
            else:
                self.local_store[cls] = value
        else:
            # Convert the class instance to a dictionary
            class_dict = {}
            for key, value in cls.__dict__.items():

                # Remove leading underscore for protected attributes
                public_key = key.lstrip('_')

                # Add the attribute to the dictionary
                class_dict[public_key] = value

            value = json.dumps(class_dict)  # Serialize the dictionary to a JSON string
            if self.storage_type == 'global':
                self.redis_client.set(cls.name, value)
            else:
                self.local_store[cls.name] = value

    def read(self, key, queueSize = 1):
        """
        Retrieve a value from the knowledge base. If the value is JSON, it will be deserialized to a Python object.
        :param key: The key for retrieving the data
        :return: The value associated with the key or None if not found
        """
        if self.storage_type == 'global':
            value = self.redis_client.get(key)
            if value is not None:
                value = value.decode('utf-8')  # Convert bytes to string
                try:
                    value = json.loads(value)  # Try to deserialize the value if it's a JSON string
                except json.JSONDecodeError:
                    pass  # If it's not JSON, return it as a string
            return value
        else:
            return self.local_store.get(key, None)

    def delete(self, key):
        """
        Delete a key-value pair from the knowledge base.
        :param key: The key to delete
        """
        if self.storage_type == 'global':
            self.redis_client.delete(key)
        else:
            if key in self.local_store:
                del self.local_store[key]

    def exists(self, key):
        """
        Check if a key exists in the knowledge base.
        :param key: The key to check
        :return: True if the key exists, False otherwise
        """
        if self.storage_type == 'global':
            return self.redis_client.exists(key)
        else:
            return key in self.local_store
