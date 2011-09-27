#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    ngzodb.py
    ~~~~~~~~

    ngrun.py is a python module which contains ZODB related classes and helpler functions

    :copyright: (c) 2011 by Yi-Xin Liu (liuyxpp@gmail.com).
    :license: BSD, see LICENSE for more details.
"""
import uuid
import math
import datetime

import ZODB.config
import transaction
from persistent import Persistent
from persistent.mapping import PersistentMapping
from BTrees import IOBTree,OOBTree

from particle import Particle
from vector2d import Vector2D
from ngofflattice_kooi import Param as FileParam

def connect_zodb(zodb_URI):
    db = ZODB.config.databaseFromURL(zodb_URI)
    return db.open()


def setup_simulation(dbconn,params):
    dbroot = dbconn.root()
    if not dbroot.has_key('simulations'):
        dbroot['simulations'] = OOBTree.OOBTree()
        transaction.commit()

    sim_id = uuid.uuid4()
    simulations = dbroot['simulations']
    simulation = PersistentMapping({
        'parameter':params,
        'status':'READY',
        'create_time':datetime.datetime.now()
        })
    simulations[sim_id] = simulation
    transaction.commit()
    return sim_id


def Particles(Persistent):
    def __init__(self):
        self._particles = IOBTree.IOBTree()


def test():
    print 'Setup a simulation to run.'
    params = FileParam('ngrc.ini')
    zodb_URI = params.database
    dbconn = connect_zodb(zodb_URI)
    sim_id = setup_simulation(dbconn,params)
    dbconn.close()
    print 'Delete the simulation which is just created'
    dbconn = connect_zodb(zodb_URI)
    dbroot = dbconn.root()
    del dbroot[sim_id]
    transaction.commit()
    dbconn.close()


if __name__ == '__main__':
    test()


