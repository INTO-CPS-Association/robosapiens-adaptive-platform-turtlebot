import time
import threading
import json
import numpy as np
import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import messagebox
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from rpclpy.CommunicationManager import CommunicationManager

# MQTT setup
MQTT_BROKER = "localhost"
POSE_TOPIC = "/pose"
SCAN_TOPIC = "/Scan"
SPIN_CONFIG_TOPIC = "/spin_config"

# TurtleBotSim class
class TurtleBotSim:
    def __init__(self):
        self.position = [0, 0]
        self.angle = 1.0
        self.heading = 0
        self.lidar_occluded = False
        self.standard_navigation = True
        self.map_size = 10
        self.obstacles = self.generate_obstacles()
        self.trajectory = []
        self.lidar_data = [random.uniform(5, 10) for _ in range(360)]
        
    def generate_obstacles(self, num_obstacles=5):
        obstacles = []
        for _ in range(num_obstacles):
            obstacles.append((random.uniform(-self.map_size, self.map_size), random.uniform(-self.map_size, self.map_size)))
        return obstacles
    
    def publish_pose(self):
        client.publish(POSE_TOPIC, json.dumps({"x": self.position[0], "y": self.position[1], "angle": self.angle}))

    def publish_scan(self):
        if self.lidar_occluded:
            self.lidar_data[0:300] = [float('inf') for _ in range(300)]
        else:
            self.lidar_data = [random.uniform(5, 10) for _ in range(360)]
        lidar_data = {
            'angle_min':-3.124,
            'angle_max': 3.1415927,
            'angle_increment': 0.0174533,
            'scan_time': 0.2,
            'range_min': 0.1,
            'range_max': 12.0,
            'ranges': self.lidar_data
            # 'intensities': list(msg.intensities)
        }
        client.publish(SCAN_TOPIC, json.dumps(lidar_data))

    def navigate_to(self, trajectory):
        self.trajectory = trajectory
        for point in trajectory:
            self.heading = np.atan2(point[1]-self.position[1],(point[0]-self.position[0]))
            self.position = point
            if (self.standard_navigation):
                self.publish_pose()
                self.publish_scan()
                time.sleep(0.5)
            else:
                self.publish_pose()
                self.publish_scan()
                time.sleep(0.5)
                self.heading = self.heading + self.angle
                self.publish_pose()
                self.publish_scan()
                time.sleep(0.5)
                self.heading = self.heading -self.angle
                self.publish_pose()
                self.publish_scan()
                time.sleep(0.5)

    def spin(self, duration, angle):
        self.angle += angle
        self.publish_pose()
        time.sleep(duration)

# A* Pathfinding (Simple Implementation)
def astar(start, end, obstacles):
    # Placeholder for A*; generates a straight path from start to end avoiding obstacles.
    path = []
    steps = 20
    x_vals = np.linspace(start[0], end[0], steps)
    y_vals = np.linspace(start[1], end[1], steps)
    for i in range(steps):
        path.append([x_vals[i], y_vals[i]])
    return path

# GUI Setup using Tkinter
sim = TurtleBotSim()
root = tk.Tk()
root.title("TurtleBot4 Simulation Dashboard")
# Configure the main window grid
root.rowconfigure(0, weight=1)  # Row for the canvas
root.rowconfigure(1, weight=0)  # Row for buttons
root.columnconfigure(0, weight=1)  # Single column layout

# Create Matplotlib Figure
fig, (ax, ax_lidar) = plt.subplots(1, 2, figsize=(10, 5))
ax_lidar = plt.subplot(1, 2, 2, polar=True)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack


# Update Map Visualization
def update_map():
    ax.clear()
    # Plot TurtleBot position and heading
    ax.plot(sim.position[0], sim.position[1], 'bo', markersize=10, label='TurtleBot4')
    heading_x = sim.position[0] + 1 * np.cos(sim.heading)
    heading_y = sim.position[1] + 1 * np.sin(sim.heading)
    ax.arrow(sim.position[0], sim.position[1], heading_x - sim.position[0], heading_y - sim.position[1], head_width=0.5, head_length=0.5, fc='blue', ec='blue')
    
    # Plot trajectory
    if sim.trajectory:
        trajectory_x = [point[0] for point in sim.trajectory]
        trajectory_y = [point[1] for point in sim.trajectory]
        ax.plot(trajectory_x, trajectory_y, 'g--', label='Trajectory')
    
    # Plot obstacles
    for ob in sim.obstacles:
        ax.plot(ob[0], ob[1], 'ro', markersize=10, label='Obstacle')
    
    ax.set_xlim([-sim.map_size, sim.map_size])
    ax.set_ylim([-sim.map_size, sim.map_size])
    ax.set_title("TurtleBot4 Map")
    ax.legend()
    
    # Plot Lidar data in polar form
    ax_lidar.clear()
    angles = np.linspace(0, 2 * np.pi, len(sim.lidar_data))
    ax_lidar.plot(angles, sim.lidar_data, 'r-')
    ax_lidar.set_title("Lidar Data")
    ax_lidar.set_ylim([0, 10])

    canvas.draw()

# Click event to navigate TurtleBot
def on_click(event):
    target_coords = (event.xdata, event.ydata)
    if target_coords is not None:
        trajectory = astar(sim.position, target_coords, sim.obstacles)
        threading.Thread(target=sim.navigate_to, args=(trajectory,)).start()
        update_map()

fig.canvas.mpl_connect('button_press_event', on_click)

# Lidar Toggle Button
def toggle_lidar():
    sim.lidar_occluded = not sim.lidar_occluded
    status = "ON" if sim.lidar_occluded else "OFF"
    messagebox.showinfo("Lidar Occlusion", f"Lidar Occlusion is now {status}")
    update_map()

lidar_button = tk.Button(root, text="Toggle Lidar Occlusion", command=toggle_lidar)
# lidar_button.pack()
lidar_button.grid(row=1, column=0, sticky="ew", padx=300, pady=5)
# Lidar Toggle Button
def toggle_NAV2():
    sim.standard_navigation = not sim.standard_navigation
    status = "STANDARD" if sim.standard_navigation else "SPIN_CONFIG"
    messagebox.showinfo("Navigation Changed", f"Navigation method is now {status}")
    update_map()

NAV2_button = tk.Button(root, text="Toggle NAV2", command=toggle_NAV2)
# NAV2_button.pack()
NAV2_button.grid(row=2, column=0, sticky="ew", padx=300, pady=5)  # Expand horizontally
# MQTT Spin Command Listener
def on_message(message):
    try:
        payload = json.loads(message)
        if payload.get("commands") :
            plan = payload.get("commands")[0]
            duration = plan.get("duration")
            if duration == 0.0:
                sim.standard_navigation = True
            else:
                sim.standard_navigation = False
                sim.angle = plan.get("omega", 90)
            # threading.Thread(target=sim.spin, args=(duration, angle)).start()
            update_map()
    except json.JSONDecodeError:
        sim.standard_navigation = True
        print("Invalid JSON in spin config")



def stop_periodic_update():
    # Cancel any pending 'after' events
    print("closing the program")
    root.after_cancel(periodic_update_id)
    client.stop()
    root.quit()
    root.destroy()

# Update Map periodically
def periodic_update():
    global periodic_update_id
    update_map()
    periodic_update_id = root.after(1000, periodic_update)



if __name__ == "__main__":
    client = CommunicationManager({"protocol":"mqtt", "broker": "localhost", "port": 1883})
    # client = communication_manager = CommunicationManager("rabbitmq", {"host": "localhost", "port": 5672})
    # client = CommunicationManager({"protocol":"redis", "host": "localhost", "port": 6379})
    client.subscribe(SPIN_CONFIG_TOPIC, callback=on_message)
    # client.on_message = on_message
    client.start()
    periodic_update()
    # Bind the window close event to stop the periodic update
    root.protocol("WM_DELETE_WINDOW", stop_periodic_update)
    root.mainloop()
