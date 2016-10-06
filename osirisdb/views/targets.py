# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, g
from flask.views import MethodView
from ..application import app, db
from ..model import Target, NEDInfo, SIMBADInfo
from .base import ViewBase

from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, HiddenField, validators
from werkzeug.local import LocalProxy
__all__ = ['TargetView']

class TargetBase(ViewBase):
    """
    Dataset API base
    """
    model = Target
    

class TargetView(TargetBase, MethodView):
    """Method view to render the dataset."""
    
    def get(self, identifier=None, page=None):
        """Get the dataset view."""
        if identifier is None:
            form = TargetForm()
            return render_template("targets/list.html", targets=self.get_many(), form=form)
        return render_template("targets/item.html", target=self.get_one(identifier), ned_form=AddInfoForm(), simbad_form=AddInfoForm())
    
    def delete(self, identifier=None):
        """Delete a target"""
        t = Target.query.get(identifier)
        if t:
            db.session.expunge(t)
        db.session.commit()
        return redirect("/targets/")

class NEDInfoView(ViewBase, MethodView):
    
    model = NEDInfo
    
    def get(self, identifier=None):
        """Get the dataset view."""
        if identifier is None:
            return render_template("ned/list.html", neds=self.get_many())
        return render_template("ned/item.html", ned=self.get_one(identifier))

class SIMBADInfoView(ViewBase, MethodView):
    
    model = SIMBADInfo
    
    def get(self, identifier=None):
        """Get the dataset view."""
        if identifier is None:
            return render_template("simbad/list.html", simbads=self.get_many())
        return render_template("simbad/item.html", simbad=self.get_one(identifier))

@app.route("/ned/<int:id>/delete/")
def nedinfo_delete(id=None):
    """Delete the given identifier."""
    item = NEDInfo.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect("/ned/")

@app.route("/simbad/<int:id>/delete/")
def simbadinfo_delete(id=None):
    """Delete the given identifier."""
    item = SIMBADInfo.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect("/simbad/")
    
class TargetForm(Form):
    """A new target form."""
    
    name = StringField('Target Name', validators=[validators.DataRequired()])

class SelectTarget(Form):
    """Select a new target form"""
    
    prev = HiddenField()
    new_targetname = HiddenField()
    target = SelectField("Target", default="", coerce=int)
    
    def __init__(self):
        super(SelectTarget, self).__init__()
        self.prev.data = request.referrer
        self.target.choices = [(-1, "")] + [(t.id, t.name) for t in Target.query.order_by(Target.name).all()]
        
    

class AddInfoForm(Form):
    """Add NED Info by querying NED."""
    prev = HiddenField()
    name = StringField('Target Name', validators=[validators.DataRequired()])
    
    def __init__(self):
        super(AddInfoForm, self).__init__()
        self.prev.data = request.referrer

def get_select_target_form():
    """Get the select target form."""
    if not hasattr(g, "_select_target_form"):
        form = SelectTarget()
    else:
        form = g._select_target_form
    return form

select_target_form = LocalProxy(get_select_target_form)

@app.context_processor
def add_target_forms():
    return dict(select_target_form=select_target_form, )

TargetView.register_api(app, 'target', '/targets/')
NEDInfoView.register_api(app, 'nedinfo', '/ned/')
SIMBADInfoView.register_api(app, 'simbadinfo', '/simbad/')

@app.route('/targets/new/', methods=('GET', 'POST'))
def new_target():
    """Generate a new target."""
    form = TargetForm()
    if form.validate_on_submit():
        target = Target.query.filter(Target.name == form.name.data).one_or_none()
        if target is None:
            target = Target(name=form.name.data)
            db.session.add(target)
            db.session.commit()
        return redirect('/targets/')
    return render_template('targets/new.html', form=form)
    
@app.route('/targets/<int:id>/ned/new/', methods=('GET', 'POST'))
def add_NEDinfo(id):
    """Add NEDInfo."""
    form = AddInfoForm()
    if form.validate_on_submit():
        target = Target.query.get(id)
        ni = NEDInfo.from_query(target, form.name.data)
        db.session.add(ni)
        db.session.commit()
        redirect(form.prev.data)
    return redirect(form.prev.data)
    

@app.route('/targets/<int:id>/simbad/new/', methods=('GET', 'POST'))
def add_SIMBADinfo(id):
    """Add NEDInfo."""
    form = AddInfoForm()
    if form.validate_on_submit():
        target = Target.query.get(id)
        si = SIMBADInfo.from_query(target, form.name.data)
        db.session.add(si)
        db.session.commit()
        redirect(form.prev.data)
    return redirect(form.prev.data)