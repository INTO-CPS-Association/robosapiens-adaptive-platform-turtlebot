# **********************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>
# *
# * This file is part of the roboarch R&D project.
# *
# * RAP R&D concepts can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **********************************************************************************
from rpio.clientLibraries.rpclpy.node import Node
import json
import time

#<!-- cc_include END--!>

#<!-- cc_code START--!>

### USER Defined Functions

#<!-- cc_code END--!>

class Trustworthiness(Node):

    def __init__(self, config='config.yaml',verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "Trustworthiness"
        self.logger.info("Trustworthiness instantiated")

        #<!-- cc_init START--!>



        #<!-- cc_init END--!>

    # -----------------------------AUTO-GEN SKELETON FOR planner-----------------------------
    def t_a(self,msg):
        self.publish_event("stage", json.dumps({'Str':'m'}))
        time.sleep(0.1)
        self.publish_event("stage", json.dumps({'Str': 'a'}))

    def t_p(self, msg):
        self.publish_event("stage", json.dumps({'Str': 'p'}))
    def t_l(self, msg):
        self.publish_event("stage", json.dumps({'Str': 'l'}))
    def t_e(self, msg):
        self.publish_event("stage", json.dumps({'Str': 'e'}))

    def trust_check(self, msg):
        self.logger.info(msg)

    def register_callbacks(self):
        self.register_event_callback(event_key='anomaly', callback=self.t_a)     # LINK <eventTrigger> anomaly
        self.register_event_callback(event_key='new_plan', callback=self.t_p)
        self.register_event_callback(event_key='isLegit', callback=self.t_l)
        self.register_event_callback(event_key='/spin_config', callback=self.t_e)
        self.register_event_callback(event_key='maple', callback=self.trust_check)
        # self.register_event_callback(event_key='anomaly', callback=self.planner)        # LINK <inport> anomaly

def main(args=None):

    node = Trustworthiness(config='config.yaml')
    node.register_callbacks()
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()