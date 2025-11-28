import threading
import time
import socket

# Constants
KEY_PROTOCOL = "protocol"
PROTOCOL_MQTT = "mqtt"
PROTOCOL_RABBITMQ = "rabbitmq"
PROTOCOL_KAFKA = "kafka"
PROTOCOL_REDIS = "redis"
PROTOCOL_ZENOH = "zenoh"
PROTOCOL_WEBSOCKET = "websocket"
PROTOCOL_TCP = "tcp"
PROTOCOL_TCP_ALT = "tcp/ip"

KEY_BROKER = "broker"
KEY_PORT = "port"
KEY_HOST = "host"
KEY_BOOTSTRAP_SERVERS = "bootstrap_servers"
KEY_URL = "url"

TEST_TOPIC = "test/topic"
DEFAULT_PUBLISH_MESSAGE = "Hello, world!"

WARNING_UNSUPPORTED_PROTOCOL = "Unsupported protocol: {}"
ZENOH_IMPORT_ERROR = "Zenoh library is not installed"
SOCKET_CLOSED_MESSAGE = "Redis listener thread exiting: {}"
WS_NOT_ESTABLISHED = "WebSocket connection not established"
WS_ERROR_PREFIX = "WebSocket error:"
WS_CLOSED_PREFIX = "WebSocket closed"
TCP_RECEIVE_ERROR = "TCP receiving error: {}"

class CommunicationManager:
    def __init__(self, config):
        """
        Initialize the communication manager with the given protocol and configuration.
        Protocol-specific modules are imported here.
        """
        self.protocol = config.get(KEY_PROTOCOL)
        self.config = config
        self.publish_topics = []
        self.subscribe_topics = []
        self.event_callbacks = {}  # Mapping: topic -> callback function
        self._consumer_thread = None

        if self.protocol == PROTOCOL_MQTT:
            import paho.mqtt.client as mqtt
            self.mqtt = mqtt
            self._mqtt_client = None
        elif self.protocol == PROTOCOL_RABBITMQ:
            import pika
            self.pika = pika
            self._rabbitmq_connection = None
            self._rabbitmq_channel = None
        elif self.protocol == PROTOCOL_KAFKA:
            from kafka import KafkaProducer, KafkaConsumer
            self.KafkaProducer = KafkaProducer
            self.KafkaConsumer = KafkaConsumer
            self._kafka_producer = None
            self._kafka_consumer = None
        elif self.protocol == PROTOCOL_REDIS:
            import redis
            self.redis = redis
            self._redis_client = None
            self._redis_pubsub = None
        elif self.protocol == PROTOCOL_ZENOH:
            try:
                import zenoh
            except ImportError:
                zenoh = None
            self.zenoh = zenoh
            self._zenoh_session = None
        elif self.protocol == PROTOCOL_WEBSOCKET:
            import websocket
            self.websocket = websocket
            self._websocket_app = None
            self._websocket_thread = None
        elif self.protocol in [PROTOCOL_TCP, PROTOCOL_TCP_ALT]:
            # Using already imported socket module.
            self._tcp_socket = None
            self._tcp_thread = None
        else:
            raise ValueError(WARNING_UNSUPPORTED_PROTOCOL.format(self.protocol))

    def start(self):
        """Start the client for the selected protocol."""
        if self.protocol == PROTOCOL_MQTT:
            self._start_mqtt()
        elif self.protocol == PROTOCOL_RABBITMQ:
            self._start_rabbitmq()
        elif self.protocol == PROTOCOL_KAFKA:
            self._start_kafka()
        elif self.protocol == PROTOCOL_REDIS:
            self._start_redis()
        elif self.protocol == PROTOCOL_ZENOH:
            self._start_zenoh()
        elif self.protocol == PROTOCOL_WEBSOCKET:
            self._start_websocket()
        elif self.protocol in [PROTOCOL_TCP, PROTOCOL_TCP_ALT]:
            self._start_tcp()
        else:
            raise ValueError(WARNING_UNSUPPORTED_PROTOCOL.format(self.protocol))

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
        broker = self.config[KEY_BROKER]
        port = self.config[KEY_PORT]
        self._mqtt_client.connect(broker, port, 60)
        self._mqtt_client.loop_start()

    def _start_rabbitmq(self):
        parameters = self.pika.ConnectionParameters(
            host=self.config[KEY_HOST],
            port=self.config[KEY_PORT]
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
        bootstrap_servers = self.config[KEY_BOOTSTRAP_SERVERS]
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
        host = self.config[KEY_HOST]
        port = self.config[KEY_PORT]
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
                    print(SOCKET_CLOSED_MESSAGE.format(e))
            self._consumer_thread = threading.Thread(target=listen, daemon=True)
            self._consumer_thread.start()

    def _start_zenoh(self):
        if self.zenoh is None:
            raise ImportError(ZENOH_IMPORT_ERROR)
        config = self.zenoh.Config()
        self._zenoh_session = self.zenoh.open(config)
        for topic in self.subscribe_topics:
            def zenoh_callback(sample, topic=topic):
                payload = sample.payload.decode() if isinstance(sample.payload, bytes) else sample.payload
                if topic in self.event_callbacks:
                    self.event_callbacks[topic](payload)
            self._zenoh_session.declare_subscriber(topic, zenoh_callback)

    def _start_websocket(self):
        ws_url = self.config[KEY_URL]
        def on_message(ws, message):
            if ":" in message:
                parts = message.split(":", 1)
                topic = parts[0].strip()
                payload = parts[1].strip()
                if topic in self.event_callbacks:
                    self.event_callbacks[topic](payload)
            else:
                for cb in self.event_callbacks.values():
                    cb(message)
        def on_error(ws, error):
            print(WS_ERROR_PREFIX, error)
        def on_close(ws, close_status_code, close_msg):
            print(WS_CLOSED_PREFIX, close_status_code, close_msg)
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
        host = self.config[KEY_HOST]
        port = self.config[KEY_PORT]
        self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_socket.connect((host, port))
        def listen_tcp():
            while True:
                try:
                    data = self._tcp_socket.recv(1024)
                    if not data:
                        break
                    message = data.decode().strip()
                    if ":" in message:
                        parts = message.split(":", 1)
                        topic = parts[0].strip()
                        payload = parts[1].strip()
                        if topic in self.event_callbacks:
                            self.event_callbacks[topic](payload)
                    else:
                        for cb in self.event_callbacks.values():
                            cb(message)
                except Exception as e:
                    print(TCP_RECEIVE_ERROR.format(e))
                    break
        self._tcp_thread = threading.Thread(target=listen_tcp, daemon=True)
        self._tcp_thread.start()

    def subscribe(self, topic, callback):
        """Register a callback for the given topic."""
        if topic not in self.subscribe_topics:
            self.subscribe_topics.append(topic)
        self.event_callbacks[topic] = callback

        if self.protocol == PROTOCOL_MQTT and self._mqtt_client:
            self._mqtt_client.subscribe(topic)
        elif self.protocol == PROTOCOL_RABBITMQ and self._rabbitmq_channel:
            self._rabbitmq_channel.queue_declare(queue=topic)
            def callback_wrapper(ch, method, properties, body, topic=topic):
                self.event_callbacks[topic](body.decode())
            self._rabbitmq_channel.basic_consume(queue=topic, on_message_callback=callback_wrapper, auto_ack=True)
        elif self.protocol == PROTOCOL_REDIS and self._redis_pubsub:
            self._redis_pubsub.subscribe(topic)
        elif self.protocol == PROTOCOL_ZENOH and self._zenoh_session:
            def zenoh_callback(sample, topic=topic):
                payload = sample.payload.decode() if isinstance(sample.payload, bytes) else sample.payload
                self.event_callbacks[topic](payload)
            self._zenoh_session.declare_subscriber(topic, zenoh_callback)
        # For Kafka, WebSocket, and TCP dynamic subscription is not handled

    def publish(self, topic, message=DEFAULT_PUBLISH_MESSAGE):
        """Publish a message to the specified topic."""
        if topic not in self.publish_topics:
            self.publish_topics.append(topic)
        if self.protocol == PROTOCOL_MQTT and self._mqtt_client:
            result = self._mqtt_client.publish(topic, message)
            return result
        elif self.protocol == PROTOCOL_RABBITMQ and self._rabbitmq_channel:
            self._rabbitmq_channel.queue_declare(queue=topic)
            self._rabbitmq_channel.basic_publish(exchange='', routing_key=topic, body=message)
            return f"Published to {topic}: {message}"
        elif self.protocol == PROTOCOL_KAFKA and self._kafka_producer:
            self._kafka_producer.send(topic, value=message.encode())
            self._kafka_producer.flush()
            return f"Published to {topic}: {message}"
        elif self.protocol == PROTOCOL_REDIS and self._redis_client:
            self._redis_client.publish(topic, message)
            return f"Published to {topic}: {message}"
        elif self.protocol == PROTOCOL_ZENOH and self._zenoh_session:
            self._zenoh_session.put(topic, message.encode())
            return f"Published to {topic}: {message}"
        elif self.protocol == PROTOCOL_WEBSOCKET and self._websocket_app:
            if self._websocket_app.sock and self._websocket_app.sock.connected:
                send_message = f"{topic}: {message}"
                self._websocket_app.send(send_message)
                return f"Published to {topic}: {message}"
            else:
                raise RuntimeError(WS_NOT_ESTABLISHED)
        elif self.protocol in [PROTOCOL_TCP, PROTOCOL_TCP_ALT] and self._tcp_socket:
            send_message = f"{topic}: {message}\n"
            self._tcp_socket.sendall(send_message.encode())
            return f"Published to {topic}: {message}"
        else:
            raise RuntimeError("Client not started or unsupported protocol for publishing.")

    def stop(self):
        """Stop the client and close any open connections."""
        if self.protocol == PROTOCOL_MQTT and self._mqtt_client:
            self._mqtt_client.loop_stop()
            self._mqtt_client.disconnect()
        elif self.protocol == PROTOCOL_RABBITMQ and self._rabbitmq_connection:
            self._rabbitmq_connection.close()
        elif self.protocol == PROTOCOL_KAFKA:
            if self._kafka_consumer:
                self._kafka_consumer.close()
        elif self.protocol == PROTOCOL_REDIS and self._redis_pubsub:
            self._redis_pubsub.close()
        elif self.protocol == PROTOCOL_ZENOH and self._zenoh_session:
            self._zenoh_session.close()
        elif self.protocol == PROTOCOL_WEBSOCKET and self._websocket_app:
            self._websocket_app.close()
            if self._websocket_thread:
                self._websocket_thread.join(timeout=1)
        elif self.protocol in [PROTOCOL_TCP, PROTOCOL_TCP_ALT] and self._tcp_socket:
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
    """Test a given protocol by subscribing and publishing on TEST_TOPIC."""
    print(f"\n--- Testing {protocol.upper()} ---")
    received_messages = []
    def callback(msg):
        print(f"[{protocol.upper()}] Received: {msg}")
        received_messages.append(msg)
    cm = CommunicationManager({KEY_PROTOCOL: protocol, **config})
    cm.subscribe(TEST_TOPIC, callback)
    cm.start()
    time.sleep(2)
    result = cm.publish(TEST_TOPIC, DEFAULT_PUBLISH_MESSAGE)
    print(result)
    time.sleep(2)
    cm.stop()
    return received_messages

if __name__ == "__main__":
    # Configuration for each protocol is defined in the main script.
    protocols_config = {
        # PROTOCOL_MQTT: {KEY_BROKER: "localhost", KEY_PORT: 1883},
        # PROTOCOL_RABBITMQ: {KEY_HOST: "localhost", KEY_PORT: 5672},
        # PROTOCOL_KAFKA: {KEY_BOOTSTRAP_SERVERS: "localhost:9092"}, #TODO: Add Kafka configuration, test the Kafka protocol
        PROTOCOL_REDIS: {KEY_HOST: "localhost", KEY_PORT: 6379},
        # PROTOCOL_ZENOH: {},  # Add Zenoh configuration if necessary TODO: Add Zenoh configuration, test the Zenoh protocol
        # PROTOCOL_WEBSOCKET: {KEY_URL: "ws://localhost:8765"},
        # PROTOCOL_TCP: {KEY_HOST: "localhost", KEY_PORT: 9000}
    }

    # # Start WebSocket and TCP echo servers for testing.
    # try:
    #     ws_server = start_ws_echo_server("localhost", 8765)
    #     time.sleep(1)
    # except Exception as e:
    #     print("WebSocket server failed to start:", e)
    #     protocols_config.pop(PROTOCOL_WEBSOCKET, None)

    # try:
    #     tcp_server = start_tcp_echo_server("localhost", 9000)
    #     time.sleep(1)
    # except Exception as e:
    #     print("TCP echo server failed to start:", e)
    #     protocols_config.pop(PROTOCOL_TCP, None)

    results = {}
    for proto, conf in protocols_config.items():
        msgs = test_communication_manager(proto, conf)
        results[proto] = msgs
        print(f"Test for {proto.upper()} received messages: {msgs}")

    print("\nFinal Results:", results)
