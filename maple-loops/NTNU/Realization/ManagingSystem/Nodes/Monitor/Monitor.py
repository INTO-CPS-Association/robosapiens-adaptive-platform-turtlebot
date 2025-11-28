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
import json
#<!-- cc_include END--!>

#<!-- cc_code START--!>
# user code here
#<!-- cc_code END--!>

class Monitor(Node):

    def __init__(self, config='config.yaml',verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "Monitor"
        self.logger.info("Monitor instantiated")

        #<!-- cc_init START--!>
        # user includes here
        #<!-- cc_init END--!>

    # -----------------------------AUTO-GEN SKELETON FOR monitor_ship-----------------------------
    def monitor_ship(self,msg):
        _ShipStatus = ShipStatus()

        #<!-- cc_code_monitor_ship START--!>

        # user code here for monitor_ship
        
        # Fill the class instance properties
        msg_dict = json.loads(msg)
        for key, value in msg_dict.items():
            # Prepend an underscore to match class properties
            underscore_key = f"_{key}"
            if hasattr(_ShipStatus, underscore_key):
                setattr(_ShipStatus, underscore_key, value)
        # _ShipStatus._ship_prediction_model= "SET VALUE"    # datatype: string
        # _ShipStatus._surge_speed= "SET VALUE"    # datatype: Float_64
        # _ShipStatus._sway_speed= "SET VALUE"    # datatype: Float_64
        # _ShipStatus._yaw_rate= "SET VALUE"    # datatype: Float_64
        # _ShipStatus._heading= "SET VALUE"    # datatype: Float_64
        # _ShipStatus._x= "SET VALUE"    # datatype: Array
        # _ShipStatus._y= "SET VALUE"    # datatype: Array
        self.publish_event(event_key='new_data')
        #<!-- cc_code_monitor_ship END--!>

        _success = self.knowledge.write(cls=_ShipStatus)
        # TODO: Put desired publish event inside user code and uncomment!!
        #self.publish_event(event_key='new_data')    # LINK <outport> new_data
    # -----------------------------AUTO-GEN SKELETON FOR monitor_weather-----------------------------
    def monitor_weather(self,msg):
        _WeatherCondition = WeatherCondition()

        #<!-- cc_code_monitor_weather START--!>

        # user code here for monitor_weather
        msg_dict = json.loads(msg)
        for key, value in msg_dict.items():
            # Prepend an underscore to match class properties
            underscore_key = f"_{key}"
            if hasattr(_WeatherCondition, underscore_key):
                setattr(_WeatherCondition, underscore_key, value)
        # _WeatherCondition._rudder_angle= "SET VALUE"    # datatype: Array
        # _WeatherCondition._wind_direction= "SET VALUE"    # datatype: Array
        # _WeatherCondition._wind_speed= "SET VALUE"    # datatype: Array

        #<!-- cc_code_monitor_weather END--!>

        _success = self.knowledge.write(cls=_WeatherCondition)
        # TODO: Put desired publish event inside user code and uncomment!!

    def register_callbacks(self):
        self.register_event_callback(event_key='ship_status', callback=self.monitor_ship)     # LINK <eventTrigger> ship_status
        self.register_event_callback(event_key='weather_condition', callback=self.monitor_weather)     # LINK <eventTrigger> weather_condition

def main(args=None):

    node = Monitor(config='config.yaml')
    node.register_callbacks()
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()