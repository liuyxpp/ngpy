#!/usr/bin/env python

from flask import Flask
from flaskext.zodb import ZODB
from redis import Redis

app = Flask(__name__)
app.config.from_object('ngpy.config.Dev')
app.config.from_envvar('NGPY_CONFIG',silent=True)

db = ZODB(app)

redis = Redis(app.config['REDIS_HOST'])

import ngpy.views

