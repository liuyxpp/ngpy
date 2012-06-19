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
from .ngofflattice_kooi import particle_SM_nucleation, particle_SM_growth

from .ngzodb import connect_zodb, setup_simulation
from .ngzodb import get_simulation, get_parameter
from .ngutil import now2str

def save_frame(frames, SM_list_g, index, t, pa, pi, pm, p_new, p_stop):
    # Update global list
    for p in p_new:
        SM_list_g[p.ID] = p
        transaction.commit()

    for p in p_stop:
        if SM_list_g.has_key(p.ID):
            SM_list_g[p.ID].te = t
            transaction.commit()
        else:
            raise ValueError('Error: stopping particle is not in global list.')

    # Add new frame
    SM_list = [p.ID for p in pa + pi]
    frame = PersistentMapping({
                        't':t,
                        'r_MA':pm.r,
                        'SM':PersistentList(SM_list),
                            })
    frames[index] = frame
    transaction.commit()


def ngrun(zodb_uri, sim_id):
    db = connect_zodb(zodb_uri)
    simulations = db['simulations']
    sim_uuid = uuid.UUID(sim_id)
    simulation = simulations[sim_uuid]
    param = get_parameter(simulation)
    lx = param.lx
    ly = param.ly
    dx = param.dx
    dy = param.dy
    k_MA = param.k_MA
    I_SM = param.n_SM
    k_SM = param.k_SM
    r0_SM = param.r0_SM
    nu_SM = param.nu_SM
    dt = param.dt
    max_t = param.max_t
    r_seed = param.r_seed
    r_test = param.r_test
    interval_save = param.interval_save

    #UPDATE and ABORT are not handled Currently
    #Only NEW and UPDATE simulation can be run
    if simulation['status'] not in ('NEW','UPDATE'):
        return

    o_M = Vector2D(param.lx/2, param.ly/2)
    particle_MA = Particle(o_M, param.r_seed, param.r_seed, 
                           0, param.k_MA, param.nu_MA)
    particle_seed = Particle(o_M, param.r_seed, param.r_seed, 0, 0, 0)
    particle_SM_active = []
    particle_SM_inactive = []
    area_untransformed = []
    dn = 0

    simulation['run_time'] = now2str()
    simulation['status'] = 'ACTIVE'
    simulation['particle_seed'] = particle_seed
    simulation['particle_MA'] = particle_MA
    simulation['particle_SM'] = PersistentMapping({})
    ti = 2.0 * r_test / k_MA
    particle_MA.r = r_seed + 2 * r_test
    simulation['t_i'] = ti
    transaction.commit()
    SM_list_global = simulation['particle_SM']

    if not simulation.has_key('frames'):
        simulation['frames'] = IOBTree.IOBTree()
        transaction.commit()
    frames = simulation['frames']
    for i,t in np.ndenumerate(np.arange(ti + param.dt, 
                                        param.max_t + param.dt, param.dt)):
        if 2 * particle_MA.r > lx or 2 * particle_MA.r > ly:
            break
        index, = i

        dn = calc_num_nucleation(dt, I_SM, area_untransformed,
                                 particle_MA,particle_seed,
                                 particle_SM_active,particle_SM_inactive)
        #N1 = len(particle_SM_active)
        #N2 = len(particle_SM_inactive)
        N = len(particle_SM_active) + len(particle_SM_inactive)
        #print index,dn,N,N1,N2,particle_MA.r,particle_MA.r-r_seed - 2*r_test
        p_new = []
        if dn > 0 and particle_MA.r - r_seed > 2 * r_test:
            max_try = int(lx*ly/(dx*dy))
            p_new = particle_SM_nucleation(t, dn, r_test,
                                    r0_SM, k_SM, nu_SM,
                                    particle_MA, particle_seed,
                                    particle_SM_active, 
                                    particle_SM_inactive, max_try)
            #print dn

        dn = len(p_new) # the actual nucleated particle
        rr = 0.0
        for pc in particle_SM_active:
            rr += pc.r
        rr *= k_SM
        dr = k_MA * dt - rr * dt / particle_MA.r
        if N > 0 and dn > 0:
            dr -= dn * r0_SM * r0_SM / (2 * particle_MA.r)
        # The first occurence of nuclei may lead dr < 0,
        # which should be avoided
        if (N == 0 and dr > 0) or (N > 0):
            particle_MA.grow_by_dr(dr)

        p_stop = particle_SM_growth(t, particle_MA, particle_seed,
                                    particle_SM_active, 
                                    particle_SM_inactive)

        if p_new or p_stop or (index % interval_save == 0):
            try:
                save_frame(frames, SM_list_global, index, t,
                           particle_SM_active, particle_SM_inactive,
                           particle_MA, p_new, p_stop)
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

