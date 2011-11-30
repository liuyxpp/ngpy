# -*- coding: utf-8 -*-
"""
    ngplot.py
    ~~~~~~~~

    ngplot.py is a python script which contains the rendering functions for
    simulation lattice.

    :copyright: (c) 2011 by Yi-Xin Liu (liuyxpp@gmail.com).
    :license: BSD, see LICENSE for more details.
"""
import os
import csv
import uuid

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as colormap
import StringIO

from flask import request, make_response
from ngpy import app,db

from .ngofflattice_kooi import calc_area_M

GRAY_M = 63
GRAY_SEED = 255
GRAY_INACTIVE = 223
GRAY_ACTIVE_BASE = 95
GRAY_ACTIVE_STEP = 2

TMP_PATH = os.path.dirname(__file__) + "/static/tmp/"

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
    for i,particle in pa.iteritems():
        particle.draw_on_lattice(i*GRAY_ACTIVE_STEP+GRAY_ACTIVE_BASE,
                          p.lx,p.ly,lattice)
    for i,particle in pi.iteritems():
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


@app.route("/_psd/<sim_id>")
def render_psd(sim_id):
    psd_type = request.args.get('psdtype')
    frame_id = request.args.get('frame',0,type=int)
    simulations = db['simulations']
    sim_uuid = uuid.UUID(sim_id)
    if not simulations.has_key(sim_uuid):
        return "Error: No simulation " + sim_id + "."
    simulation = simulations[sim_uuid]
    if not simulation.has_key('frames'):
        return "Error: simulation " + sim_id + " does not have any frames."
    frames = simulation['frames']
    if not frames.has_key(frame_id):
        return "Error: simulation " + sim_id + " does not have frame"+str(frame_id)+"."
    frame = frames[frame_id]

    p = simulation['parameter']
    pa = frame['particle_SM_active']
    pi = frame['particle_SM_inactive']
    diameters = []
    for ipa in pa.values():
        if 2 * ipa.r > 0:
            diameters.append(2*ipa.r)
    for ipi in pi.values():
        if 2 * ipi.r >0:
            diameters.append(2*ipi.r)

    if diameters:
        bins = np.arange(0,500,20)
        fig=Figure()
        ax=fig.add_subplot(111)
        if psd_type == 'density':
            ax.hist(diameters,bins,normed=True)
        else:
            ax.hist(diameters,bins)
        ax.axis([-100,500,0,25])

        canvas = FigureCanvas(fig)
        png_output = StringIO.StringIO()
        canvas.print_png(png_output)
        response = make_response(png_output.getvalue())
        response.headers['Content-Type'] = 'image/png'
        return response
    else:
        return "Error: simulation " + sim_id + " does not have any particles."


def calc_volume(frame,ps):
    pm = frame['particle_MA']
    pa = frame['particle_SM_active']
    pi = frame['particle_SM_inactive']

    area_M = 1e-6 * calc_area_M(pm,ps,pa.values(),pi.values())
    area_MA = 1e-6 * np.pi * pm.r**2
    area_seed = 1e-6 * np.pi * ps.r**2
    area_SM = area_MA - area_seed - area_M
    vol_MA = area_M * 1.0 # because rho_MA=1.0
    vol_SM = area_SM * 2.0 # because rho_SM=2.0
    vol_total = vol_MA + vol_SM
    return vol_MA,vol_SM,vol_total


# TODO: make the full range and interval=1 file to cache the result
#       Next the same request will return directly
#       render_volume will use the existing file to retieve data
def make_volfile(sim_id,frame_low,frame_high,frame_interval):
    simulations = db['simulations']
    sim_uuid = uuid.UUID(sim_id)
    simulation = simulations[sim_uuid]
    frames = simulation['frames']

    p = simulation['parameter']
    ps = simulation['particle_seed']
    frame_list = range(frame_low,frame_high+1,frame_interval)
    data_list = []
    for frame_id in frame_list:
        t = (frame_id + 1) * p.dt # t start from dt
        frame = frames[frame_id]
        volm,vols,volt = calc_volume(frame,ps)
        data_list.append((t,volm,vols,volt))
    datafile = sim_id + '-vol.csv'
    datapath = TMP_PATH + datafile
    with open(datapath,'wb') as f:
        writer = csv.writer(f)
        writer.writerows(data_list)
    return datafile


@app.route("/_volume")
def render_volume():
    datafile = request.args.get('datafile')
    datapath = TMP_PATH + datafile
    t_list = []
    volm_list = []
    vols_list = []
    volt_list = []
    with open(datapath,"rb") as f:
        reader = csv.reader(f)
        for row in reader:
            t, volm, vols, volt = row
            t_list.append(t)
            volm_list.append(volm)
            vols_list.append(vols)
            volt_list.append(volt)

    fig=Figure()
    ax=fig.add_subplot(111)
    ax.plot(t_list,volm_list,'b-')
    ax.plot(t_list,vols_list,'r-')
    ax.plot(t_list,volt_list,'g-')

    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


def calc_n(frame):
    pa = frame['particle_SM_active']
    pi = frame['particle_SM_inactive']

    return len(pa)+len(pi)


def make_nucfile(sim_id,n_type,frame_low,frame_high,frame_interval):
    simulations = db['simulations']
    sim_uuid = uuid.UUID(sim_id)
    simulation = simulations[sim_uuid]
    frames = simulation['frames']

    p = simulation['parameter']
    ps = simulation['particle_seed']
    aseed = 1e-6 * np.pi * ps.r**2
    frame_list = range(frame_low,frame_high+1,frame_interval)
    data_list = []
    for frame_id in frame_list:
        t = (frame_id + 1) * p.dt # t start from dt
        frame = frames[frame_id]
        n = calc_n(frame)
        if n_type == 'density':
            pm = frame['particle_MA']
            am = 1e-6 * np.pi * pm.r**2
            n = n / (am - aseed)
        data_list.append((t,n))
    datafile = sim_id + '-nuc.csv'
    datapath = TMP_PATH + datafile
    with open(datapath,'wb') as f:
        writer = csv.writer(f)
        writer.writerows(data_list)
    return datafile


@app.route("/_nucleation")
def render_nucleation():
    datafile = request.args.get('datafile')
    datapath = TMP_PATH + datafile
    t_list = []
    n_list = []
    with open(datapath,"rb") as f:
        reader = csv.reader(f)
        for row in reader:
            t, n = row
            t_list.append(t)
            n_list.append(n)

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(t_list,n_list,'o')

    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

