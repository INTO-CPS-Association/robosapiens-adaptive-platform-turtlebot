from rpio.clientLibraries.rpclpy.node import Node
from messages import *
import time
#<!-- cc_include START--!>
from fractions import Fraction
from .lidarocclusion.masks import BoolLidarMask
from .lidarocclusion.sliding_lidar_masks import sliding_lidar_mask, sliding_prob_lidar_mask
from typing import List, Tuple, Dict
import traceback
import json
import numpy as np
import pickle
import portion



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

        # _success = self.knowledge.write(cls=_LaserScan)
        self.knowledge.write("laser_scan",msg)
        self.publish_event(event_key='new_data')    # LINK <outport> new_data

    def register_callbacks(self):
        self.register_event_callback(event_key='/Scan', callback=self.monitor_data)     # LINK <eventTrigger> Scan



#<!-- cc_code START--!>
# Probability threshold for detecting a lidar occlusion
OCCLUSION_THRESHOLD = 0.3
# Number of scans to use for the sliding window
SLIDING_WINDOW_SIZE = 3
# Lidar mask sensitivity (ignore small occlusions below this angle)
OCCLUSION_SENSITIVITY = Fraction(1, 48)

# user defined!
def lidar_mask_from_scan(scan) -> BoolLidarMask:
    scan_ranges = np.array(scan.get("ranges"))
    return BoolLidarMask(
        (scan_ranges != np.inf) & (scan_ranges != -np.inf),
        base_angle=Fraction(2, len(scan.get("ranges"))),
        # base_angle=scan.angleIncrement/180,
    )#<!-- cc_code END--!>

class Analysis(Node):

    def __init__(self, config='config.yaml',verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "Analysis"
        self.logger.info("Analysis instantiated")

        #<!-- cc_init START--!>
        self._scans = []
        self.anomaly = False

        def scans():
            while True:
                for scan in self._scans:
                    yield scan

                self._scans = []

        def raw_lidar_masks():
            for scan in scans():
                yield lidar_mask_from_scan(scan)

        self._sliding_prob_lidar_masks = sliding_prob_lidar_mask(
            raw_lidar_masks(),
            window_size=SLIDING_WINDOW_SIZE,
        )
        #<!-- cc_init END--!>

    # -----------------------------AUTO-GEN SKELETON FOR analyse_scan_data-----------------------------
    def analyse_scan_data(self,msg):
        laser_scan = self.knowledge.read("laser_scan",queueSize=1)

        #<!-- cc_code_analyse_scan_data START--!>

        self.lidar_data = laser_scan
        self.logger.info(f"REtrieved laser_scan: {self.lidar_data}")

        self._scans.append(self.lidar_data)
        prob_lidar_mask = next(self._sliding_prob_lidar_masks)
        prob_lidar_mask = prob_lidar_mask.rotate(-Fraction(1, 2))

        lidar_mask = (prob_lidar_mask >= OCCLUSION_THRESHOLD)
        # Weaken lidar masks to threshold
        lidar_mask = lidar_mask.weaken(OCCLUSION_SENSITIVITY)
        lidar_mask = lidar_mask.weaken(-OCCLUSION_SENSITIVITY)
        lidar_mask = lidar_mask.strengthen(OCCLUSION_SENSITIVITY)
        lidar_mask = lidar_mask.strengthen(-OCCLUSION_SENSITIVITY)

        # We don't care if there is an occlusion directly behind the robot
        ignore_lidar_region = BoolLidarMask(
            [(3 * np.pi / 4, 5 * np.pi / 4)],
            lidar_mask.base_angle,
        )
        # Mask out the ignored region
        lidar_mask_reduced = lidar_mask | ignore_lidar_region
        self.logger.info(f" Reduced lidar mask: {lidar_mask_reduced}")

        # Add the next sliding boolean lidar mask to the knowledge base
        self.logger.info(f" - Lidar mask: {lidar_mask}")
        serialized_lidar_mask = pickle.dumps(lidar_mask)

        self.knowledge.write("lidar_mask", serialized_lidar_mask)

        # Set the monitor status to mark an anomaly if the there is any

        # occlusion outside of the ignored region
        anomaly_status_old = self.anomaly
        if lidar_mask_reduced._values.all():
            self.anomaly = False
            self.logger.info(f" Anomaly: {self.anomaly}")
        else:
            self.anomaly = True
            self.logger.info(f" Anomaly: {self.anomaly}")
        if anomaly_status_old != self.anomaly:
            if (self.anomaly == True):
                self.publish_event(event_key='anomaly')


        #<!-- cc_code_analyse_scan_data END--!>

        # self.publish_event(event_key='anomaly')    # LINK <outport> anomaly

    def register_callbacks(self):
        self.register_event_callback(event_key='new_data', callback=self.analyse_scan_data)     # LINK <eventTrigger> new_data
#<!-- cc_include END--!>

#<!-- cc_code START--!>
# Probability threshold for detecting a lidar occlusion
OCCLUSION_THRESHOLD = 0.3
# Number of scans to use for the sliding window
SLIDING_WINDOW_SIZE = 3
# Lidar mask sensitivity (ignore small occlusions below this angle)
OCCLUSION_SENSITIVITY = Fraction(1, 48)


# user defined!
def lidar_mask_from_scan(scan) -> BoolLidarMask:
    scan_ranges = np.array(scan.get("ranges"))
    return BoolLidarMask(
        (scan_ranges != np.inf) & (scan_ranges != -np.inf),
        base_angle=Fraction(2, len(scan.get("ranges"))),
        # base_angle=scan.angleIncrement/180,
    )


### USER Defined Functions
def calculate_lidar_occlusion_rotation_angles(lidar_mask: BoolLidarMask) -> List[Fraction]:
    """
    Calculate the angles of the detected occlusions in the lidar mask.
    :param lidar_mask: The lidar mask.
    :return: A list of angles of the detected occlusions.
    """
    occlusion_angles = []
    mask_angles = np.concatenate((
        np.arange(0, 1, lidar_mask.base_angle),
        np.arange(-1, 0, lidar_mask.base_angle),
    ))
    mask_values = lidar_mask.map_poly(lambda x: 0 if x else 1)._values
    rotation_angles = (mask_angles * mask_values)

    occlusion_angles = [rotation_angles.min(), rotation_angles.max()]

    # Return the two rotations necessary for occlusions on either side
    # of the robot
    match occlusion_angles:
        case [x]:
            return [x, -x]
        case [x, y] if 0 <= x <= y:
            return [y, -y]
        case [x, y] if x <= y <= 0:
            return [x, -x]
        case [x, y] if y - x > 1:
            return [Fraction(2)]
        case [x, y] if abs(x) > abs(y):
            return [x, -x + y, -y]
        case [x, y] if abs(y) > abs(x):
            return [y, -y + x, -x]
        case _:
            assert False


def occlusion_angle_to_rotation(occlusion_angle: Fraction) -> Dict[str, float]:
    signed_angle = float(occlusion_angle) * np.pi
    return {
        'omega': (-1.0) ** int(signed_angle < 0),
        'duration': abs(float(signed_angle)),
    }


def occlusion_angles_to_rotations(occlusion_angles: List[Fraction]) -> List[Dict[str, float]]:
    return list(map(occlusion_angle_to_rotation, occlusion_angles))
#<!-- cc_code END--!>

class Plan(Node):

    def __init__(self, config='config.yaml',verbose=True):
        super().__init__(config=config,verbose=verbose)

        self._name = "Plan"
        self.logger.info("Plan instantiated")

        #<!-- cc_init START--!>
        self._scans = []

        def scans():
            while True:
                for scan in self._scans:
                    yield scan

                self._scans = []

        def raw_lidar_masks():
            for scan in scans():
                yield lidar_mask_from_scan(scan)

        self._sliding_prob_lidar_masks = sliding_prob_lidar_mask(
            raw_lidar_masks(),
            window_size=SLIDING_WINDOW_SIZE,
        )
        #<!-- cc_init END--!>

    # -----------------------------AUTO-GEN SKELETON FOR planner-----------------------------
    def planner(self,msg):
        _NewPlanMessage = NewPlanMessage()
        _Direction = Direction()

        #<!-- cc_code_planner START--!>

        # user code here for planner

        _NewPlanMessage._NewPlan= "SET VALUE"    # datatype: Boolean
        _Direction._omega= "SET VALUE"    # datatype: Float_64
        _Direction._duration= "SET VALUE"    # datatype: Float_64

        self.logger.debug(f"Plan generating: {msg}")
        # Simulate planning logic based on analysis
        # pickled_lidar_mask = self.knowledge.read("lidar_mask")
        # lidar_mask = pickle.load(self.knowledge.read("lidar_mask"))

        #this part of code must be placed in analyse but I cannot retrieve lidar_mask for now
        lidar_data = self.knowledge.read("laser_scan")
        self._scans.append(lidar_data)
        prob_lidar_mask = next(self._sliding_prob_lidar_masks)
        prob_lidar_mask = prob_lidar_mask.rotate(-Fraction(1, 2))
        lidar_mask = (prob_lidar_mask >= OCCLUSION_THRESHOLD)
        # Weaken lidar masks to threshold
        lidar_mask = lidar_mask.weaken(OCCLUSION_SENSITIVITY)
        lidar_mask = lidar_mask.weaken(-OCCLUSION_SENSITIVITY)
        lidar_mask = lidar_mask.strengthen(OCCLUSION_SENSITIVITY)
        lidar_mask = lidar_mask.strengthen(-OCCLUSION_SENSITIVITY)
        #The upper code must be deleted later

        try:
            self.logger.info(
                f"Plan lidar mask determined: {lidar_mask}")

            occlusion_angles = calculate_lidar_occlusion_rotation_angles(lidar_mask)
            directions = occlusion_angles_to_rotations(occlusion_angles)
            self.knowledge.write("directions", json.dumps(directions))
            self.logger.info(f"- Plan action written to knowledge :{directions}")
            new_plan = True
        except:
            self.logger.info("traceback case")
            occlusion_angles = []
            directions = []
            self.logger.info("traceback: " + traceback.format_exc())
            new_plan = False

        if new_plan:
            for i in range(2):
                self.logger.info("Planning")
                time.sleep(0.1)
            self.publish_event("new_plan")
            self.knowledge.write("directions", json.dumps({'commands': directions, 'period': 8}))
            self.logger.info(f"Stored planned action: {directions}")
        #<!-- cc_code_planner END--!>

        # _success = self.knowledge.write(cls=_NewPlanMessage)
        # _success = self.knowledge.write(cls=_Direction)

    def register_callbacks(self):
        self.register_event_callback(event_key='anomaly', callback=self.planner)     # LINK <eventTrigger> anomaly
        # self.register_event_callback(event_key='anomaly', callback=self.planner)        # LINK <inport> anomaly

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
        directions = self.knowledge.read("directions",queueSize=1)
        _Direction = Direction()

        #<!-- cc_code_executer START--!>

        # user code here for executer


        #<!-- cc_code_executer END--!>
        for i in range(1):
            self.logger.info("Executing")
            time.sleep(0.1)
        self.publish_event(event_key='/spin_config',message=json.dumps(directions))    # LINK <outport> spin_config

    def register_callbacks(self):
        self.register_event_callback(event_key='new_plan', callback=self.executer)        # LINK <inport> new_plan
        self.register_event_callback(event_key='isLegit', callback=self.executer)        # LINK <inport> isLegit

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

monitor = Monitor("./Deployment/Nodes/Monitor/config.yaml")
analyse = Analysis("./Deployment/Nodes/Analysis/config.yaml")
plan = Plan("./Deployment/Nodes/Plan/config.yaml")
execute = Execute("./Deployment/Nodes/Execute/config.yaml")
legitimate = Legitimate("./Deployment/Nodes/Legitimate/config.yaml")
trust_c = Trustworthiness("./Deployment/Nodes/Trustworthiness/config.yaml")

monitor.register_callbacks()
analyse.register_callbacks()
plan.register_callbacks()
legitimate.register_callbacks()
execute.register_callbacks()
trust_c.register_callbacks()



monitor.start()
analyse.start()
plan.start()
legitimate.start()
execute.start()
trust_c.start()


try:
    print("Script is running. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)  # Sleep to avoid busy-waiting
except KeyboardInterrupt:
    monitor.shutdown()
    analyse.shutdown()
    plan.shutdown()
    legitimate.shutdown()
    execute.shutdown()
    trust_c.shutdown()
    print("\nKeyboard interruption detected. Exiting...")