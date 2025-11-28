# **********************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>
# *
# * This file is part of the roboarch R&D project.
# *
# * RAP R&D concepts can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **********************************************************************************
from rpio.clientLibraries.rpclpy.node import Node
from .messages import *
import time
#<!-- cc_include START--!>
import json
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
    # -----------------------------AUTO-GEN SKELETON FOR executer-----------------------------
    def legitimate(self,msg):
        isLegit = self.knowledge.read("isLegit",queueSize=1)
        directions = self.knowledge.read("directions",queueSize=1)
        _Direction = Direction()

        #<!-- cc_code_executer START--!>

        # user code here for executer


        #<!-- cc_code_executer END--!>
        for i in range(1):
            self.logger.info("Legitimating")
            time.sleep(0.1)
        self.publish_event(event_key='isLegit')    # LINK <outport> spin_config

    def register_callbacks(self):
        self.register_event_callback(event_key='new_plan', callback=self.legitimate)        # LINK <inport> new_plan

def main(args=None):

    node = Legitimate(config='config.yaml')
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()