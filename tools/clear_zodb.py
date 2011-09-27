#!/usr/bin/env python

'''
    Clear a zodb database.
'''
import sys
import transaction

from ZODB import DB
from zodburi import resolve_uri
from ZODB.POSException import ConflictError

if len(sys.argv) < 2:
    print 'Nothing has been done since no ZODB database provided!'
    sys.exit()

storage_factory,dbkw = resolve_uri(sys.argv[1])
storage = storage_factory()
db = DB(storage,**dbkw)
conn = db.open()
root = conn.root()

t = 0

if len(root.keys()) > 0:
    retry = 0
    for k in root.keys():
        while retry < 10:
            try:
                del root[k]
                transaction.commit()
            except ConflictError:
                retry += 1
                time.sleep(1)
                pass
            else:
                t += 1
                break
        else:
            conn.close()
            print "Error: transaction failed."
conn.close()
print t,"root items in database have been cleared."

