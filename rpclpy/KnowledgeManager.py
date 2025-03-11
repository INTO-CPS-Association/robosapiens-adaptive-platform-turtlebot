import time
import string
import random

# Helper function to generate random strings (if needed)
def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


class KnowledgeManager:
    def __init__(self, backend, config):
        """
        Initialize the KnowledgeManager with a chosen backend.
        Supported backends: redis, memcached, ignite, hazelcast, tarantool, aerospike, kafka, sqlite

        :param backend: A string representing the backend to use.
        :param config: A dictionary containing all configuration parameters needed by the backend.
        """
        self.backend = backend.lower()
        if self.backend == 'redis':
            import redis
            self.client = redis.Redis(host=config["host"], port=config["port"], db=config["db"])
        elif self.backend == 'memcached':
            import memcache
            self.client = memcache.Client([(config["host"], config["port"])])
        elif self.backend == 'ignite':
            from pyignite import Client
            self.client = Client()
            self.client.connect(config["host"], config["port"])
        elif self.backend == 'hazelcast':
            import hazelcast
            # Configuration for hazelcast client is passed via config.
            self.client = hazelcast.HazelcastClient(**config)
        elif self.backend == 'tarantool':
            import tarantool
            self.client = tarantool.Connection(config["host"], config["port"])
        elif self.backend == 'aerospike':
            import aerospike
            cfg = {'hosts': [(config["host"], config["port"])]}
            self.client = aerospike.client(cfg).connect()
        elif self.backend == 'kafka':
            from kafka import KafkaProducer, KafkaConsumer
            self.topic = config["topic"]
            self.producer = KafkaProducer(bootstrap_servers=config["bootstrap_servers"])
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=config["bootstrap_servers"],
                auto_offset_reset='earliest',
                consumer_timeout_ms=1000
            )
        elif self.backend == 'sqlite':
            import sqlite3
            self.conn = sqlite3.connect(':memory:')
            self.cursor = self.conn.cursor()
            self.cursor.execute('CREATE TABLE kv (key TEXT PRIMARY KEY, value TEXT)')
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def write(self, key, value):
        """Write a key-value pair to the backend."""
        if self.backend == 'redis':
            if isinstance(key, str):
                return self.client.set(key, value)
            else:
                # Convert the class instance to a dictionary
                class_dict = {}
                for key, value in key.__dict__.items():

                    # Remove leading underscore for protected attributes
                    public_key = key.lstrip('_')

                    # Add the attribute to the dictionary
                    class_dict[public_key] = value

                value = json.dumps(class_dict)  # Serialize the dictionary to a JSON string
                return self.client.set(key.name, value)
        elif self.backend == 'memcached':
            return self.client.set(key, value)
        elif self.backend == 'ignite':
            cache = self.client.get_or_create_cache('default')
            return cache.put(key, value)
        elif self.backend == 'hazelcast':
            hz_map = self.client.get_map("default").blocking()
            return hz_map.put(key, value)
        elif self.backend == 'tarantool':
            # Assumes a space 'kv' exists with schema (key, value)
            return self.client.insert('kv', (key, value))
        elif self.backend == 'aerospike':
            # Note: In Aerospike, the key should be a tuple; this is a simplified example.
            return self.client.put(key, {'value': value})
        elif self.backend == 'kafka':
            # Kafka is a streaming system; here, writing means sending a message.
            future = self.producer.send(self.topic, key=key.encode(), value=value.encode())
            return future.get(timeout=10)
        elif self.backend == 'sqlite':
            try:
                self.cursor.execute('INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)', (key, value))
                self.conn.commit()
                return True
            except Exception as e:
                self.conn.rollback()
                return False

    def read(self, key, queueSize = 1):
        """Read the value for a given key from the backend."""
        if self.backend == 'redis':
            return self.client.get(key)
        elif self.backend == 'memcached':
            return self.client.get(key)
        elif self.backend == 'ignite':
            cache = self.client.get_or_create_cache('default')
            return cache.get(key)
        elif self.backend == 'hazelcast':
            hz_map = self.client.get_map("default").blocking()
            return hz_map.get(key)
        elif self.backend == 'tarantool':
            result = self.client.select('kv', 0, 1, 0, key)
            return result[0][1] if result else None
        elif self.backend == 'aerospike':
            try:
                (key_rec, metadata, record) = self.client.get(key)
                return record.get('value')
            except Exception as e:
                return None
        elif self.backend == 'kafka':
            # For Kafka, simulate reading by consuming one message from the topic.
            for message in self.consumer:
                return message.value.decode()
            return None
        elif self.backend == 'sqlite':
            self.cursor.execute('SELECT value FROM kv WHERE key=?', (key,))
            row = self.cursor.fetchone()
            return row[0] if row else None

    def delete(self, key):
        """Delete the key-value pair identified by key from the backend."""
        if self.backend == 'redis':
            return self.client.delete(key)
        elif self.backend == 'memcached':
            return self.client.delete(key)
        elif self.backend == 'ignite':
            cache = self.client.get_or_create_cache('default')
            return cache.remove(key)
        elif self.backend == 'hazelcast':
            hz_map = self.client.get_map("default").blocking()
            return hz_map.remove(key)
        elif self.backend == 'tarantool':
            return self.client.delete('kv', key)
        elif self.backend == 'aerospike':
            try:
                return self.client.remove(key)
            except Exception as e:
                return None
        elif self.backend == 'kafka':
            # Kafka does not support deleting individual messages.
            return None
        elif self.backend == 'sqlite':
            self.cursor.execute('DELETE FROM kv WHERE key=?', (key,))
            self.conn.commit()
            return True

    def exists(self, key):
        """Check whether a key exists in the backend."""
        if self.backend == 'redis':
            return self.client.exists(key)
        elif self.backend == 'memcached':
            return self.client.get(key) is not None
        elif self.backend == 'ignite':
            cache = self.client.get_or_create_cache('default')
            return cache.get(key) is not None
        elif self.backend == 'hazelcast':
            hz_map = self.client.get_map("default").blocking()
            return hz_map.contains_key(key)
        elif self.backend == 'tarantool':
            result = self.client.select('kv', 0, 1, 0, key)
            return bool(result)
        elif self.backend == 'aerospike':
            try:
                self.client.get(key)
                return True
            except Exception as e:
                return False
        elif self.backend == 'kafka':
            # Kafka does not provide a means to check for existence of a message by key.
            return None
        elif self.backend == 'sqlite':
            self.cursor.execute('SELECT 1 FROM kv WHERE key=?', (key,))
            return self.cursor.fetchone() is not None


def benchmark_operations(backend, config, num_operations=1000):
    print(f"\nBenchmarking backend: {backend.upper()} with {num_operations} operations")
    try:
        km = KnowledgeManager(backend, config)
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
        'memcached': {"host": "127.0.0.1", "port": 11211},
        # 'ignite': {"host": "127.0.0.1", "port": 10800}, #TODO:Test this
        # 'hazelcast': {},  # Provide Hazelcast-specific configuration if needed. #TODO:Test this
        # 'tarantool': {"host": "127.0.0.1", "port": 3301}, #TODO:Test this
        # 'aerospike': {"host": "127.0.0.1", "port": 3000}, #TODO:Test this
        # 'kafka': {"bootstrap_servers": "localhost:9092", "topic": "knowledge"}, #TODO:Test this
        'sqlite': {}  # No configuration required for in-memory SQLite.
    }

    # Benchmark each backend.
    for backend, config in backend_configs.items():
        benchmark_operations(backend, config, num_operations=1000)
