class ShipStatus(object):
    def __init__(self):

        self.name= "ShipStatus"
        self._ship_prediction_model= 'TBD'
        self._surge_speed= 0.0
        self._sway_speed= 0.0
        self._yaw_rate= 0.0
        self._heading= 0.0
        self._x= []
        self._y= []


    @property
    def ship_prediction_model(self):
        """The ship_prediction_model (read-only)."""
        return self._ship_prediction_model

    @ship_prediction_model.setter
    def ship_prediction_model(self, cmp):
        """The ship_prediction_model (write)."""
        self._ship_prediction_model = cmp

    @property
    def surge_speed(self):
        """The surge_speed (read-only)."""
        return self._surge_speed

    @surge_speed.setter
    def surge_speed(self, cmp):
        """The surge_speed (write)."""
        self._surge_speed = cmp

    @property
    def sway_speed(self):
        """The sway_speed (read-only)."""
        return self._sway_speed

    @sway_speed.setter
    def sway_speed(self, cmp):
        """The sway_speed (write)."""
        self._sway_speed = cmp

    @property
    def yaw_rate(self):
        """The yaw_rate (read-only)."""
        return self._yaw_rate

    @yaw_rate.setter
    def yaw_rate(self, cmp):
        """The yaw_rate (write)."""
        self._yaw_rate = cmp

    @property
    def heading(self):
        """The heading (read-only)."""
        return self._heading

    @heading.setter
    def heading(self, cmp):
        """The heading (write)."""
        self._heading = cmp

    @property
    def x(self):
        """The x (read-only)."""
        return self._x

    @x.setter
    def x(self, cmp):
        """The x (write)."""
        self._x = cmp

    @property
    def y(self):
        """The y (read-only)."""
        return self._y

    @y.setter
    def y(self, cmp):
        """The y (write)."""
        self._y = cmp


class WeatherCondition(object):
    def __init__(self):

        self.name= "WeatherCondition"
        self._rudder_angle= []
        self._wind_direction= []
        self._wind_speed= []


    @property
    def rudder_angle(self):
        """The rudder_angle (read-only)."""
        return self._rudder_angle

    @rudder_angle.setter
    def rudder_angle(self, cmp):
        """The rudder_angle (write)."""
        self._rudder_angle = cmp

    @property
    def wind_direction(self):
        """The wind_direction (read-only)."""
        return self._wind_direction

    @wind_direction.setter
    def wind_direction(self, cmp):
        """The wind_direction (write)."""
        self._wind_direction = cmp

    @property
    def wind_speed(self):
        """The wind_speed (read-only)."""
        return self._wind_speed

    @wind_speed.setter
    def wind_speed(self, cmp):
        """The wind_speed (write)."""
        self._wind_speed = cmp


class AnomalyMessage(object):
    def __init__(self):

        self.name= "AnomalyMessage"
        self._anomaly= None


    @property
    def anomaly(self):
        """The anomaly (read-only)."""
        return self._anomaly

    @anomaly.setter
    def anomaly(self, cmp):
        """The anomaly (write)."""
        self._anomaly = cmp


class NewPlanMessage(object):
    def __init__(self):

        self.name= "NewPlanMessage"
        self._New_plan= None


    @property
    def New_plan(self):
        """The New_plan (read-only)."""
        return self._New_plan

    @New_plan.setter
    def New_plan(self, cmp):
        """The New_plan (write)."""
        self._New_plan = cmp


class Model(object):
    def __init__(self):

        self.name= "Model"
        self._ship_prediction_model= 'TBD'


    @property
    def ship_prediction_model(self):
        """The ship_prediction_model (read-only)."""
        return self._ship_prediction_model

    @ship_prediction_model.setter
    def ship_prediction_model(self, cmp):
        """The ship_prediction_model (write)."""
        self._ship_prediction_model = cmp


