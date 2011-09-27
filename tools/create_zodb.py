#!/usr/bin/env python

'''
    Create a zodb database storage file.
'''

import sys
import os
from ZODB import FileStorage, DB

if len(sys.argv) < 2:
    zodbfs = 'test.fs'
else:
    zodbfs = sys.argv[1]
if os.path.exists(zodbfs):
    print "WARNING: file %s exists!" % zodbfs
    exit()

storage = FileStorage.FileStorage(zodbfs)
db = DB(storage)
conn = db.open()
root = conn.root()
conn.close()

