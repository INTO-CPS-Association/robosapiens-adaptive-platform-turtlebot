# **********************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>
# *
# * This file is part of the roboarch R&D project.
# *
# * RAP R&D concepts can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **********************************************************************************
from rpio.clientLibraries.rpclpy.node import Node
import time

try:
    from .messages import *
except (ValueError, ImportError):
    from messages import *

#<!-- cc_include START--!>
try:
    import NTNU.Realization.ManagingSystem.Nodes.Analysis.ship_maneuvering_model as ship_maneuvering_model
except(ValueError, ImportError):
    import ship_maneuvering_model as ship_maneuvering_model
import numpy as np
#<!-- cc_include END--!>

#<!-- cc_code START--!>
class HydroPara_PI3():
    def get_X(u, v, r, d, U, L):
        X = np.array((u * U, u ** 2, (u ** 3) / U, v ** 2, (L ** 2) * r ** 2, r * v * L,
                      (U ** 2) * d ** 2, U * u * d ** 2, U * v * d, u * v * d))
        return X


    def get_Y(u, v, r, d, U, L):
        Y = np.array((v * U, U * r * L, (v ** 3) / U, (r * L * v ** 2) / U, v * u,
                      r * L * u, (U ** 2) * d, (U ** 2) * d ** 3, u * U * d, d * u ** 2, U * v * d ** 2,
                      d * v ** 2, U ** 2, U * u, u ** 2))
        return Y


    def get_N(u, v, r, d, U, L):
        N = np.array((v * U, U * r * L, (v ** 3) / U, (r * L * v ** 2) / U, v * u,
                      r * L * u, (U ** 2) * d, (U ** 2) * d ** 3, u * U * d, d * u ** 2, U * v * d ** 2,
                      d * v ** 2, U ** 2, U * u, u ** 2))
        return N

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
#<!-- cc_code END--!>

class Analysis(Node):

    def __init__(self, config='config.yaml',verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "Analysis"
        self.logger.info("Analysis instantiated")

        #<!-- cc_init START--!>
        self.anomaly = False
        self.ship_model = None
        
        #<!-- cc_init END--!>

    # -----------------------------AUTO-GEN SKELETON FOR analyse_trajectory_prediction-----------------------------
    def analyse_trajectory_prediction(self,msg):
        ShipStatus = self.knowledge.read("ShipStatus",queueSize=1)
        WeatherCondition = self.knowledge.read("WeatherCondition",queueSize=1)

        #<!-- cc_code_analyse_trajectory_prediction START--!>
        self.ship_model = getattr(ship_maneuvering_model,ShipStatus["ship_prediction_model"])()
        eta, nu =self.ship_model.predict(HydroPara_PI3,
            ShipStatus['surge_speed'],
            ShipStatus['sway_speed'],
            ShipStatus['yaw_rate'],
            ShipStatus['heading'],
            ShipStatus['x'][0],
            ShipStatus['y'][0],
            WeatherCondition['rudder_angle'],
            WeatherCondition['wind_direction'],
            WeatherCondition['wind_speed'])
        window_size = 300 # 60 sample equals to 1 minute       
        score = compare_trajectories(ShipStatus['x'][0 : window_size],ShipStatus['y'][0 : window_size],eta[0 : window_size, 0], eta[0 : window_size, 1]  ) 
        # Set the monitor status to mark an anomaly if the there is any

        # # occlusion outside of the ignored region
        anomaly_status_old = self.anomaly
        if score: 
            if score > 0.97 : 
                self.anomaly = False
                self.logger.info(f" Anomaly: {self.anomaly}, similarity score is:{score}")
            else: 
                self.anomaly = True
                self.logger.info(f" Anomaly: {self.anomaly}, similarity score is:{score}")
            if anomaly_status_old != self.anomaly:
                if (self.anomaly == True):
                    self.publish_event(event_key='anomaly')



        #<!-- cc_code_analyse_trajectory_prediction END--!>

        # TODO: Put desired publish event inside user code and uncomment!!
        #self.publish_event(event_key='anomaly')    # LINK <outport> anomaly

    def register_callbacks(self):
        self.register_event_callback(event_key='new_data', callback=self.analyse_trajectory_prediction)     # LINK <eventTrigger> new_data

def main(args=None):

    node = Analysis(config='config.yaml')
    node.register_callbacks()
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()