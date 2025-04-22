# **********************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>
# *
# * This file is part of the roboarch R&D project.
# *
# * RAP R&D concepts can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **********************************************************************************
from rpclpy.node import Node
from .messages import *
import time
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

        _laser_scan = json_to_object(msg, LaserScan)
        json_message = json.loads(msg)
        _laser_scan._ranges = json_message['ranges']

        #<!-- cc_code_monitor_data END--!>

        # _success = self.knowledge.write(cls=_LaserScan)
        self.write_knowledge("laser_scan",msg)
        #use the bellew
        self.write_knowledge(_laser_scan)
        
        self.publish_event(NewData)

    def register_callbacks(self):
        self.register_event_callback(event_key='/Scan', callback=self.monitor_data)     # LINK <eventTrigger> Scan

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