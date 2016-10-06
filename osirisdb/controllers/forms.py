# -*- coding: utf-8 -*-

from wtforms.fields import Field
from flask_wtf import FlaskForm
from wtforms_alchemy import ModelForm, model_form_factory
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

__all__ = ['Form', 'QuerySelectField', 'QuerySelectMultipleField']

Form = model_form_factory(base=FlaskForm)
