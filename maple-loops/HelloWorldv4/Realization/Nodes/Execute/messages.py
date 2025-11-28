class LaserScan(object):
    def __init__(self):

        self.name= "LaserScan"
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


class AnomalyEvent(object):
    def __init__(self):

        self.name= "AnomalyEvent"
        self._anomaly= None


    @property
    def anomaly(self):
        """The anomaly (read-only)."""
        return self._anomaly

    @anomaly.setter
    def anomaly(self, cmp):
        """The anomaly (write)."""
        self._anomaly = cmp


class NewPlanEvent(object):
    def __init__(self):

        self.name= "NewPlanEvent"
        self._NewPlan= None


    @property
    def NewPlan(self):
        """The NewPlan (read-only)."""
        return self._NewPlan

    @NewPlan.setter
    def NewPlan(self, cmp):
        """The NewPlan (write)."""
        self._NewPlan = cmp


