# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_scss import Scss
from flask_script import Manager

__all__ = ['app', 'db']

BASENAME = __name__.split(".")[0]
app = Flask(BASENAME)
app.config.from_object(".".join([BASENAME, "conf"]))

db = SQLAlchemy(app)
scss = Scss(app)
scss.set_hooks()

@app.cli.command()
def initdb():
    """Initialize the database."""
    db.create_all()
    
@app.cli.command()
def routes():
    """Show routes"""
    print(app.url_map)