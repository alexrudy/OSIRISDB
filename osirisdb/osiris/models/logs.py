# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import Column, Text, String, Integer, Date, DateTime, Float, Boolean, ForeignKey
from sqlalchemy import inspect
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import Angle

from ...model.base import Base

class _OSIRISObserver(Base):
    """Association table to connect observers to log entries"""
    
    person_id = Column(Integer, ForeignKey("person.id"))
    log_id = Column(Integer, ForeignKey("osirislog.id"))

class OSIRISLog(Base):
    """A group of log entries for OSIRIS."""
    
    date = Column(Date, doc='UT Start of log date.', default=datetime.date.today)
    program = Column(String, doc='Keck Program Identifier')
    
    observers = relationship("Person", secondary="_osirisobserver")
    
    support_astronomer_id = Column(Integer, ForeignKey("person.id"))
    support_astronomer = relationship("Person", foreign_keys=[support_astronomer_id])
    observing_assistant_id = Column(Integer, ForeignKey("person.id"))
    observing_assistant = relationship("Person", foreign_keys=[observing_assistant_id])
    
    weather = Column(Text, doc="Weather")
    
    data_directory = Column(String, doc="Data directory", info={"label":"Data Directory"})
    
class OSIRISLogRow(Base):
    """A single row entry in an OSIRIS log."""
    __abstract__ = True
    created = Column(DateTime, doc="When this log row was created.", default=datetime.datetime.now)
        
class OSIRISLogNote(OSIRISLogRow):
    """A note entry."""
    log_id = Column(Integer, ForeignKey("osirislog.id"))
    log = relationship("OSIRISLog", backref="notes")
    
    note = Column(Text)
    
class OSIRISLogDataset(OSIRISLogRow):
    
    log_id = Column(Integer, ForeignKey("osirislog.id"))
    log = relationship("OSIRISLog", backref="rows")
    ut_start_time = Column(DateTime, doc="UT Start time for this dataset.", default=datetime.datetime.now)
    dataset_number = Column(Integer, doc="Dataset number.")
    object_name = Column(String)
    airmass = Column(Float)
    pa_used = Column(Float)
    ao_rate = Column(Float)
    ao_gain = Column(Float)
    comments = Column(Text)
    
class OSIRISLogRowSpec(Base):
    """Row items which relate to the spectrograph."""
    
    log_dataset_id = Column(Integer, ForeignKey("osirislogdataset.id"))
    log_dataset = relationship("OSIRISLogDataset", backref='spec', uselist=False)
    
    number_of_frames = Column(Integer)
    filter = Column(String)
    scale = Column(String)
    integration_time = Column(Float)
    coadds = Column(Integer, default=1)
    dither_object = Column(Integer)
    dither_sky = Column(Integer)
    
class OSIRISLogRowImager(Base):
    """Row items which relate to the imager."""
    log_dataset_id = Column(Integer, ForeignKey("osirislogdataset.id"))
    log_dataset = relationship("OSIRISLogDataset", backref='imag', uselist=False)
    
    number_of_frames = Column(Integer)
    filter = Column(String)
    repeats = Column(Integer)
    integration_time = Column(Float)
    coadds = Column(Integer, default=1)
    dither_object = Column(Integer)
    dither_sky = Column(Integer)
        