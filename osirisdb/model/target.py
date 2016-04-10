# -*- coding: utf-8 -*-

from .base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
import astropy.units as u
from astropy.coordinates import Angle, SkyCoord

__all__ = ['Target', 'SIMBADInfo', 'NEDInfo']

class Target(Base):
    """A single target object."""
    
    name = Column(String, doc="User-provided name.")
    
    
class SIMBADInfo(Base):
    """Simbad data for a given target."""
    
    target_id = Column(Integer, ForeignKey('target.id'))
    target = relationship("Target", backref="simbad")
    
    name = Column(String, doc="SIMBAD-resolved main identifier.")
    ra = Column(Float, doc="RA, in radians.")
    dec = Column(Float, doc="Declination, in radians.")
    
    @property
    def coordinates(self):
        """Return a full SkyCoord object for the coordinates."""
        return SkyCoord(self.ra, self.dec, unit=(u.rad, u.rad), frame='icrs')
    
    @classmethod
    def from_query(cls, target, name=None):
        """Make SIMBAD data from an object query."""
        from astroquery.simbad import Simbad
        if name is None:
            name = target.name
        t = Simbad.query_object(name)
        r = t[0]
        ra = Angle(r['RA'], unit=u.hourangle).radian
        dec = Angle(r['DEC'], unit=u.deg).radian
        
        return cls(target=target, ra=ra, dec=dec, name=r['MAIN_ID'].decode("ascii"))
        
    
class NEDInfo(Base):
    """NED information for a target."""
    
    target_id = Column(Integer, ForeignKey('target.id'))
    target = relationship("Target", backref="ned")
    
    name = Column(String, doc="NED-resolved main identifier.")
    kind = Column(String, doc="NED kind.")
    ra = Column(Float, doc="RA, in radians.")
    dec = Column(Float, doc="Declination, in radians.")
    redshift = Column(Float, doc="Redshift, from NED.")
    
    @property
    def coordinates(self):
        """Return a full SkyCoord object for the coordinates."""
        return SkyCoord(self.ra, self.dec, unit=(u.rad, u.rad), frame='icrs')
    
    @classmethod
    def from_query(cls, target, name=None):
        """Make SIMBAD data from an object query."""
        from astroquery.ned import Ned
        if name is None:
            name = target.name
        t = Ned.query_object(name)
        r = t[0]
        ra = Angle(r['RA(deg)'], unit=u.deg).radian
        dec = Angle(r['DEC(deg)'], unit=u.deg).radian
        redshift = r['Redshift']
        kind = r['Type'].decode("ascii")
        name = r['Object Name'].decode("ascii")
        
        return cls(target=target, ra=ra, dec=dec, name=name, kind=kind, redshift=redshift)
    