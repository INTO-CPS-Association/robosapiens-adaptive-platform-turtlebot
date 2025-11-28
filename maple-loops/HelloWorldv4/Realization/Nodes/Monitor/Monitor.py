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
# user includes here
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

    # -----------------------------AUTO-GEN SKELETON FOR monitor_data-----------------------------
    def monitor_data(self,msg):
        _LaserScan = LaserScan()

        #<!-- cc_code_monitor_data START--!>

        # user code here for monitor_data

        _LaserScan._ranges= "SET VALUE"    # datatype: Array
        _LaserScan._angle_increment= "SET VALUE"    # datatype: Float_64

        #<!-- cc_code_monitor_data END--!>

        _success = self.knowledge.write(cls=_LaserScan)
        # TODO: Put desired publish event inside user code and uncomment!!
        #self.publish_event(event_key='new_data')    # LINK <outport> new_data

    def register_callbacks(self):
        self.register_event_callback(event_key='Scan', callback=self.monitor_data)     # LINK <eventTrigger> Scan

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