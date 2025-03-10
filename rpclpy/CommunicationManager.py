import threading
import time

class CommunicationManager:
    def __init__(self, protocol, config):
        """
        Initialize the communication manager with the given protocol and configuration.
        Protocol-specific modules are imported here.
        """
        self.protocol = protocol.lower()
        self.config = config
        self.publish_topics = []
        self.subscribe_topics = []
        self.event_callbacks = {}  # Mapping: topic -> callback function
        self._consumer_thread = None

        if self.protocol == 'mqtt':
            import paho.mqtt.client as mqtt
            self.mqtt = mqtt
            self._mqtt_client = None
        elif self.protocol == 'rabbitmq':
            import pika
            self.pika = pika
            self._rabbitmq_connection = None
            self._rabbitmq_channel = None
        elif self.protocol == 'kafka':
            from kafka import KafkaProducer, KafkaConsumer
            self.KafkaProducer = KafkaProducer
            self.KafkaConsumer = KafkaConsumer
            self._kafka_producer = None
            self._kafka_consumer = None
        elif self.protocol == 'redis':
            import redis
            self.redis = redis
            self._redis_client = None
            self._redis_pubsub = None
        elif self.protocol == 'zenoh':
            try:
                import zenoh
            except ImportError:
                zenoh = None
            self.zenoh = zenoh
            self._zenoh_session = None
        elif self.protocol == 'websocket':
            import websocket
            self.websocket = websocket
            self._websocket_app = None
            self._websocket_thread = None
        elif self.protocol in ['tcp', 'tcp/ip']:
            import socket
            self.socket = socket
            self._tcp_socket = None
            self._tcp_thread = None
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

    def start(self):
        """Start the client for the selected protocol."""
        if self.protocol == 'mqtt':
            self._start_mqtt()
        elif self.protocol == 'rabbitmq':
            self._start_rabbitmq()
        elif self.protocol == 'kafka':
            self._start_kafka()
        elif self.protocol == 'redis':
            self._start_redis()
        elif self.protocol == 'zenoh':
            self._start_zenoh()
        elif self.protocol == 'websocket':
            self._start_websocket()
        elif self.protocol in ['tcp', 'tcp/ip']:
            self._start_tcp()
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

    def _start_mqtt(self):
        self._mqtt_client = self.mqtt.Client()
        def on_connect(client, userdata, flags, rc):
            for topic in self.subscribe_topics:
                client.subscribe(topic)
        def on_message(client, userdata, msg):
            if msg.topic in self.event_callbacks:
                self.event_callbacks[msg.topic](msg.payload.decode())
        self._mqtt_client.on_connect = on_connect
        self._mqtt_client.on_message = on_message
        broker = self.config['broker']
        port = self.config['port']
        self._mqtt_client.connect(broker, port, 60)
        self._mqtt_client.loop_start()

    def _start_rabbitmq(self):
        parameters = self.pika.ConnectionParameters(
            host=self.config['host'],
            port=self.config['port']
        )
        self._rabbitmq_connection = self.pika.BlockingConnection(parameters)
        self._rabbitmq_channel = self._rabbitmq_connection.channel()
        for topic in self.subscribe_topics:
            self._rabbitmq_channel.queue_declare(queue=topic)
            def callback(ch, method, properties, body, topic=topic):
                if topic in self.event_callbacks:
                    self.event_callbacks[topic](body.decode())
            self._rabbitmq_channel.basic_consume(queue=topic, on_message_callback=callback, auto_ack=True)
        def consume():
            self._rabbitmq_channel.start_consuming()
        self._consumer_thread = threading.Thread(target=consume, daemon=True)
        self._consumer_thread.start()

    def _start_kafka(self):
        bootstrap_servers = self.config['bootstrap_servers']
        self._kafka_producer = self.KafkaProducer(bootstrap_servers=bootstrap_servers)
        if self.subscribe_topics:
            self._kafka_consumer = self.KafkaConsumer(*self.subscribe_topics,
                                                       bootstrap_servers=bootstrap_servers,
                                                       auto_offset_reset='earliest',
                                                       consumer_timeout_ms=1000)
            def consume():
                for msg in self._kafka_consumer:
                    if msg.topic in self.event_callbacks:
                        self.event_callbacks[msg.topic](msg.value.decode())
            self._consumer_thread = threading.Thread(target=consume, daemon=True)
            self._consumer_thread.start()

    def _start_redis(self):
        host = self.config['host']
        port = self.config['port']
        self._redis_client = self.redis.Redis(host=host, port=port, decode_responses=True)
        self._redis_pubsub = self._redis_client.pubsub()
        if self.subscribe_topics:
            self._redis_pubsub.subscribe(*self.subscribe_topics)
            def listen():
                try:
                    for message in self._redis_pubsub.listen():
                        if message['type'] == 'message':
                            topic = message['channel']
                            if topic in self.event_callbacks:
                                self.event_callbacks[topic](message['data'])
                except (ValueError, OSError) as e:
                    # Socket was likely closed during shutdown; exit gracefully.
                    print("Redis listener thread exiting:", e)
            self._consumer_thread = threading.Thread(target=listen, daemon=True)
            self._consumer_thread.start()

    def _start_zenoh(self):
        if self.zenoh is None:
            raise ImportError("Zenoh library is not installed")
        config = self.zenoh.Config()
        self._zenoh_session = self.zenoh.open(config)
        for topic in self.subscribe_topics:
            def zenoh_callback(sample, topic=topic):
                payload = sample.payload.decode() if isinstance(sample.payload, bytes) else sample.payload
                if topic in self.event_callbacks:
                    self.event_callbacks[topic](payload)
            self._zenoh_session.declare_subscriber(topic, zenoh_callback)

    def _start_websocket(self):
        ws_url = self.config['url']
        def on_message(ws, message):
            if ":" in message:
                topic, payload = message.split(":", 1)
                topic = topic.strip()
                payload = payload.strip()
                if topic in self.event_callbacks:
                    self.event_callbacks[topic](payload)
            else:
                for cb in self.event_callbacks.values():
                    cb(message)
        def on_error(ws, error):
            print("WebSocket error:", error)
        def on_close(ws, close_status_code, close_msg):
            print("WebSocket closed", close_status_code, close_msg)
        def on_open(ws):
            print("WebSocket connection opened")
        self._websocket_app = self.websocket.WebSocketApp(ws_url,
                                                            on_message=on_message,
                                                            on_error=on_error,
                                                            on_close=on_close,
                                                            on_open=on_open)
        def run_ws():
            self._websocket_app.run_forever()
        self._websocket_thread = threading.Thread(target=run_ws, daemon=True)
        self._websocket_thread.start()

    def _start_tcp(self):
        host = self.config['host']
        port = self.config['port']
        self._tcp_socket = self.socket.socket(self.socket.AF_INET, self.socket.SOCK_STREAM)
        self._tcp_socket.connect((host, port))
        def listen_tcp():
            while True:
                try:
                    data = self._tcp_socket.recv(1024)
                    if not data:
                        break
                    message = data.decode().strip()
                    if ":" in message:
                        topic, payload = message.split(":", 1)
                        topic = topic.strip()
                        payload = payload.strip()
                        if topic in self.event_callbacks:
                            self.event_callbacks[topic](payload)
                    else:
                        for cb in self.event_callbacks.values():
                            cb(message)
                except Exception as e:
                    print("TCP receiving error:", e)
                    break
        self._tcp_thread = threading.Thread(target=listen_tcp, daemon=True)
        self._tcp_thread.start()

    def subscribe(self, topic, callback):
        """Register a callback for the given topic."""
        if topic not in self.subscribe_topics:
            self.subscribe_topics.append(topic)
        self.event_callbacks[topic] = callback

        if self.protocol == 'mqtt' and self._mqtt_client:
            self._mqtt_client.subscribe(topic)
        elif self.protocol == 'rabbitmq' and self._rabbitmq_channel:
            self._rabbitmq_channel.queue_declare(queue=topic)
            def callback_wrapper(ch, method, properties, body, topic=topic):
                self.event_callbacks[topic](body.decode())
            self._rabbitmq_channel.basic_consume(queue=topic, on_message_callback=callback_wrapper, auto_ack=True)
        elif self.protocol == 'redis' and self._redis_pubsub:
            self._redis_pubsub.subscribe(topic)
        elif self.protocol == 'zenoh' and self._zenoh_session:
            def zenoh_callback(sample, topic=topic):
                payload = sample.payload.decode() if isinstance(sample.payload, bytes) else sample.payload
                self.event_callbacks[topic](payload)
            self._zenoh_session.declare_subscriber(topic, zenoh_callback)
        # For Kafka, WebSocket, and TCP dynamic subscription is not handled

    def publish(self, topic, message):
        """Publish a message to the specified topic."""
        if topic not in self.publish_topics:
            self.publish_topics.append(topic)
        if self.protocol == 'mqtt' and self._mqtt_client:
            result = self._mqtt_client.publish(topic, message)
            return result
        elif self.protocol == 'rabbitmq' and self._rabbitmq_channel:
            self._rabbitmq_channel.queue_declare(queue=topic)
            self._rabbitmq_channel.basic_publish(exchange='', routing_key=topic, body=message)
            return f"Published to {topic}: {message}"
        elif self.protocol == 'kafka' and self._kafka_producer:
            self._kafka_producer.send(topic, value=message.encode())
            self._kafka_producer.flush()
            return f"Published to {topic}: {message}"
        elif self.protocol == 'redis' and self._redis_client:
            self._redis_client.publish(topic, message)
            return f"Published to {topic}: {message}"
        elif self.protocol == 'zenoh' and self._zenoh_session:
            self._zenoh_session.put(topic, message.encode())
            return f"Published to {topic}: {message}"
        elif self.protocol == 'websocket' and self._websocket_app:
            if self._websocket_app.sock and self._websocket_app.sock.connected:
                send_message = f"{topic}: {message}"
                self._websocket_app.send(send_message)
                return f"Published to {topic}: {message}"
            else:
                raise RuntimeError("WebSocket connection not established")
        elif self.protocol in ['tcp', 'tcp/ip'] and self._tcp_socket:
            send_message = f"{topic}: {message}\n"
            self._tcp_socket.sendall(send_message.encode())
            return f"Published to {topic}: {message}"
        else:
            raise RuntimeError("Client not started or unsupported protocol for publishing.")

    def stop(self):
        """Stop the client and close any open connections."""
        if self.protocol == 'mqtt' and self._mqtt_client:
            self._mqtt_client.loop_stop()
            self._mqtt_client.disconnect()
        elif self.protocol == 'rabbitmq' and self._rabbitmq_connection:
            self._rabbitmq_connection.close()
        elif self.protocol == 'kafka':
            if self._kafka_consumer:
                self._kafka_consumer.close()
        elif self.protocol == 'redis' and self._redis_pubsub:
            self._redis_pubsub.close()
        elif self.protocol == 'zenoh' and self._zenoh_session:
            self._zenoh_session.close()
        elif self.protocol == 'websocket' and self._websocket_app:
            self._websocket_app.close()
            if self._websocket_thread:
                self._websocket_thread.join(timeout=1)
        elif self.protocol in ['tcp', 'tcp/ip'] and self._tcp_socket:
            self._tcp_socket.close()
        if self._consumer_thread:
            self._consumer_thread.join(timeout=1)


# ----------------- Main Test Script -----------------

def start_tcp_echo_server(host, port):
    """Start a simple TCP echo server."""
    import socket
    def handle_client(client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            client_socket.sendall(data)
        client_socket.close()
    def server_loop():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)
        print(f"TCP Echo Server started on {host}:{port}")
        while True:
            client_socket, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket,), daemon=True)
            client_thread.start()
    server_thread = threading.Thread(target=server_loop, daemon=True)
    server_thread.start()
    return server_thread

def start_ws_echo_server(host, port):
    import asyncio
    import websockets

    async def ws_echo(websocket, path):
        async for message in websocket:
            await websocket.send(message)

    async def server_main():
        async with websockets.serve(ws_echo, host, port):
            await asyncio.Future()  # Run forever

    def run_server():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server_main())

    ws_thread = threading.Thread(target=run_server, daemon=True)
    ws_thread.start()
    return ws_thread


def test_communication_manager(protocol, config):
    """Test a given protocol by subscribing and publishing on 'test/topic'."""
    print(f"\n--- Testing {protocol.upper()} ---")
    received_messages = []
    def callback(msg):
        print(f"[{protocol.upper()}] Received: {msg}")
        received_messages.append(msg)
    cm = CommunicationManager(protocol, config)
    cm.subscribe("test/topic", callback)
    cm.start()
    time.sleep(2)
    result = cm.publish("test/topic", "Hello, world!")
    print(result)
    time.sleep(2)
    cm.stop()
    return received_messages

if __name__ == "__main__":
    # Configuration for each protocol is defined in the main script.
    protocols_config = {
        "mqtt": {"broker": "localhost", "port": 1883},
        "rabbitmq": {"host": "localhost", "port": 5672},
        # "kafka": {"bootstrap_servers": "localhost:9092"}, #TODO: Add Kafka configuration, test the Kafka protocol
        "redis": {"host": "localhost", "port": 6379},
        # "zenoh": {},  # Add Zenoh configuration if necessary TODO: Add Zenoh configuration, test the Zenoh protocol
        "websocket": {"url": "ws://localhost:8765"},
        "tcp": {"host": "localhost", "port": 9000}
    }

    # Start WebSocket and TCP echo servers for testing.
    try:
        ws_server = start_ws_echo_server("localhost", 8765)
        time.sleep(1)
    except Exception as e:
        print("WebSocket server failed to start:", e)
        protocols_config.pop("websocket", None)

    try:
        tcp_server = start_tcp_echo_server("localhost", 9000)
        time.sleep(1)
    except Exception as e:
        print("TCP echo server failed to start:", e)
        protocols_config.pop("tcp", None)

    results = {}
    for proto, conf in protocols_config.items():
        msgs = test_communication_manager(proto, conf)
        results[proto] = msgs
        print(f"Test for {proto.upper()} received messages: {msgs}")

    print("\nFinal Results:", results)
