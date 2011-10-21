#!/usr/bin/env python

from zodburi import resolve_uri
from ZODB.DB import DB

zodb_URI = 'zeo://console:1234'

storage_factory, dbkw = resolve_uri(zodb_URI)
storage = storage_factory()
db = DB(storage,**dbkw)
conn = db.open()
dbroot = conn.root()

print dbroot.keys()

