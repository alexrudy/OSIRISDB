# -*- coding: utf-8 -*-
"""
Tools to handle FITS files.
"""

from sqlalchemy import Column
from sqlalchemy.types import TypeDecorator, VARCHAR
from astropy.io import fits
from sqlalchemy import inspect

from ..application import db

__all__ = ['FHColumn', 'FHType']

class FHColumn(Column):
    """A column which supports operating on a FITS Header."""
    def __init__(self, *args, **kwargs):
        key = kwargs.pop("key")
        info = kwargs.setdefault('info', {})
        info['FITS.header.key'] = key
        super(FHColumn, self).__init__(*args, **kwargs)

    def parse_header(self, header):
        """Parse a FITS Header, and return the column value."""
        key = self.info['FITS.header.key']
        value = header.get(key, None)
        if value is None:
            return value
        return self.type.python_type(value)
        
    
class FHType(TypeDecorator):
    """A FITS header type"""
    
    impl = VARCHAR
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value.tostring()

        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            value = fits.Header.fromstring(value)
        return value

class FHMixin(db.Model):
    """A base class for FITS-Header based data objects."""
    
    __abstract__ = True
    
    @classmethod
    def parse_header(cls, header):
        """Parse a FITS Header"""
        attrs = {}
        for name, col in inspect(cls).columns.items():
            if hasattr(col, 'parse_header'):
                attrs[name] = col.parse_header(header)
        return attrs
    
    