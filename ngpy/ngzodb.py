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
import copy

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


def create_zodb(zodb_URI):
    db = connect_zodb(zodb_URI)
    if not db.has_key('simulations'):
        db['simulations'] = OOBTree.OOBTree()
    if not db.has_key('sim_groups'):
        db['sim_groups'] = OOBTree.OOBTree()
    # setup predefined groups
    groups = db['sim_groups']
    groups['test'] = 'Simulation group for testing'
    groups['std'] = 'A standard simulation group'
    db['sim_groups'] = groups
    transaction.commit()


def setup_simulation(db,params,name='',owner='',group='test'):
    sim_id = uuid.uuid4()
    simulations = db['simulations']
    simulation = PersistentMapping({
        'name':name,
        'owner':owner,
        'group':group,
        'parameter':copy.deepcopy(params),
        'status':'NEW',
        'create_time':now2str(),
        'update_time':None,
        'run_time':None,
        'finish_time':None,
        'abort_time':None
        })
    simulations[sim_id] = simulation
    transaction.commit()
    return sim_id


def update_simulation(db,sim_id,params,name=None,group=None):
    sim_uuid = uuid.UUID(sim_id)
    simulations = db['simulations']
    if not simulations.has_key(sim_id):
        return
    simulation = simulations[sim_id]
    simulation['parameter'] = params
    if name:
        simulation['name'] = name
    if group:
        simulation['group'] = group
    simulation['status'] = 'UPDATE'
    simulation['update_time'] = now2str()
    simulations[sim_id] = simulation
    transaction.commit()


def del_simulation(db,sim_id):
    sim_uuid = uuid.UUID(sim_id)
    simulations = db['simulations']
    if simulations.has_key(sim_uuid):
        simulation = simulations[sim_uuid]
        if simulation['status'] != 'ACTIVE':
            del simulations[sim_uuid]
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


