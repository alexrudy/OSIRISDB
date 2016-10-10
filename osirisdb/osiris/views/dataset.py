# -*- coding: utf-8 -*-
from flask.views import MethodView
from flask import render_template, redirect, g, jsonify

import datetime

from ..core import api
from ..models import Dataset
from ...views.targets import select_target_form
from ...model.target import Target
from ...views.base import ViewBase
from ...views.archive import ArchiveView
from ...application import db

__all__ = ['DatasetView']

class DatasetBase(ViewBase):
    """
    Dataset API base
    """
    model = Dataset
    

class DatasetView(DatasetBase, MethodView):
    """Method view to render the dataset."""
    
    def get(self, identifier=None, page=None):
        """Get the dataset view."""
        if identifier is None:
            return render_template("datasets/list.html", datasets=self.get_paginate(page))
        return render_template("datasets/item.html", dataset=self.get_one(identifier))

ArchiveView.register(api, 'dataset_archive', Dataset, 'datasets/', prefix='datasets/archive', modelcontextname='datasets')

@api.route("datasets/page/<int:page>/raw")
def dataset_raw(page=None):
    """Return the raw part of the dataset page."""
    return render_template("datasets/_datasets.html", datasets=Dataset.query.order_by(Dataset.date).paginate(page, per_page=100))

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
        db.session.refresh(dataset)
        return redirect(form.prev.data)
    elif form.target.data == -2:
        target = Target.query.filter(Target.name == form.new_targetname.data).one_or_none()
        if not target:
            target = Target(name=form.new_targetname.data)
        dataset = Dataset.query.get(id)
        db.session.add(target)
        for frame in dataset.sframes:
            frame.target = target
            db.session.add(frame)
        db.session.commit()
    elif form.target.data == -1:
        dataset = Dataset.query.get(id)
        for frame in dataset.sframes:
            frame.target = None
            db.session.add(frame)
        db.session.commit()
    if form.prev.data:
        return redirect(form.prev.data)
    if target:
        return jsonify({'name':target.name, 'id':target.id})
    return jsonify("")

@api.route("datasets/<int:id>/target/_row/", methods=('GET',))
def get_dataset_row(id):
    """Get a specific row for a dataset."""
    dataset = Dataset.query.get(id)
    return render_template("datasets/_dataset_row_target.html", dataset=dataset)

DatasetView.register_api(api, 'dataset', 'datasets/')