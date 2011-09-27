#!/usr/bin/env python

import copy
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import transaction

class Account(object):
    def __init__(self):
        self.balance = 0.0

    def deposit(self,amount):
        self.balance += amount

    def cash(self,amount):
        assert amount < self.balance
        self.balance -= amount


storage = FileStorage('Data.fs')
db = DB(storage)
connection = db.open()
root = connection.root()

params={}
params['dx'] = 0.1
params['dy'] = 0.2
params['max_t'] = 10000

accdict={}

acclist=[]
a1=Account()
acclist.append(a1)
a2=Account()
acclist.append(a2)
a2.deposit(10.0)
acclist1=copy.deepcopy(acclist)
accdict['account-list-1'] = acclist1

acclist[0].deposit(11.0)
acclist[1].deposit(22.0)
a3 = Account()
acclist.append(a3)
acclist2=copy.deepcopy(acclist)
accdict['account-list-2'] = acclist2

simulation = {}
simulation['parameter'] = params
simulation['account-lists'] = accdict

root['simulation-xx'] = simulation
transaction.commit()

acclist[0].deposit(11.0)
acclist[1].deposit(22.0)
acclist[2].deposit(33.0)
a4 = Account()
acclist.append(a4)
acclist3=copy.deepcopy(acclist)
accdict['account-list-3'] = acclist3

root._p_changed = True
transaction.commit()

