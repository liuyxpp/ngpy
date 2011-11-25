#!/usr/bin/env python

from flask import Flask,render_template
from flaskext.zodb import ZODB
from redis import Redis

app = Flask(__name__)
app.config.from_object('ngpy.config.Dev')
app.config.from_envvar('NGPY_CONFIG',silent=True)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

db = ZODB(app)

redis = Redis(app.config['REDIS_HOST'])

import ngpy.views

