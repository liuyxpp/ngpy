# -*- coding: utf-8 -*-
"""
    ngplot.py
    ~~~~~~~~

    ngplot.py is a python script which contains the rendering functions for
    simulation lattice.

    :copyright: (c) 2011 by Yi-Xin Liu (liuyxpp@gmail.com).
    :license: BSD, see LICENSE for more details.
"""
import uuid

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as colormap
import StringIO

from flask import request, make_response
from ngpy import app,db

GRAY_M = 63
GRAY_SEED = 255
GRAY_INACTIVE = 223
GRAY_ACTIVE_BASE = 95
GRAY_ACTIVE_STEP = 2

@app.route("/render/<sim_id>")
def render_simulation_frame(sim_id):
    simulations = db['simulations']
    sim_uuid = uuid.UUID(sim_id)
    if not simulations.has_key(sim_uuid):
        return "Error: No simulation " + sim_id + "."
    simulation = simulations[sim_uuid]
    if not simulation.has_key('frames'):
        return "Error: simulation " + sim_id + " does not have any frames."
    frames = simulation['frames']
    frame_id = eval(request.args.get('frame','0'))
    if not frames.has_key(frame_id):
        return "Error: simulation " + sim_id + " does not have frame"+str(frame_id)+"."
    frame = frames[frame_id]

    p = simulation['parameter']
    ps = simulation['particle_seed']
    pm = frame['particle_MA']
    pa = frame['particle_SM_active']
    pi = frame['particle_SM_inactive']

    lattice = np.zeros((p.Lx,p.Ly),int)
    number_active_max = (GRAY_INACTIVE -  GRAY_ACTIVE_BASE) / GRAY_ACTIVE_STEP
    pm.draw_on_lattice(GRAY_M,p.lx,p.ly,lattice)
    ps.draw_on_lattice(GRAY_SEED,p.lx,p.ly,lattice)
    for i,particle in enumerate(pa):
        particle.draw_on_lattice(i*GRAY_ACTIVE_STEP+GRAY_ACTIVE_BASE,
                          p.lx,p.ly,lattice)
    for i,particle in enumerate(pi):
        particle.draw_on_lattice(GRAY_INACTIVE,p.lx,p.ly,lattice)

    fig=Figure()
    ax=fig.add_subplot(111)
    ax.imshow(lattice,cmap=colormap.gray,vmin=0,vmax=255)

    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

