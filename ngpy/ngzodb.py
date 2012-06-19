#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    ngzodb.py
    ~~~~~~~~

    ngrun.py is a python module which contains ZODB related classes and helpler functions

    TODO: Currently the storage of particles in ZODB is inefficient.
          1. Rewrite the Particle object?
          2. Use another database?

    :copyright: (c) 2011 by Yi-Xin Liu (liuyxpp@gmail.com).
    :license: BSD, see LICENSE for more details.
"""
import uuid
import math
import datetime
import copy
from pickle import dumps

from zodburi import resolve_uri
from ZODB.DB import DB
import transaction
from persistent import Persistent
from persistent.mapping import PersistentMapping
from BTrees import IOBTree, OOBTree

from ngpy import app, db

from .particle import Particle
from .vector2d import Vector2D
from .ngofflattice_kooi import Param as FileParam

from .ngutil import now2str,str2time

SIMULATION_PARAMETERS = [('lx','lx'),('ly','ly'),
                         ('Lx','Lx'),('Lx','Lx'),
                         ('dt','dt'),('Nx','Nx'),
                         ('max_t','max_t'),('k_MA','k_MA'),
                         ('nu_MA','nu_MA'),('k_SM','k_SM'),
                         ('nu_SM','nu_SM'),('n_SM','n_SM'),
                         ('r0_SM','r0_SM'),
                         ('r_seed','r_seed'),('r_test','r_test')]

CHANGEABLE_SIM_PARAM = [('lx','lx'),('Lx','Lx'),('dt','dt'),
                        ('max_t','max_t'),('k_MA','k_MA'),
                        ('nu_MA','nu_MA'),('k_SM','k_SM'),
                        ('nu_SM','nu_SM'),('n_SM','n_SM'),
                        ('r_seed','r_seed'),('r_test','r_test')]

SIMULATION_STATUS = [('NEW','NEW'),('UPDATE','UPDATE'),
                  ('ACTIVE','ACTIVE'),('FINISH','FINISH'),
                  ('ABORT','ABORT'),('all','All')]


SIMULATION_TIME = [('create_time','create_time'),
                   ('update_time','update_time'),
                   ('run_time','run_time'),
                   ('finish_time','finish_time'),
                   ('abort_time','abort_time')]

SIMULATION_CMD = [('RUN','RUN'),('ABORT','ABORT')]

def connect_zodb(zodb_URI):
    storage_factory,dbkw = resolve_uri(zodb_URI)
    storage = storage_factory()
    db = DB(storage,**dbkw)
    conn = db.open()
    return conn.root()


def create_zodb(zodb_URI):
    ''' zodb_URI example:
            zeo://localhost:1234
    '''

    db = connect_zodb(zodb_URI)
    if not db.has_key('simulations'):
        db['simulations'] = OOBTree.OOBTree()
    if not db.has_key('sim_groups'):
        db['sim_groups'] = OOBTree.OOBTree()
    transaction.commit()
    # setup predefined groups
    groups = db['sim_groups']
    setup_group(db,'TEST','lyx',None,'Simulation group for testing')
    setup_group(db,'STANDARD','lyx',None,'A standard simulation group')


def setup_group(db,name,owner,batchvar,description=''):
    groups = db['sim_groups']
    if groups.has_key(name):
            return False
    group = PersistentMapping({
        'owner':owner,
        'batchvar':batchvar,
        'description':description
        })
    groups[name] = group
    db['sim_groups']=groups
    transaction.commit()
    return True


def update_group(db,name,batchvar):
    groups = db['sim_groups']
    if groups.has_key(name):
        group = groups[name]
        group['batchvar'] = batchvar
        db['sim_groups']=groups
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


def find_simulations_by_group(db,gname,is_sort=False,is_reverse=False):
    groups = db['sim_groups']
    if not groups.has_key(gname):
        return None
    group = groups[gname]
    batchvar = group['batchvar']
    group_simulations = []
    simulations = db['simulations']
    for sim_uuid in simulations.keys():
        simulation = simulations[sim_uuid]
        if simulation['group'] == gname:
            group_simulations.append((str(sim_uuid),simulation))
    if is_sort:
        group_simulations.sort(
            key=lambda x:getattr(x[1]['parameter'],batchvar),
            reverse=is_reverse)
    return group_simulations


# TODO: Add sort fuctionality
def find_simulations(db,form):
    results = []
    simulations = db['simulations']
    for sim_uuid,simulation in simulations.items():
        if form.name.data != '' and simulation['name'] != form.name.data:
            continue
        if form.group.data != 'all' and simulation['group'] != form.group.data:
            continue
        if form.status.data != 'all' and simulation['status'] != form.status.data:
            continue
        # parameters
        params = simulation['parameter']
        param_in_range = True
        for k,v in CHANGEABLE_SIM_PARAM:
            is_set = getattr(getattr(form,'set_'+k),('data'))
            if is_set:
                val = getattr(params,k)
                val_min = getattr(getattr(form,'from_'+k),'data')
                val_max = getattr(getattr(form,'to_'+k),'data')
                # ignore the wrong query
                if val_min > val_max:
                    continue
                if val < val_min or val > val_max:
                    param_in_range = False
                    break
        if not param_in_range:
            continue
        # times
        sim_in_time = True
        for k,v in SIMULATION_TIME:
            is_set = getattr(getattr(form,'set_'+k),('data'))
            if is_set:
                time = str2time(simulation[k])
                time_min = getattr(getattr(form,'from_'+k),'data')
                time_max = getattr(getattr(form,'to_'+k),'data')
                if time is None:
                    sim_in_time = False
                    break
                # ignore the wrong query
                if time_min > time_max:
                    continue
                if time < time_min or time > time_max:
                    sim_in_time = False
                    break
        if not sim_in_time:
            continue
        results.append((str(sim_uuid),simulation))
    return results


def execute_simulation(redis,sim_id):
    qkey = app.config['REDIS_QUEUE_KEY']
    key = '%s:%s' % (qkey,sim_id)
    cmd = 'RUN'
    zodb = app.config['ZODB_STORAGE']
    s = dumps((key,cmd,zodb,sim_id))
    redis.rpush(qkey,s)


def cancel_simulation(redis,sim_id):
    qkey = app.config['REDIS_QUEUE_KEY']
    key = '%s:%s' % (qkey,sim_id)
    cmd = 'ABORT'
    zodb = app.config['ZODB_STORAGE']
    s = dumps((key,cmd,zodb,sim_id))
    redis.rpush(qkey,s)


#def Particles(Persistent):
#    def __init__(self):
#        self._particles = IOBTree.IOBTree()


def get_batch_value(sim_id, batchvar):
    sim_uuid = uuid.UUID(sim_id)
    params = db['simulations'][sim_uuid]['parameter']
    return getattr(params,batchvar)


def get_ti(simulation):
    if not simulation.has_key('t_i'):
        return 0
    return simulation['t_i']


def get_simulation(sim_id):
    ''' sim_id is a uuid4 string. '''
    simulations = db['simulations']
    sim_uuid = uuid.UUID(sim_id)
    if not simulations.has_key(sim_uuid):
        return None
    return simulations[sim_uuid]


def get_num_frames(simulation):
    if not simulation.has_key('frames'):
        return 0
    return len(simulation['frames'])


def get_frame(simulation, frame_id):
    if not simulation.has_key('frames'):
        return None
    frames = simulation['frames']
    if not frames.has_key(frame_id):
        return None
    return frames[frame_id]


def get_frame_max(simulation):
    if not simulation.has_key('frames'):
        return -1
    frames = simulation['frames']
    return frames.maxKey()


def get_frame_interval(simulation):
    param = get_parameter(simulation)
    return param.interval_save


def get_particle_MA(simulation, frame):
    if not simulation.has_key('particle_MA'):
        raise ValueError('Error: simulation does not have particle_MA.')
    pm = copy.deepcopy(simulation['particle_MA'])
    pm.r = get_particle_MA_r(frame)
    return pm 


def get_particle_seed(simulation):
    if not simulation.has_key('particle_seed'):
        raise ValueError('Error: simulation does not have particle_seed.')
    return simulation['particle_seed']


def get_particle_SM_list_global(simulation):
    if not simulation.has_key('particle_SM'):
        raise ValueError('Error: simulation does not have particle_SM.')
    return simulation['particle_SM']


def get_parameter(simulation):
    if not simulation.has_key('parameter'):
        raise ValueError('Error: simulation does not have parameter.')
    return simulation['parameter']


def get_particle_SM_list_frame(frame):
    if not frame.has_key('SM'):
        raise ValueError('Error: frame does not have particle_SM list.')
    return frame['SM']


def get_t(frame):
    if not frame.has_key('t'):
        raise ValueError('Error: frame does not have t.')
    return frame['t']


def get_particle_MA_r(frame):
    if not frame.has_key('r_MA'):
        raise ValueError('Error: frame does not have r_MA.')
    return frame['r_MA']


def get_SM_particle_list(simulation, frame):
    SM_list_g = get_particle_SM_list_global(simulation)
    pid_list = get_particle_SM_list_frame(frame)
    t = get_t(frame)
    if not pid_list:
        return ([], [])

    pa = []
    pi = []
    for pid in pid_list:
        if SM_list_g.has_key(pid):
            p = copy.deepcopy(SM_list_g[pid])
            if p.te > 0 and (t - p.te) > 1e-6:
                p.grow_by_function(p.te)
                pi.append(p)
            else:
                p.grow_by_function(t)
                pa.append(p)
        else:
            pass
            #raise ValueError('particle in frame is not in global list.')
    return (pa, pi)


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


