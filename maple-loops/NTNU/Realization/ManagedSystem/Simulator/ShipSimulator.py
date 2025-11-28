import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ship_maneuvering_model
import HydroPara_PI3_alternative1 as HydroPara_PI3
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import matplotlib
import random
matplotlib.use('TkAgg')

import json


# List of available models
available_models = ["ShipModel_M1", "ShipModel_M2", "ShipModel_M7", "ShipModel_M12", "ShipModel_MS"]

#RA probe and effector 
from rpio.clientLibraries.rpclpy.node import Node
import time 
class Probe(Node):
    def __init__(self, config ,verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "probe"
        self.logger.info("Probe instantiated")
        self.plant = True
        

class Effector(Node):
    def __init__(self, config ,verbose=True, plant = True):
        super().__init__(config=config,verbose=verbose)

        self._name = "effector"
        self.logger.info("effector instantiated")
        self.plant  = plant 


        #<!-- cc_init START--!>
        # user includes here
        #<!-- cc_init END--!>
    def effector(self, msg):
        self.plant  = False
        # self.plant.new_model = getattr(ship_maneuvering_model, msg)()    
        


    def register_callbacks(self):
        return super().register_event_callback(event_key="new_model", callback= self.effector)

def compare_trajectories(x, y, predicted_x, predicted_y):
    """
    Compare two trajectories given by x, y and predicted_x, predicted_y arrays,
    normalize the trajectories, and return a similarity score.

    Parameters:
        x: list or array of floats - Actual x coordinates
        y: list or array of floats - Actual y coordinates
        predicted_x: list or array of floats - Predicted x coordinates
        predicted_y: list or array of floats - Predicted y coordinates

    Returns:
        similarity_score: float - A score representing similarity (higher is better)
    """
    # Ensure all input arrays have the same length
    if len(x) != len(y) or len(y) != len(predicted_x) or len(predicted_x) != len(predicted_y):
        raise ValueError("All input arrays must have the same length")

    # Convert inputs to numpy arrays
    x = np.array(x)
    y = np.array(y)
    predicted_x = np.array(predicted_x)
    predicted_y = np.array(predicted_y)

    # Normalize the trajectories to fit in a unit square (0 to 1 range)
    def normalize(arr1, arr2):
        min_val = min(arr1.min(), arr2.min())  # Find the minimum value across both arrays
        max_val = max(arr1.max(), arr2.max())  # Find the maximum value across both arrays
        range_val = max_val - min_val         # Calculate the range
        if range_val == 0:                    # Handle edge case where all values are the same
            return arr1, arr2
        return (arr1 - min_val) / range_val, (arr2 - min_val) / range_val

    # Normalize x and predicted_x
    x, predicted_x = normalize(x, predicted_x)

    # Normalize y and predicted_y
    y, predicted_y = normalize(y, predicted_y)

    # Combine x and y into coordinate pairs
    actual = np.array(list(zip(x, y)))
    predicted = np.array(list(zip(predicted_x, predicted_y)))

    # Calculate Euclidean distances between corresponding points
    distances = np.linalg.norm(actual - predicted, axis=1)

    # Compute the similarity score (1 / (1 + average distance))
    average_distance = np.mean(distances)
    similarity_score = 1 / (1 + average_distance)  # Higher score means more similar

    return similarity_score

class ShipSim:
    def __init__(self, root):
        self.predicttion_model = "ShipModel_MS"
        self.predicttion_new_model = "ShipModel_MS"
        self.model = getattr(ship_maneuvering_model, self.predicttion_model)()
        self.new_model = getattr(ship_maneuvering_model, self.predicttion_new_model)()
        self.root = root
        self.root.title("Ship Trajectory Dashboard")
        self.root.geometry("800x600")
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.setup_gui()
        self.data = np.array 
        self.eta  = np.array
        self.nu = np.array
        self.file_path = ''
        self.probe = Probe(config='mape_config.yaml')
        self.probe.start()
        self.effector = Effector(config='mape_config.yaml')
        self.effector.effector = self.add_new_model
        self.effector.register_callbacks()
        self.effector.start()

    def setup_gui(self):
        animate_button = tk.Button(self.root, text="Animate Ship", command=self.animate_file)
        animate_button.pack(side = "left", padx=30, pady=5)

        select_button = tk.Button(self.root, text="New Model", command=self.predict_botton, justify= "left")
        select_button.pack(side = "left", padx=30, pady=5)

        anomaly_button = tk.Button(self.root, text="Anomaly Detection", command=self.anomaly_detection)
        anomaly_button.pack(side = "left", padx=30, pady=5)

        accept_model_button = tk.Button(self.root, text="Accept New Model", command=self.accept_new_model)
        accept_model_button.pack(side = "left", padx=30, pady=5)

        generate_model_button = tk.Button(self.root, text="Decline New Model", command=self.decline_new_model)
        generate_model_button.pack(side = "left", padx=30, pady=5)


    def load_data(self, file, U0):
        df = pd.read_csv(file)
        df['Surge Speed'] = df['Surge Speed'] - U0
        return df

    def predict_trajectory(self, df):
        eta, nu = self.model.predict(
            HydroPara_PI3,
            df['Surge Speed'][0],
            df['Sway Speed'][0],
            df['Yaw Rate'][0],
            df['Heading'][0],
            df['x'][0],
            df['y'][0],
            df['Rudder Angle'],
            df['Wind Direction'],
            df['Wind Speed']
        )
        return eta, nu
        
    def new_predict_trajectory(self, df):
        eta, nu = self.new_model.predict(
            HydroPara_PI3,
            df['Surge Speed'][0],
            df['Sway Speed'][0],
            df['Yaw Rate'][0],
            df['Heading'][0],
            df['x'][0],
            df['y'][0],
            df['Rudder Angle'],
            df['Wind Direction'],
            df['Wind Speed']
        )
        return eta, nu


    def animate_ship(self, data):
        x = data['x'].values
        y = data['y'].values
        heading = data['Heading'].values
        
        fig, ax = plt.subplots()
        ax.set_xlim(min(x), max(x))
        x_scale = max(x) - min(x)
        ax.set_ylim(min(y), max(y))
        y_scale = max(y) - min(y)
        ax.set_xlabel('x [m] - East')
        ax.set_ylabel('y [m] - North')


        def update(frame_num):
            ax.clear()
            ship_width, ship_length = int(x_scale/30), int(y_scale/30)
            ship = Rectangle((x[0] - ship_width / 2, y[0] - ship_length / 2), ship_width, ship_length, angle=heading[0], color='darkblue')
            window = Rectangle((x[0], y[0]), ship_width/10, ship_length, color="green")
            ax.add_patch(ship)
            ax.add_patch(window)
            window_size = 300
            ship.set_xy([x[frame_num] - ship_width / 2, y[frame_num] - ship_length / 2])
            window.set_xy([x[frame_num+window_size] - ship_width / 2, y[frame_num+window_size] - ship_length / 2])
            ax.plot(x, y, label='Current Trajectory')
            _data = self.data
            shifted_data = _data.shift(-frame_num)
            self.eta, self.nu = self.predict_trajectory(shifted_data)
            ax.plot(self.eta[:, 0], self.eta[:, 1], 'r--', label='Currecnt Prediction:'+ self.predicttion_model)
            self.probe.publish_event(event_key='ship_status', message= json.dumps({'ship_prediction_model':self.predicttion_model, 'surge_speed':shifted_data['Surge Speed'][0],
            'sway_speed':shifted_data['Sway Speed'][0],
            'yaw_rate': shifted_data['Yaw Rate'][0],
            'heading': shifted_data['Heading'][0],
            'x': shifted_data['x'].to_list(),
            'y': shifted_data['y'].to_list()}))
            self.probe.publish_event(event_key='weather_condition', message= json.dumps({'rudder_angle': shifted_data['Rudder Angle'].tolist(),
            'wind_direction': shifted_data['Wind Direction'].tolist(),
            'wind_speed':shifted_data['Wind Speed'].tolist()}))  

            score = compare_trajectories(shifted_data['x'][0 : window_size],shifted_data['y'][0 : window_size],self.eta[0 : window_size, 0], self.eta[0 : window_size, 1]  ) 
            if self.predicttion_model != self.predicttion_new_model:
                _eta, _nu = self.new_predict_trajectory(shifted_data)
                ax.plot(_eta[:, 0], _eta[:, 1], 'g--', label='New Prediction:'+ self.predicttion_new_model)
                ax.set_title(f"{self.predicttion_model} -> {self.predicttion_new_model}")
            else: 
                ax.set_title(f"{self.predicttion_model}, score:{score: .3f}")
            fig.legend(loc = "lower left")
            fig.canvas.draw()
            return ship

        ani = animation.FuncAnimation(fig, update, frames=len(x), interval=1000, blit=False)

        # Embed the animation in the tkinter window
        for widget in self.frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Keep a reference to the animation to prevent it from being garbage collected
        self.frame.ani = ani

    def predict_botton(self):

        try:
            # df = self.load_data(self.file_path, self.model.U0)
            # messagebox.showinfo("go to ->"+ self.predicttion_new_model)
            self.predicttion_new_model= random.choice(available_models)
            self.add_new_model(self.predicttion_new_model) 
            
        #     # self.make_plots(self.data, eta, nu)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def add_new_model(self, model):
        print(f"new_mdoel is {model}")
        self.predicttion_new_model = model
        self.new_model = getattr(ship_maneuvering_model, model)()   

    def anomaly_detection(self):
        messagebox.showinfo("Anomaly Detection", "Anomaly detection functionality is not yet implemented.")

    def accept_new_model(self):
        self.predicttion_model = self.predicttion_new_model
        self.model = getattr(ship_maneuvering_model, self.predicttion_model)()  
        # messagebox.showinfo("Accept New Model", "Accepting the new model functionality is not yet implemented.")

    def decline_new_model(self):
        self.predicttion_new_model = self.predicttion_model

    def animate_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            try:
                self.data = self.load_data(self.file_path, self.model.U0)
                self.animate_ship(self.data)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShipSim(root)
    root.mainloop()

