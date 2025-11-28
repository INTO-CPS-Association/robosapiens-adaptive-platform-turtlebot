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

class Legitimate(Node):

    def __init__(self, config='config.yaml',verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "Legitimate"
        self.logger.info("Legitimate instantiated")

        #<!-- cc_init START--!>
        # user includes here
        #<!-- cc_init END--!>

    # -----------------------------AUTO-GEN SKELETON FOR legitimize-----------------------------
    def legitimize(self,msg):

        #<!-- cc_code_legitimize START--!>

        # user code here for legitimize


        #<!-- cc_code_legitimize END--!>

        # TODO: Put desired publish event inside user code and uncomment!!
        #self.publish_event(event_key='isLegit')    # LINK <outport> isLegit

    def register_callbacks(self):
        self.register_event_callback(event_key='new_plan', callback=self.legitimize)     # LINK <eventTrigger> new_plan
        self.register_event_callback(event_key='new_plan', callback=self.legitimize)        # LINK <inport> new_plan

def main(args=None):

    node = Legitimate(config='config.yaml')
    node.register_callbacks()
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()