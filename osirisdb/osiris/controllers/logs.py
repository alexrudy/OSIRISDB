# -*- coding: utf-8 -*-

from flask import current_app, render_template, request
from wtforms_alchemy import ModelFormField, ModelFieldList
from wtforms.fields import FormField
from ..models.logs import OSIRISLog, OSIRISLogDataset, OSIRISLogRowSpec, OSIRISLogRowImager
from ..core import api
from ...application import db
from ...controllers.forms import Form, QuerySelectMultipleField, QuerySelectField
from ...model.person import Person

class PersonForm(Form):
    class Meta:
        model = Person

class LogRowSpecForm(Form):
    """A form for the spectrograph log row."""
    
    class Meta(object):
        model = OSIRISLogRowSpec
        all_fields_optional = True
        
        
    
class LogRowImagerForm(Form):
    """A form for the imager log row."""
    
    class Meta(object):
        model = OSIRISLogRowImager
        all_fields_optional = True
        
    
class LogRowDatasetForm(Form):
    
    class Meta(object):
        model = OSIRISLogDataset
        include = ['ut_start_time']
        all_fields_optional = True
        
    spectrograph = ModelFormField(LogRowSpecForm)
    imager = ModelFormField(LogRowImagerForm)

class LogForm(Form):
    
    class Meta(object):
        model = OSIRISLog
        all_fields_optional = True
        
    support_astronomer = QuerySelectField(query_factory=Person.query.all, get_label='name', allow_blank=True)
    observing_assistant = QuerySelectField(query_factory=Person.query.all, get_label='name', allow_blank=True)
    # observers = QuerySelectField(query_factory=Person.query.all, get_label='name', allow_blank=True)
    
    rows = ModelFieldList(FormField(LogRowDatasetForm, default=lambda: OSIRISLogDataset()), population_strategy='replace', min_entries=1)

@api.route('logs/<int:id>/row/<int:row_id>', methods=('GET', 'POST'))
@api.route('logs/<int:id>/row/', methods=('GET', 'POST'))
def row_form(id, row_id=None):
    log = OSIRISLog.query.get_or_404(id)
    success = False
    if row_id is not None:
        row = OSIRISLogDataset.query.get_or_404(row_id)
    else:
        row = OSIRISLogDataset()
    row.log = log
    
    form = LogRowDatasetForm(obj=row)
    if form.validate_on_submit():
        form.populate_obj(row)
        db.session.add(row)
        db.session.commit()
        success = True
    
    return render_template('logs/_row.html', form=form, row=row, success=success)

@api.route('logs/new/', methods=("GET", "POST"))
@api.route('logs/<int:id>', methods=("GET", "POST"))
def log(id=None):
    """View a log with an identifier."""
    if id is None:
        log = OSIRISLog()
    else:
        log = OSIRISLog.query.get_or_404(id)
    success = False
    
    if request.method == 'POST':
        form = LogForm(request.form, obj=log)
        if form.validate():
            form.populate_obj(log)
            for i, row in enumerate(form.rows):
                row.populate_obj(log.row[i])
            for row in log.rows:
                db.session.add(row)
            db.session.add(log)
            db.session.commit()
            success = True
        else:
            print("Validation failed")
            print(form.errors)
    else:
        form = LogForm(obj=log)
    
    for row in log.rows:
        form.rows.append_entry(row)
    form.rows.append_entry()
    return render_template('logs/item.html', log=log, form=form, success=success)
