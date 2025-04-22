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
from fractions import Fraction
from lidarocclusion.masks import BoolLidarMask
from lidarocclusion.sliding_lidar_masks import sliding_lidar_mask, sliding_prob_lidar_mask
from typing import List, Tuple, Dict
import traceback
import json
import numpy as np
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
        #<!-- cc_init END--!>

    # -----------------------------AUTO-GEN SKELETON FOR planner-----------------------------
    def planner(self,msg):
        _Direction = Direction()

        #<!-- cc_code_planner START--!>

        # user code here for planner

        _Direction._omega= "SET VALUE"    # datatype: Float_64
        _Direction._duration= "SET VALUE"    # datatype: Float_64

        self.logger.debug(f"Plan generating: {msg}")

        lidar_data = self.knowledge.read('lidar_mask')
        if lidar_data is None:
            raise Exception("No lidar mask available in knowledge mask")
        else:
            lidar_data = lidar_data.decode('utf-8')

        lidar_mask = BoolLidarMask.from_json(lidar_data)
        # Record the LiDAR mask we last did planning from in the knowledge base
        self.write_knowledge("planned_lidar_mask", lidar_data)
        #The upper code must be deleted later

        try:
            self.logger.info(
                f"Plan lidar mask determined: {lidar_mask}")

            occlusion_angles = calculate_lidar_occlusion_rotation_angles(lidar_mask)
            directions = occlusion_angles_to_rotations(occlusion_angles)
            self.write_knowledge("directions", json.dumps(directions))
            self.logger.info(f"- Plan action written to knowledge :{directions}")
            new_plan = True
        except:
            raise
            self.logger.info("traceback case")
            occlusion_angles = []
            directions = []
            self.logger.info("traceback: " + traceback.format_exc())
            new_plan = False

        if new_plan:
            for i in range(10):
                self.logger.info("Planning")
                time.sleep(0.1)
            self.publish_event(NewPlan)
            self.write_knowledge("directions", json.dumps({'commands': directions, 'period': 8}))
            self.logger.info(f"Stored planned action: {directions}")
        #<!-- cc_code_planner END--!>

        # _success = self.knowledge.write(cls=_NewPlanMessage)
        # _success = self.knowledge.write(cls=_Direction)

    def register_callbacks(self):
        self.register_event_callback(event_key='anomaly', callback=self.planner)     # LINK <eventTrigger> anomaly
        # self.register_event_callback(event_key='anomaly', callback=self.planner)        # LINK <inport> anomaly

def main(args=None):

    node = Plan(config='config.yaml')
    node.register_callbacks()
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()