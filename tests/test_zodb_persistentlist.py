#!/usr/bin/env python

import copy
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
from persistent.list import PersistentList
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

acclist=[]
a1=Account()
acclist.append(a1)
a2=Account()
acclist.append(a2)
a2.deposit(10.0)
#acclist1=copy.deepcopy(acclist)
pacclist1 = PersistentList(acclist)
root['account-list-1'] = pacclist1
transaction.commit()

acclist[0].deposit(11.0)
acclist[1].deposit(22.0)
a3 = Account()
acclist.append(a3)
#acclist2=copy.deepcopy(acclist)
pacclist2 = PersistentList(acclist)
root['account-list-2'] = pacclist2
transaction.commit()

