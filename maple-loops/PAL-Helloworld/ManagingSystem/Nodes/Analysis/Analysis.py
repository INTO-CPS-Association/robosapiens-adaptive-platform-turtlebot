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
from fractions import Fraction
from .lidarocclusion.masks import BoolLidarMask, ProbLidarMask
from .lidarocclusion.sliding_lidar_masks import sliding_lidar_mask, sliding_prob_lidar_mask
from .lidarocclusion.masks import BoolLidarMask
from typing import List, Tuple, Dict
import traceback
import numpy as np
import pickle
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

def main(args=None):

    node = Analysis(config='config.yaml')
    node.register_callbacks()
    node.start()

if __name__ == '__main__':
    main()
    try:
       while True:
           time.sleep(1)
    except:
       exit()