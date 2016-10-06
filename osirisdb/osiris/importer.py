# -*- coding: utf-8 -*-
"""
Tools to import FITS files from their headers.
"""

import click

from astropy.io import fits

from .models import Dataset, SpecFrame
from ..model import DataFile
from ..application import app, db

__all__ = ['import_osiris_fits', 'oimport']

def import_osiris_fits(filename, session):
    """Import an OSIRIS fits file to session."""
    
    with fits.open(filename) as HDUs:
        primary_header = HDUs[0].header
        
        # Create the dataset.
        q = Dataset.query.filter_by(**Dataset.parse_header(primary_header))
        dataset = q.one_or_none()
        if dataset is None:
            dataset = Dataset.from_header(primary_header)
            frame = None
        else:
            # Create the Frame.
            frame_number = int(primary_header['FRAMENUM'])
            frame = SpecFrame.query.filter(SpecFrame.dataset == dataset, SpecFrame.number == frame_number).one_or_none()
        
        if frame is None:
            frame = SpecFrame.from_header(primary_header, dataset=dataset)
            session.add(frame)

        
        # Add a datafile object for the file itself.
        datafile = DataFile.query.filter(DataFile.filename == filename).one_or_none()
        if datafile is None:
            datafile = DataFile.from_filename(filename)
            frame.dataframes.append(datafile)
            session.add(datafile)
        
        # Add them to the session.
        dataset.sframes.append(frame)
        session.add(dataset)
        
    
@app.cli.command()
@click.argument('files', nargs=-1, type=str)
def oimport(files):
    """Import OSIRIS data files."""
    for filename in files:
        click.echo("Importing '{0:s}'".format(filename))
        import_osiris_fits(filename, db.session)
    db.session.commit()
    
@app.cli.command()
def odelete():
    """Delete OSIRIS data frames from databaes"""
    db.session.query(Dataset).delete()
    db.session.query(SpecFrame).delete()
    db.session.commit()
    
