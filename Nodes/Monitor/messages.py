from enum import Enum

class Type(Enum):
    Event = 1
    Knowledge = 2
    Message = 3


class LaserScan(object):
    def __init__(self):

        self.name= "LaserScan"
        self.type = Type.Knowledge

        self.uid= None
        self.timestamp= None
        self.topic= "/Scan"
        self._ranges= []
        self._angle_increment= 0.0


    @property
    def ranges(self):
        """The ranges (read-only)."""
        return self._ranges

    @ranges.setter
    def ranges(self, cmp):
        """The ranges (write)."""
        self._ranges = cmp

    @property
    def angle_increment(self):
        """The angle_increment (read-only)."""
        return self._angle_increment

    @angle_increment.setter
    def angle_increment(self, cmp):
        """The angle_increment (write)."""
        self._angle_increment = cmp


class Direction(object):
    def __init__(self):

        self.name= "Direction"
        self.type = Type.Knowledge
        self.uid= None
        self.timestamp= None
        self.topic= None

        self._omega= 0.0
        self._duration= 0.0


    @property
    def omega(self):
        """The omega (read-only)."""
        return self._omega

    @omega.setter
    def omega(self, cmp):
        """The omega (write)."""
        self._omega = cmp

    @property
    def duration(self):
        """The duration (read-only)."""
        return self._duration

    @duration.setter
    def duration(self, cmp):
        """The duration (write)."""
        self._duration = cmp
 

    def __init__(self):
        self.name= "NewData"
        self.type = Type.Event 
        self.uid= None
        self.timestamp= None
        self.topic= None
        
class NewData(object):

    def __init__(self):
        self.name= "NewData"
        self.type = "event"
        self.topic= "new_data"
        self.timestamp= None

class NewPlan(object):
    def __init__(self):
        self.name= "NewPlan"
        self.type = "event"
        self.uid= None
        self.timestamp= "new_plan"
        self.topic= None


    @property
    def NewPlan(self):
        """The NewPlan (read-only)."""
        return self._NewPlan

    @NewPlan.setter
    def NewPlan(self, cmp):
        """The NewPlan (write)."""
        self._NewPlan = cmp

class Anomaly(object):
    def __init__(self):
        self.name= "Anomaly"
        self.type = Type.Event
        self.uid= None
        self.timestamp= None
        self.topic= "anomaly"


class isLegit(object):
    def __init__(self):
        self.name= "isLegit"
        self.type = Type.Event
        self.uid= None
        self.timestamp= None
        self.topic= "isLegit"

class HandlingAnomalyData(object):
    def __init__(self):

        self.name= "HandlingAnomaly"
        self.uid= None
        self.timestamp= None
        self._anomaly= False


    @property
    def HandlingAnomaly(self, cmp):
        """The NewPlan (read-only)."""
        self._anomaly = cmp