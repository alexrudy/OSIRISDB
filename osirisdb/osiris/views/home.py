# -*- coding: utf-8 -*-

from flask import render_template
from ..core import api
from ..models import Dataset

@api.route('')
def home():
    """OSIRIS Home view."""
    return render_template('osiris_home.html', datasets=Dataset.query.all())