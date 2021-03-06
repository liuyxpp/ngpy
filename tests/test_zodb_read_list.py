#!/usr/bin/env python

class Account(object):
    def __init__(self):
        self.balance = 0.0

    def deposit(self,amount):
        self.balance += amount

    def cash(self,amount):
        assert amount < self.balance
        self.balance -= amount


from ZODB.FileStorage import FileStorage
from ZODB.DB import DB

storage = FileStorage('Data.fs')
db = DB(storage)
connection = db.open()
root = connection.root()

print root.keys()
print root.items()

print
print 'account-list-1:'
for aa in root['account-list-1']:
    print aa.__dict__
print

print 'account-list-2:'
for aa in root['account-list-2']:
    print aa.__dict__

