# -*- coding: utf-8 -*-
"""
Views for servering data files.
"""

from flask import render_template, redirect, request, g, send_from_directory, send_file
from flask.views import MethodView
import os
from ..application import app, db
from ..model import DataFile
from .base import ViewBase

class DataFileViewBase(ViewBase):
    """
    DataFile API base
    """
    model = DataFile
    

class DataFileView(DataFileViewBase, MethodView):
    """Method view to render the dataset."""
    
    def get(self, identifier=None, page=None):
        """Get the dataset view."""
        if identifier is None:
            return render_template("data/list.html", datafiles=self.get_many())
        return render_template("data/item.html", datafile=self.get_one(identifier))
    

@app.route('/datafile/<int:identifier>/preview')
def get_datafile_preview(identifier):
    """Get a preview for a datafile."""
    datafile = DataFile.query.get(identifier)
    path = os.path.abspath(datafile.preview())
    return send_file(path)

@app.route('/datafile/<int:identifier>/download')
def download_datafile(identifier):
    """Download a data file."""
    datafile = DataFile.query.get(identifier)
    path = os.path.abspath(datafile.filename)
    return send_file(path, as_attachment=True)

DataFileView.register_api(app, 'datafile', '/datafile/')