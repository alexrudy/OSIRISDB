# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import render_template, redirect, g

import datetime

from ..core import api
from ..models import Dataset
from ...views.targets import select_target_form
from ...model.target import Target
from ...views.base import ViewBase
from ...application import db

__all__ = ['DatasetView']

class DatasetBase(ViewBase):
    """
    Dataset API base
    """
    model = Dataset
    

class DatasetView(DatasetBase, MethodView):
    """Method view to render the dataset."""
    
    def get(self, identifier=None):
        """Get the dataset view."""
        if identifier is None:
            return render_template("datasets/list.html", datasets=self.get_many())
        return render_template("datasets/item.html", dataset=self.get_one(identifier))
        
@api.route('datasets/archive/<int:year>/<int:month>/<int:day>/', endpoint='dataset_archive')
@api.route('datasets/archive/<int:year>/<int:month>/', endpoint='dataset_archive')
@api.route('datasets/archive/<int:year>', endpoint='dataset_archive')
def archive(year, month=None, day=None):
    """Get the dataset view, by date."""
    start_date = datetime.date(year, month or 1, day or 1)
    if month is None:
        end_date = datetime.date(year+1, 1, 1)
    elif day is None:
        end_date = datetime.date(year, month + 1, 1)
    else:
        end_date = start_date + datetime.timedelta(days=1)
    datasets = Dataset.query.filter(Dataset.date.between(start_date, end_date)).all()
    return render_template("datasets/archive.html", datasets=datasets, year=year, month=month, day=day)

@api.route("datasets/<int:id>/target/", methods=('POST',))
def set_dataset_target(id):
    """Set the target for a particular dataset."""
    form = select_target_form
    if form.validate_on_submit():
        target = Target.query.get(form.target.data)
        dataset = Dataset.query.get(id)
        for frame in dataset.sframes:
            frame.target = target
            db.session.add(frame)
        db.session.commit()
        return redirect(form.prev.data)
    return redirect(form.prev.data)

DatasetView.register_api(api, 'dataset', 'datasets/')