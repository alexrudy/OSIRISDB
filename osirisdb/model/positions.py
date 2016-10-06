# -*- coding: utf-8 -*-

from sqlalchemy.types import TypeDecorator, Float
from astropy.coordinates import Angle as apAngle
import astropy.units as u

class Quantity(TypeDecorator):
    """A quantity type"""
    
    impl = Float
    
    def __init__(self, unit):
        super(Quantity, self).__init__()
        self.unit = u.Unit(unit)
    
    def python_type(self, value):
        """Make this into a python type."""
        return u.Quantity(value, self.unit)
    
    def process_bind_param(self, value, dialect):
        """Bind a parameter to the flaot value."""
        if value is not None:
            value = u.Quantity(value, unit=self.unit).to(self.unit).value
        return value
    
    def process_result_value(self, value, dialect):
        """Get the value back from the database."""
        if value is not None:
            value = u.Quantity(value, self.unit)
        return value

class Angle(TypeDecorator):
    """A type representing an angle in radians"""
    
    impl = Float
    
    def python_type(self, value):
        return apAngle(value)
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = apAngle(value, unit=u.radian).to(u.radian).value
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            value = apAngle(value, u.radian)
        return value
    