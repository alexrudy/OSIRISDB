# -*- coding: utf-8 -*-

from flask import render_template
from ..core import api
from ..models import Dataset, OSIRISLog

@api.route('')
def home():
    """OSIRIS Home view."""
    return render_template('osiris_home.html', datasets=Dataset.query.order_by(Dataset.date).paginate(), logs=OSIRISLog.query.all())