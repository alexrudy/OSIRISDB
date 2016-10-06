from flask import render_template
from ..application import app, db

@app.route("/")
def home():
    """Generic Homepage for OSIRISDB"""
    return render_template("home.html")