# -*- coding: utf-8 -*-
import datetime
from flask import current_app, render_template, request
from wtforms_alchemy import ModelFormField, ModelFieldList
from wtforms.fields import FormField, HiddenField, FieldList, DateTimeField
from ..models.logs import OSIRISLog, OSIRISLogDataset, OSIRISLogRowSpec, OSIRISLogRowImager
from ..core import api
from ...application import db
from ...controllers.forms import Form, QuerySelectMultipleField, QuerySelectField
from ...model.person import Person

class PersonForm(Form):
    class Meta:
        model = Person
        
class TimeField(DateTimeField):
    """
    Same as DateTimeField, except stores a `datetime.date`.
    """
    def __init__(self, label=None, validators=None, format='%H:%M:%S', **kwargs):
        super(TimeField, self).__init__(label, validators, format, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist and valuelist != [""]:
            date_str = ' '.join(valuelist)
            try:
                time = datetime.datetime.strptime(date_str, self.format).time()
                self.data = datetime.datetime.combine(datetime.date.today(), time)
            except ValueError as e:
                self.data = None
                raise ValueError(self.gettext('{!r} is not a valid time value: {!r}'.format(date_str, e)))

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
        all_fields_optional = True
        
    ut_start_time = TimeField()
    number = HiddenField()
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

def populate_log(form, log):
    """Populate a log object."""
    for field in form:
        if not isinstance(field, (FormField, QuerySelectField, FieldList)):
            field.populate_obj(log, field.name)
            
    empty_data = LogRowDatasetForm().data
    empty_data.pop("number")
    empty_data.pop("ut_start_time")
    removes = set()
    for row_field in form.rows:
        row_form = row_field.form
        row_number = int(row_form.number.data)
        row_data = row_form.data
        row_data.pop('number', None)
        row_data.pop('ut_start_time', None)
        print("{:d}:{:10.10s}".format(row_number, row_form.object_name.data), end="")
        if row_number < len(log.rows):
            if row_data == empty_data:
                print("Removing", end="")
                db.session.expunge(log.rows[row_number])
                del log.rows[row_number]
                removes.add(row_field)
            else:
                row_form.populate_obj(log.rows[row_number])
        else:

            if row_data == empty_data:
                print("Skipping", end="")
                removes.add(row_field)
                continue
            
            row = OSIRISLogDataset()
            row_form.populate_obj(row)
            log.rows.append(row)
        print("")
    
    for remove in removes:
        form.rows.entries.remove(remove)

@api.route('logs/new/', methods=("GET", "POST"))
@api.route('logs/<int:id>', methods=("GET", "POST"))
def log(id=None):
    """View a log with an identifier."""
    if id is None:
        log = OSIRISLog()
    else:
        log = OSIRISLog.query.get_or_404(id)
    success = False
    
    if request.method == "POST":
        form = LogForm(request.form, obj=log)
    else:
        form = LogForm(obj=log)
        for row in log.rows:
            print("{:d}:{:s}".format(row.number, row.object_name))
    
    for row in form.rows:
        row.form.ut_start_time.format = "%H:%M:%S"
    
    if form.validate_on_submit():
        populate_log(form, log)
        db.session.add(log)
        [db.session.add(row) for row in log.rows]
        db.session.commit()
        
    row = OSIRISLogDataset()
    row.number = len(log.rows)
    form.rows.append_entry(row)
    for row in form.rows:
        row.form.ut_start_time.format = "%H:%M:%S"
    
    return render_template('logs/item.html', log=log, form=form, success=success)
