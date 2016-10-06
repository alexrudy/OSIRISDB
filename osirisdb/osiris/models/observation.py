# -*- coding: utf-8 -*-

import datetime

from copy import copy

from sqlalchemy import Column, Text, String, Integer, Date, DateTime, Float, Boolean, ForeignKey
from sqlalchemy import inspect
from sqlalchemy.orm import relationship

import astropy.units as u
from astropy.time import Time
from astropy import coordinates

from ...model.positions import Angle, Quantity
from ...model.base import Base
from ...model.fits import FHColumn, FHType, FHMixin

__all__ = ['Dataset', 'SpecFrame']

class Dataset(Base, FHMixin):
    """A single OSIRIS dataset."""
    
    number = FHColumn(Integer, doc="Dataset Number", key="SETNUM")
    date = Column(Date, doc="UT Date of start of dataset.")
    dataset_name = FHColumn(String, doc="Dataset name from DDF.", key="DATASET")
    
    targets = relationship("Target", secondary="specframe", backref="datasets")
    
    def _add_name_to_target_choices(self, form):
        """Add name to target choices field"""
        form = copy(form)
        for value, label in form.target.choices:
            if label == self.dataset_name:
                if len(self.targets) and all(target.name == label for target in self.targets):
                    form.target.choices.insert(0, (value, label))
                break
        else:
            form.target.choices.append((-2, self.dataset_name))
        form.new_targetname.data = self.dataset_name
        return form
    
    def object_name(self):
        """Return the object name, if it is consistent across all frames."""
        names = set(frame.object_name for frame in self.sframes)
        if len(names) == 1:
            return names.pop()
        else:
            return None
    
    @classmethod
    def parse_header(cls, header):
        """Parse a header into the necessary attributes."""
        attrs = super(Dataset, cls).parse_header(header)
        attrs['number'] = header.get("SETNUM")
        attrs['date'] = datetime.datetime.strptime(header.get("DATE-OBS"), "%Y-%m-%d").date()
        attrs['dataset_name'] = header.get("DATASET")
        return attrs
    
    @classmethod
    def from_header(cls, header):
        """Make a new dataset object from a header."""
        attrs = cls.parse_header(header)
        return cls(**attrs)

class Frame(Base, FHMixin):
    """Database row for a single OSIRIS frame."""
    
    __abstract__ = True
        
    number = FHColumn(Integer, doc="Frame Number", key="FRAMENUM")
    obstype = FHColumn(String, doc="Observation Type", key="OBSTYPE")
    header = Column(FHType, doc="FITS Header")
    
    integration_time = FHColumn(Quantity(u.second), doc="Integration time in seconds for each coadd.", key="ITIME")
    coadds = FHColumn(Integer, doc="Number of coadds per frame.", key="COADDS")
    object_name = FHColumn(String, doc="Target name from DDF.", key="OBJECT")
    
    ra = Column(Angle, doc="Frame position (RA) in radians.", key="RA")
    dec = Column(Angle, doc="Frame position (DEC) in radians.", key="DEC")
    
    airmass = FHColumn(Float, doc="Airmass of observation.", key="AIRMASS")
    
    time = Column(DateTime, doc="UT time for observation.")
    
    def _format_keywords(self):
        """Format keywords"""
        keywords = []
        for name, col in inspect(self.__class__).columns.items():
            if name != 'header':
                keywords.append("{}={!r}".format(name, getattr(self, name)))
        return ", ".join(keywords)
    
    @classmethod
    def parse_header(cls, header):
        """Parse a header."""
        attrs = super(Frame, cls).parse_header(header)
        try:
            if "ITIME0" in header and "microseconds" in header.comments['ITIME0']:
                original = attrs['integration_time']
                attrs['integration_time'] = (header['ITIME0'] * u.microsecond).to(u.second)
        except KeyError:
            pass
        attrs['ra'] = coordinates.Angle(header["RA"], unit=u.deg).radian
        attrs['dec'] = coordinates.Angle(header["DEC"], unit=u.deg).radian
        time = "{0}T{1}".format(header["DATE-OBS"], header["UTC"])
        attrs['time'] = Time(time, format='isot').datetime
        return attrs
    
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
        attrs = cls.parse_header(header)
        attrs['header'] = header
        if dataset is not None:
            attrs['dataset'] = dataset
        return cls(**attrs)
    

class SpecFrameData(Base):
    """An association table for spectrum frame data files."""
    
    specframe_id = Column(Integer, ForeignKey("specframe.id"))
    datafile_id = Column(Integer, ForeignKey("datafile.id"))
        