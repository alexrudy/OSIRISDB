# -*- coding: utf-8 -*-

from .base import Base

import os
import socket
import h5py
from astropy.io import fits
from sqlalchemy import Column, String, Integer, ForeignKey

__all__ = ['DataFile']

KINDMAP = {
    '.fits' : 'fits',
    '.hdf5' : 'hdf5',
}

class DataFile(Base):
    """A data file, stored somewhere on a disk."""
    
    kind = Column(String, doc="File kind.")
    host = Column(String, doc="Hostname which holds the data file.")
    filename = Column(String, doc="File path")
    
    @property
    def basename(self):
        """Basename of the file."""
        return os.path.basename(self.filename)
    
    @classmethod
    def from_filename(cls, filename):
        """From a filename, create a data file record."""
        kind = KINDMAP[os.path.splitext(filename)[1]]
        return cls(host=socket.gethostname(), filename=filename, kind=kind)
        
    def open(self, mode="r"):
        """Open this file."""
        if socket.gethostname() != self.host:
            warnings.warn("Trying to open a file which might not be on this host.")
        if self.kind == "fits":
            return fits.open(self.filename, mode=mode)
        elif self.kind == "hdf5":
            return h5py.File(self.filename, mode=mode)
        else:
            return open(self.filename, mode=mode)