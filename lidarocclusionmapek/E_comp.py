# **********************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>
# *
# * This file is part of the roboarch R&D project.
# *
# * RAP R&D concepts can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **********************************************************************************
from RoboSapiensAdaptivePlatform.utils.nodes import TriggeredNode
from RoboSapiensAdaptivePlatform.Communication.Messages.messages import ComponentStatus
from RoboSapiensAdaptivePlatform.utils.constants import *

from RoboSapiensAdaptivePlatform.utils.CommunicationInterfaces import MQTTInterface
import json

class Execute(TriggeredNode):

    def __init__(self, logger = None,knowledgeBase = None,adaptationManagement = None, verbose=False):
        super().__init__(logger=logger,knowledge = knowledgeBase,verbose=verbose)

        self._name = 'execute'
        self._adaptationManagement = adaptationManagement

    # ------------------------------------------------------------------------------------------------
    # -------------------------------------INTERNAL FUNCTIONS----------------------------------------
    # ------------------------------------------------------------------------------------------------
    def _SpinOnceFcn(self, args):

        # TODO: implement execute component
        _status = executeStatus.IDLE
        _accuracy = 1.0

        self.logger.log("[" + self._name + "] - " + "entered execute")

        # # 1. CHECK FOR ACTIVE DIAGNOSIS/ADAPTATION PLAN FROM KB
        # _diagnosePlan, historyD = self.knowledge.read(actionType.DIAGNOSISTYPE, 1)
        # _adaptationPlan, historyA = self.knowledge.read(actionType.ADAPTATIONTYPE, 1)
        # # 2. EXECUTE PLAN
        # if _diagnosePlan != -1:
        #     self.logger.log("[" + self._name + "] - " + "Diagnose action registered to adaptation management")
        #     self._adaptationManagement.performDiagnosis(_diagnosePlan)
        # elif _adaptationPlan != -1:
        #     self.logger.log("[" + self._name + "] - " + "Adaptation action registered to adaptation management")
        #     self._adaptationManagement.performAdaptation(_adaptationPlan)

        directions, _ = self.knowledge.read("directions", 1)

        self.logger.log("[" + self._name + "] - " + "Executing plan: " + str(directions))
        # Directly create an MQTT client to send the plan to the robot
        # This is a temporary hack until the action-based interface is properly
        # implemented
        client = MQTTInterface('hackmqtt')
        client.start()
        client.push('/spin_config',
                    json.dumps({'commands': directions, 'period': 8}))
        self.logger.log("[" + self._name + "] - " + "Plan executed")
        del client

        _status = executeStatus.EXECUTION

        # x. SIGNAL EXECUTE STATE VIA KNOWLEDGE
        self.RaPSignalStatus(component=adaptivityComponents.EXECUTE,status=_status,accuracy=_accuracy)

        # y. return status of execution (fail = False, success = True)
        return True


    def _EnterInitializationModeFcn(self):
        if self._verbose: print("Enter initializationModeFcn not implemented")

    def _ExitInitializationModeFcn(self):
        # initial signal after startup
        self.RaPSignalStatus(component=adaptivityComponents.MONITOR,status=monitorStatus.NORMAL,accuracy=1.0)

    def _EnterConfigurationModeFcn(self):
        if self._verbose: print("Enter configurationModeFcn not implemented")

