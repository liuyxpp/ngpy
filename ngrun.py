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
import uuid
import math
import datetime
import copy
import signal
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import ZODB.config
from ZODB.POSException import ConflictError
import transaction
from BTrees import IOBTree
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping

from particle import Particle
from vector2d import Vector2D
from ngofflattice_kooi import Param as FileParam
from ngofflattice_kooi import calc_area_M, calc_num_nucleation
from ngofflattice_kooi import is_in_particle_list, is_touch_particle
from ngofflattice_kooi import particle_SM_nucleation,particle_SM_growth

#from ngzodb import Particles # a Persistent object of list of particles
from ngzodb import connect_zodb,setup_simulation

def signal_handler(signum,frame):
    print "SIGINT received."
    transaction.abort()
    #dbconn = connect_zodb(zodb_URI)
    global dbconn
    dbroot = dbconn.root()
    simulations = dbroot['simulations']
    simulation = simulations[sim_id]
    retry = 0
    while retry < 3:
        try:
            simulation['status'] = 'ABORT'
            transaction.commit()
        except ConflictError:
            retry += 1
            time.sleep(1)
            pass
        else:
            break
    dbconn.close()
    print 'simulation:',sim_id,'status set to ABORT.'
    sys.exit(0)


def ngrun(dbconn,sim_id):
    dbroot = dbconn.root()
    simulations = dbroot['simulations']
    simulation = simulations[sim_id]
    p = simulation['parameter']

    o_M = Vector2D(p.lx/2,p.ly/2)
    particle_MA = Particle(o_M,p.r_seed,p.r_seed,0,p.k_MA,p.nu_MA)
    particle_seed = Particle(o_M,p.r_seed,p.r_seed,0,0,0)
    particle_SM_active = []
    particle_SM_inactive = []
    area_untransformed = []
    dn =0

    simulation['status'] = 'ACTIVE'
    transaction.commit()

    if not simulation.has_key('frames'):
        simulation['frames'] = IOBTree.IOBTree()
        transaction.commit()
    frames = simulation['frames']
    for i,t in np.ndenumerate(np.arange(p.dt,p.max_t,p.dt)):
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
            'particle_MA':particle_MA,
            'particle_SM_active':PersistentList(particle_SM_active),
            'particle_SM_inactive':PersistentList(particle_SM_inactive)
            })
        try:
            frames[index] = frame
            transaction.commit()
        except KeyboardInterrupt:
            transaction.abort()
            simulation['status'] = 'ABORT'
            transaction.commit()
            sys.exit(0)

    simulation['particle_seed'] = particle_seed
    simulation['status'] = 'FINISH'
    transaction.commit()


if __name__ == '__main__':
    params = FileParam('ngrc.ini')
    zodb_URI = params.database
    dbconn = connect_zodb(zodb_URI)
    sim_id = setup_simulation(dbconn,params)

    # handle the Ctrl + C interruption
    #signal.signal(signal.SIGINT,signal_handler)
    ngrun(dbconn,sim_id)
    dbconn.close()

