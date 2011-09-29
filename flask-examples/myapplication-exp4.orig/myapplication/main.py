# -*- coding:utf-8 -*-

"""
    main.py
    ~~~~~~~
    author: italo maia
    date: 30/07/2010

    Creates and configures the application and database. 
    Error page handling is done here for simplicity.
"""

from flask import Flask
from flask import render_template
from flaskext.sqlalchemy import SQLAlchemy

installed = ['auth', 'frontend', 'admin']

app = Flask(__name__)
app.config.from_object('config.Dev')# loads config.py

db = SQLAlchemy(app)

# == Error Handling ==
@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500


@app.errorhandler(404) # page not found
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(401) # access denied
def access_denied(error):
    return render_template("401.html"), 401


def load_module(m):
    "Importing module at runtime"
    return __import__("apps.%s.views" % m, fromlist=["app"])

def load_models(m):
    "Importing models at runtime"
    models_namespace = __import__('apps.%s.models' % m, fromlist='*')

def create_app(app):
    """Register all modules under app"""
    
    for m in installed:
        app.register_module(load_module(m).app)
    
    return app

def create_db(db):
    """Makes all models visible for db.create_all()"""
    for m in installed:
        try: load_models(m)
        except ImportError, e: print e, "for %s" % m
    db.create_all()
