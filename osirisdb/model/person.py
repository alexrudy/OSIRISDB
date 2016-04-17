# -*- coding: utf-8 -*-

from .base import Base

from sqlalchemy import Column, String, Integer

__all__ = ['Person']

class Person(Base):
    """A person."""
    
    name = Column(String)
    email = Column(String)
    institution = Column(String)
    
        