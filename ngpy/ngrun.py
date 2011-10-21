#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    ngrun.py
    ~~~~~~~~

    ngrun.py is a python script to run the actual MC simulation for
    nucleation and growth in the web mode.

    The data are stored in a ZODB database, shared with the ngmc website

    :copyright: (c) 2011 by Yi-Xin Liu (liuyxpp@gmail.com).
    :license: BSD, see LICENSE for more details.
"""
import math
import sys
import uuid
import copy

import numpy as np

import transaction
from BTrees import IOBTree
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping

from .particle import Particle
from .vector2d import Vector2D
from .ngofflattice_kooi import Param as FileParam
from .ngofflattice_kooi import calc_num_nucleation
from .ngofflattice_kooi import particle_SM_nucleation,particle_SM_growth

from .ngzodb import connect_zodb,setup_simulation
from .ngutil import now2str

def ngrun(zodb_URI,sim_id):
    db = connect_zodb(zodb_URI)
    sim_uuid = uuid.UUID(sim_id)
    simulations = db['simulations']
    simulation = simulations[sim_uuid]
    p = simulation['parameter']

    #UPDATE and ABORT are not handled Currently
    #Only NEW simulation can be run
    if not simulation['status'] == 'NEW':
        return

    o_M = Vector2D(p.lx/2,p.ly/2)
    particle_MA = Particle(o_M,p.r_seed,p.r_seed,0,p.k_MA,p.nu_MA)
    particle_seed = Particle(o_M,p.r_seed,p.r_seed,0,0,0)
    particle_SM_active = []
    particle_SM_inactive = []
    area_untransformed = []
    dn = 0

    simulation['run_time'] = now2str()
    simulation['status'] = 'ACTIVE'
    simulation['particle_seed'] = particle_seed
    transaction.commit()

    if not simulation.has_key('frames'):
        simulation['frames'] = IOBTree.IOBTree()
        transaction.commit()
    frames = simulation['frames']
    for i,t in np.ndenumerate(np.arange(p.dt,p.max_t+p.dt,p.dt)):
        if 2 * particle_MA.r > p.lx:
            break
        index, = i

        I_SM = p.n_SM
        dn = calc_num_nucleation(p.dt,I_SM,area_untransformed,
                                 particle_MA,particle_seed,
                                 particle_SM_active,particle_SM_inactive)
        N = len(particle_SM_active) + len(particle_SM_inactive)
        if dn > 0 and particle_MA.r - p.r_seed > p.r_test:
            particle_SM_nucleation(t,dn,p.r_test,
                                   p.r0_SM,p.k_SM,p.nu_SM,
                                   particle_MA,particle_seed,
                                   particle_SM_active,particle_SM_inactive)
        rr = 0.0
        for pc in particle_SM_active:
            rr += pc.r
        rr *= p.k_SM
        dr = (p.k_MA * p.dt - rr * p.dt / particle_MA.r -
              dn * p.r0_SM * p.r0_SM / (2 * particle_MA.r))
        particle_MA.grow_by_dr(dr)

        particle_SM_growth(t,particle_SM_active,particle_seed,
                           particle_SM_active,particle_SM_inactive)

        frame = PersistentMapping({
            'particle_MA':copy.deepcopy(particle_MA),
            'particle_SM_active':PersistentList(particle_SM_active),
            'particle_SM_inactive':PersistentList(particle_SM_inactive)
            })
        try:
            frames[index] = frame
            transaction.commit()
        except KeyboardInterrupt:
            transaction.abort()
            simulation['status'] = 'ABORT'
            simulation['abort_time'] = now2str()
            transaction.commit()
            sys.exit(0)

    simulation['status'] = 'FINISH'
    simulation['finish_time'] = now2str()
    transaction.commit()
    return


def ngabort(zodb_URI,sim_id):
    db = connect_zodb(zodb_URI)
    sim_uuid = uuid.UUID(sim_id)
    simulations = db['simulations']
    simulation = simulations[sim_uuid]
    if simulation['status'] == 'ACTIVE':
        simulation['status'] = 'ABORT'
        simulation['abort_time'] = now2str()
        transaction.commit()


if __name__ == '__main__':
    params = FileParam('ngrc.ini')
    db = connect_zodb(params.database)
    sim_id = None
    if not db.has_key('simulations'):
        sim_id = setup_simulation(params)
    simulations = db['simulations']
    if not len(simulations):
        sim_id = setup_simulation(params)
    for k in simulations.keys():
        simulation = simulations[k]
        if simulation['status'] == 'NEW':
            sim_id = k
            break
    if sim_id is None:
        sim_id = setup_simulation(params)

    ngrun(sim_id)

