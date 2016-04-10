# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import Column, Text, String, Integer, Date, DateTime, Float, Boolean, ForeignKey
from sqlalchemy import inspect
from sqlalchemy.orm import relationship

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import Angle

from ...model.base import Base
from ...model.fits import FHColumn, FHType

__all__ = ['Dataset', 'SpecFrame']

class Dataset(Base):
    """A single OSIRIS dataset."""
    
    number = Column(Integer, doc="Dataset Number")
    date = Column(Date, doc="UT Date of start of dataset.")
    dataset_name = Column(String, doc="Dataset name from DDF.")
    
    targets = relationship("Target", secondary="specframe", backref="datasets")
    
    
    @classmethod
    def parse_header(cls, header):
        """Parse a header into the necessary attributes."""
        attrs = {}
        attrs['number'] = header.get("SETNUM")
        attrs['date'] = datetime.datetime.strptime(header.get("DATE-OBS"), "%Y-%m-%d").date()
        attrs['dataset_name'] = header.get("DATASET")
        return attrs
    
    @classmethod
    def from_header(cls, header):
        """Make a new dataset object from a header."""
        attrs = cls.parse_header(header)
        return cls(**attrs)

class Frame(Base):
    """Database row for a single OSIRIS frame."""
    
    __abstract__ = True
        
    number = FHColumn(Integer, doc="Frame Number", key="FRAMENUM")
    obstype = FHColumn(String, doc="Observation Type", key="OBSTYPE")
    header = Column(FHType, doc="FITS Header")
    
    integration_time = FHColumn(Float, doc="Integration time in seconds for each coadd.", key="ITIME")
    coadds = FHColumn(Integer, doc="Number of coadds per frame.", key="COADDS")
    object_name = FHColumn(String, doc="Target name from DDF.", key="OBJECT")
    
    ra = Column(Float, doc="Frame position (RA) in radians.")
    dec = Column(Float, doc="Frame position (DEC) in radians.")
    
    airmass = FHColumn(Float, doc="Airmass of observation.", key="AIRMASS")
    
    time = Column(DateTime, doc="UT time for observation.")
    
    
class SpecFrame(Frame):
    """Frame parts that apply to the spectral frame specifically."""
    dataset_id = Column(Integer, ForeignKey("dataset.id"))
    dataset = relationship("Dataset", backref='sframes')
    
    target_id = Column(Integer, ForeignKey("target.id"))
    target = relationship("Target", backref="osiris_spec_frames")
    
    filter = FHColumn(String, doc="Filter", key="SFILTER")
    scale = FHColumn(Float, doc="Spaxel scale, in arcseconds per spaxel", key="SSCALE")
    
    sky = FHColumn(Boolean, doc="Is this a sky frame?", key="ISSKY")
    
    pa = FHColumn(Float, doc="Rotator position (PA) in degrees.", key="PA_SPEC")
    
    dataframes = relationship("DataFile", secondary="specframedata", backref="specframes")
    
    @classmethod
    def from_header(cls, header, dataset=None):
        """Make a new SpecFrame from the given header."""
        attrs = {}
        for name, col in inspect(cls).columns.items():
            if isinstance(col, FHColumn):
                attrs[name] = col.parse_header(header)
            
        time = "{0}T{1}".format(header["DATE-OBS"], header["UTC"])
        attrs['time'] = Time(time, format='isot').datetime
        attrs['ra'] = Angle(header["RA"], unit=u.deg).radian
        attrs['dec'] = Angle(header["DEC"], unit=u.deg).radian
        attrs['header'] = header
        if dataset is not None:
            attrs['dataset'] = dataset
        return cls(**attrs)
    

class SpecFrameData(Base):
    """An association table for spectrum frame data files."""
    
    specframe_id = Column(Integer, ForeignKey("specframe.id"))
    datafile_id = Column(Integer, ForeignKey("datafile.id"))
        