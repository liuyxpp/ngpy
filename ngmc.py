#!/usr/bin/env python

from flask import Flask
from flaskext.zodb import ZODB
from redis import Redis

app = Flask(__name__)
app.config.from_object('config.Dev')
app.config.from_envvar('NGPY_SETTINGS',silent=True)

db = ZODB(app)

redis = Redis(app.config['REDIS_HOST'])

from views import *

if __name__ == "__main__":
    app.run(host='0.0.0.0')

