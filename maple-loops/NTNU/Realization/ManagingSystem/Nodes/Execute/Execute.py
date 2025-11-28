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

class Execute(Node):

    def __init__(self, config='config.yaml',verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "Execute"
        self.logger.info("Execute instantiated")

        #<!-- cc_init START--!>
        # user includes here
        #<!-- cc_init END--!>

    # -----------------------------AUTO-GEN SKELETON FOR executer-----------------------------
    def executer(self,msg):
        isLegit = self.knowledge.read("isLegit",queueSize=1)
        Model = self.knowledge.read("Model",queueSize=1)

        #<!-- cc_code_executer START--!>
        # del(_Model)
        # _Model = Model["ship_prediction_model"]
        self.publish_event(event_key='new_model', message=Model["ship_prediction_model"])
        #<!-- cc_code_executer END--!>

        # TODO: Put desired publish event inside user code and uncomment!!
        #self.publish_event(event_key='new_model')    # LINK <outport> new_model

    def register_callbacks(self):
        self.register_event_callback(event_key='new_plan', callback=self.executer)     # LINK <eventTrigger> new_plan
        self.register_event_callback(event_key='isLegit', callback=self.executer)        # LINK <inport> isLegit

def main(args=None):

    node = Execute(config='config.yaml')
    node.register_callbacks()
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()