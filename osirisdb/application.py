# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.ext.scss import Scss
from flask.ext.script import Manager

__all__ = ['app', 'db', 'cli']

BASENAME = __name__.split(".")[0]
app = Flask(BASENAME)
app.config.from_object(".".join([BASENAME, "conf"]))

db = SQLAlchemy(app)
cli = Manager(app)
scss = Scss(app)
scss.set_hooks()

@cli.command
def initdb():
    """Initialize the database."""
    db.create_all()
    
@cli.command
def routes():
    """Show routes"""
    print(app.url_map)