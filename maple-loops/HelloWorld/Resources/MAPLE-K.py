import tkinter as tk
from tkinter import Canvas
import paho.mqtt.client as mqtt
import time

# MQTT Settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPICS = ["new_data", "anomaly", "new_plan", "is_legit", "/spin_config"]

# State Definitions
STATE_COLORS = {
    "new_data": "lightblue",
    "anomaly": "lightgreen",
    "new_plan": "lightyellow",
    "legitimate": "lightpink",
    "spin_config": "lightcoral"
}

class MAPEKDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("MAPE-K Loop Dashboard")
        self.canvas = Canvas(root, width=1000, height=200)
        self.canvas.pack()

        # Create components visualization
        self.state_rects = {}
        self.create_state_machine_visuals()

        # MQTT Client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()

        # Initialize active state
        self.active_state = None
        self.set_active_state("monitor")

    def create_state_machine_visuals(self):
        # Coordinates for horizontal layout
        x, y = 50, 50
        gap = 150
        states = list(STATE_COLORS.keys())

        for state in states:
            rect = self.canvas.create_rectangle(
                x, y, x + 100, y + 60, fill="white", outline="black", width=2
            )
            text = self.canvas.create_text(
                x + 50, y + 30, text=state.capitalize(), font=("Helvetica", 16)
            )
            self.state_rects[state] = (rect, text)
            x += gap

    def set_active_state(self, state):
        # Reset colors of all states
        for key, (rect, _) in self.state_rects.items():
            self.canvas.itemconfig(rect, fill="white")

        # Highlight active state
        if state in self.state_rects:
            rect, _ = self.state_rects[state]
            self.canvas.itemconfig(rect, fill=STATE_COLORS[state])
            self.active_state = state

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        for topic in MQTT_TOPICS:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        print(f"Received message on topic {msg.topic}")
        state = msg.topic.split("/")[-1]
        self.set_active_state(state)

if __name__ == "__main__":
    root = tk.Tk()
    dashboard = MAPEKDashboard(root)
    root.mainloop()
