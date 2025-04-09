import time
import string
import random

# Constants for configuration keys
KEY_KNOWLEDGE_TYPE = "knowledge_type"
KEY_HOST = "host"
KEY_PORT = "port"
KEY_DB = "db"
KEY_TOPIC = "topic"
KEY_BOOTSTRAP_SERVERS = "bootstrap_servers"

# Constants for backends
BACKEND_REDIS = "redis"
BACKEND_MEMCACHED = "memcached"
BACKEND_IGNITE = "ignite"
BACKEND_HAZELCAST = "hazelcast"
BACKEND_TARANTOOL = "tarantool"
BACKEND_AEROSPIKE = "aerospike"
BACKEND_KAFKA = "kafka"
BACKEND_SQLITE = "sqlite"

# Constants for SQLite queries and in-memory DB
SQLITE_MEMORY = ":memory:"
SQLITE_CREATE_TABLE = "CREATE TABLE kv (key TEXT PRIMARY KEY, value TEXT)"
SQLITE_INSERT_OR_REPLACE = "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)"
SQLITE_SELECT_VALUE = "SELECT value FROM kv WHERE key=?"
SQLITE_DELETE_KEY = "DELETE FROM kv WHERE key=?"

# Other constants
ERROR_UNSUPPORTED_BACKEND = "Unsupported backend: {}"
DEFAULT_CACHE_NAME = "default"
AEROSPIKE_VALUE_FIELD = "value"

# Helper function to generate random strings (if needed)
def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


class KnowledgeManager:
    def __init__(self, config):
        """
        Initialize the KnowledgeManager with a chosen backend.
        Supported backends: redis, memcached, ignite, hazelcast, tarantool, aerospike, kafka, sqlite

        :param config: A dictionary containing all configuration parameters needed by the backend.
        """
        self.backend = config[KEY_KNOWLEDGE_TYPE]
        if self.backend == BACKEND_REDIS:
            import redis
            self.client = redis.Redis(host=config[KEY_HOST], port=config[KEY_PORT], db=config[KEY_DB])
        elif self.backend == BACKEND_MEMCACHED:
            import memcache
            self.client = memcache.Client([(config[KEY_HOST], config[KEY_PORT])])
        elif self.backend == BACKEND_IGNITE:
            from pyignite import Client
            self.client = Client()
            self.client.connect(config[KEY_HOST], config[KEY_PORT])
        elif self.backend == BACKEND_HAZELCAST:
            import hazelcast
            # Configuration for hazelcast client is passed via config.
            self.client = hazelcast.HazelcastClient(**config)
        elif self.backend == BACKEND_TARANTOOL:
            import tarantool
            self.client = tarantool.Connection(config[KEY_HOST], config[KEY_PORT])
        elif self.backend == BACKEND_AEROSPIKE:
            import aerospike
            cfg = {'hosts': [(config[KEY_HOST], config[KEY_PORT])]}
            self.client = aerospike.client(cfg).connect()
        elif self.backend == BACKEND_KAFKA:
            from kafka import KafkaProducer, KafkaConsumer
            self.topic = config[KEY_TOPIC]
            self.producer = KafkaProducer(bootstrap_servers=config[KEY_BOOTSTRAP_SERVERS])
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=config[KEY_BOOTSTRAP_SERVERS],
                auto_offset_reset='earliest',
                consumer_timeout_ms=1000
            )
        elif self.backend == BACKEND_SQLITE:
            import sqlite3
            self.conn = sqlite3.connect(SQLITE_MEMORY)
            self.cursor = self.conn.cursor()
            self.cursor.execute(SQLITE_CREATE_TABLE)
        else:
            raise ValueError(ERROR_UNSUPPORTED_BACKEND.format(self.backend))

    def write(self, key, value):
        """Write a key-value pair to the backend."""
        if self.backend == BACKEND_REDIS:
            return self.client.set(key, value)
        elif self.backend == BACKEND_MEMCACHED:
            return self.client.set(key, value)
        elif self.backend == BACKEND_IGNITE:
            cache = self.client.get_or_create_cache(DEFAULT_CACHE_NAME)
            return cache.put(key, value)
        elif self.backend == BACKEND_HAZELCAST:
            hz_map = self.client.get_map(DEFAULT_CACHE_NAME).blocking()
            return hz_map.put(key, value)
        elif self.backend == BACKEND_TARANTOOL:
            # Assumes a space 'kv' exists with schema (key, value)
            return self.client.insert('kv', (key, value))
        elif self.backend == BACKEND_AEROSPIKE:
            # Note: In Aerospike, the key should be a tuple; this is a simplified example.
            return self.client.put(key, {AEROSPIKE_VALUE_FIELD: value})
        elif self.backend == BACKEND_KAFKA:
            # Kafka is a streaming system; here, writing means sending a message.
            future = self.producer.send(self.topic, key=key.encode(), value=value.encode())
            return future.get(timeout=10)
        elif self.backend == BACKEND_SQLITE:
            try:
                self.cursor.execute(SQLITE_INSERT_OR_REPLACE, (key, value))
                self.conn.commit()
                return True
            except Exception as e:
                self.conn.rollback()
                return False

    def read(self, key, queueSize=1):
        """Read the value for a given key from the backend."""
        if self.backend == BACKEND_REDIS:
            return self.client.get(key)
        elif self.backend == BACKEND_MEMCACHED:
            return self.client.get(key)
        elif self.backend == BACKEND_IGNITE:
            cache = self.client.get_or_create_cache(DEFAULT_CACHE_NAME)
            return cache.get(key)
        elif self.backend == BACKEND_HAZELCAST:
            hz_map = self.client.get_map(DEFAULT_CACHE_NAME).blocking()
            return hz_map.get(key)
        elif self.backend == BACKEND_TARANTOOL:
            result = self.client.select('kv', 0, 1, 0, key)
            return result[0][1] if result else None
        elif self.backend == BACKEND_AEROSPIKE:
            try:
                (key_rec, metadata, record) = self.client.get(key)
                return record.get(AEROSPIKE_VALUE_FIELD)
            except Exception as e:
                return None
        elif self.backend == BACKEND_KAFKA:
            # For Kafka, simulate reading by consuming one message from the topic.
            for message in self.consumer:
                return message.value.decode()
            return None
        elif self.backend == BACKEND_SQLITE:
            self.cursor.execute(SQLITE_SELECT_VALUE, (key,))
            row = self.cursor.fetchone()
            return row[0] if row else None

    def delete(self, key):
        """Delete the key-value pair identified by key from the backend."""
        if self.backend == BACKEND_REDIS:
            return self.client.delete(key)
        elif self.backend == BACKEND_MEMCACHED:
            return self.client.delete(key)
        elif self.backend == BACKEND_IGNITE:
            cache = self.client.get_or_create_cache(DEFAULT_CACHE_NAME)
            return cache.remove(key)
        elif self.backend == BACKEND_HAZELCAST:
            hz_map = self.client.get_map(DEFAULT_CACHE_NAME).blocking()
            return hz_map.remove(key)
        elif self.backend == BACKEND_TARANTOOL:
            return self.client.delete('kv', key)
        elif self.backend == BACKEND_AEROSPIKE:
            try:
                return self.client.remove(key)
            except Exception as e:
                return None
        elif self.backend == BACKEND_KAFKA:
            # Kafka does not support deleting individual messages.
            return None
        elif self.backend == BACKEND_SQLITE:
            self.cursor.execute(SQLITE_DELETE_KEY, (key,))
            self.conn.commit()
            return True

    def exists(self, key):
        """Check whether a key exists in the backend."""
        if self.backend == BACKEND_REDIS:
            return self.client.exists(key)
        elif self.backend == BACKEND_MEMCACHED:
            return self.client.get(key) is not None
        elif self.backend == BACKEND_IGNITE:
            cache = self.client.get_or_create_cache(DEFAULT_CACHE_NAME)
            return cache.get(key) is not None
        elif self.backend == BACKEND_HAZELCAST:
            hz_map = self.client.get_map(DEFAULT_CACHE_NAME).blocking()
            return hz_map.contains_key(key)
        elif self.backend == BACKEND_TARANTOOL:
            result = self.client.select('kv', 0, 1, 0, key)
            return bool(result)
        elif self.backend == BACKEND_AEROSPIKE:
            try:
                self.client.get(key)
                return True
            except Exception as e:
                return False
        elif self.backend == BACKEND_KAFKA:
            # Kafka does not provide a means to check for existence of a message by key.
            return None
        elif self.backend == BACKEND_SQLITE:
            self.cursor.execute('SELECT 1 FROM kv WHERE key=?', (key,))
            return self.cursor.fetchone() is not None


def benchmark_operations(backend, config, num_operations=1000):
    print(f"\nBenchmarking backend: {backend.upper()} with {num_operations} operations")
    try:
        km = KnowledgeManager(config)
    except Exception as e:
        print(f"Could not initialize backend '{backend}': {e}")
        return

    keys = [f'key_{i}' for i in range(num_operations)]
    value = "sample_value"

    # Write benchmark
    start_time = time.time()
    for key in keys:
        km.write(key, value)
    write_time = time.time() - start_time
    print(f"Write: {write_time:.6f} sec total, {(write_time/num_operations)*1e6:.2f} µs/op")

    # Read benchmark
    start_time = time.time()
    for key in keys:
        km.read(key)
    read_time = time.time() - start_time
    print(f"Read: {read_time:.6f} sec total, {(read_time/num_operations)*1e6:.2f} µs/op")

    # Exists benchmark
    start_time = time.time()
    for key in keys:
        km.exists(key)
    exists_time = time.time() - start_time
    print(f"Exists: {exists_time:.6f} sec total, {(exists_time/num_operations)*1e6:.2f} µs/op")

    # Delete benchmark
    start_time = time.time()
    for key in keys:
        km.delete(key)
    delete_time = time.time() - start_time
    print(f"Delete: {delete_time:.6f} sec total, {(delete_time/num_operations)*1e6:.2f} µs/op")


if __name__ == '__main__':
    # Define backend configurations here. Adjust values as needed for your environment.
    backend_configs = {
        'redis': {"host": "localhost", "port": 6379, "db": 0},
        # 'memcached': {"host": "127.0.0.1", "port": 11211},
        # 'ignite': {"host": "127.0.0.1", "port": 10800}, #TODO:Test this
        # 'hazelcast': {},  # Provide Hazelcast-specific configuration if needed. #TODO:Test this
        # 'tarantool': {"host": "127.0.0.1", "port": 3301}, #TODO:Test this
        # 'aerospike': {"host": "127.0.0.1", "port": 3000}, #TODO:Test this
        # 'kafka': {"bootstrap_servers": "localhost:9092", "topic": "knowledge"}, #TODO:Test this
        # 'sqlite': {}  # No configuration required for in-memory SQLite.
    }

    # Benchmark each backend.
    for backend, config in backend_configs.items():
        benchmark_operations(backend, config, num_operations=1000)
