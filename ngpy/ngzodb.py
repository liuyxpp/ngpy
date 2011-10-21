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

from zodburi import resolve_uri
from ZODB.DB import DB
import transaction
from persistent import Persistent
from persistent.mapping import PersistentMapping
from BTrees import IOBTree,OOBTree

from .particle import Particle
from .vector2d import Vector2D
from .ngofflattice_kooi import Param as FileParam

from .ngutil import now2str

def connect_zodb(zodb_URI):
    storage_factory,dbkw = resolve_uri(zodb_URI)
    storage = storage_factory()
    db = DB(storage,**dbkw)
    conn = db.open()
    return conn.root()


def setup_simulation(db,params):
    if not db.has_key('simulations'):
        db['simulations'] = OOBTree.OOBTree()
        transaction.commit()

    sim_id = uuid.uuid4()
    simulations = db['simulations']
    simulation = PersistentMapping({
        'parameter':params,
        'status':'NEW',
        'create_time':now2str()
        })
    simulations[sim_id] = simulation
    transaction.commit()
    return sim_id


def update_simulation(db,sim_id,params):
    simulations = db['simulations']
    if not simulations.has_key(sim_id):
        return
    simulation = simulations[sim_id]
    simulation['parameter'] = params
    simulation['status'] = 'UPDATE'
    simulation['update_time'] = now2str()
    simulations[sim_id] = simulation
    transaction.commit()


def Particles(Persistent):
    def __init__(self):
        self._particles = IOBTree.IOBTree()


def test():
    print 'Setup a simulation to run.'
    params = FileParam('ngrc.ini')
    sim_id = setup_simulation(params)
    dbconn.close()
    print 'Delete the simulation which is just created'
    dbconn = connect_zodb(zodb_URI)
    dbroot = dbconn.root()
    del dbroot[sim_id]
    transaction.commit()
    dbconn.close()


if __name__ == '__main__':
    test()


