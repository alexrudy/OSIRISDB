# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, inspect
from ..application import db

class Base(db.Model):
    """A generic base class for uniform handling of things like the primary key."""
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(Integer, primary_key=True, doc="Primary key identifier for the database.")
    
    def _format_keywords(self):
        """Format keywords"""
        keywords = []
        for name, col in inspect(self.__class__).columns.items():
            keywords.append("{}={!r}".format(name, getattr(self, name)))
        return ", ".join(keywords)
    
    def __repr__(self):
        """Lets make a better default repr"""
        result = "{}({})".format(self.__class__.__name__, self._format_keywords())
        return result
