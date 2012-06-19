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
import tarfile
import uuid

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as colormap
import StringIO

from flask import request, make_response
from ngpy import app,db,redis

from .ngofflattice_kooi import calc_area_M
from .ngutil import Group, Parameters, GroupInfo
from .ngzodb import get_batch_value, get_simulation, get_frame
from .ngzodb import get_particle_MA, get_particle_seed
from .ngzodb import get_parameter, get_t, get_ti, get_particle_MA_r
from .ngzodb import get_particle_SM_list_global, get_particle_SM_list_frame
from .ngzodb import get_SM_particle_list

GRAY_M = 63
GRAY_SEED = 255
GRAY_INACTIVE = 223
GRAY_ACTIVE_BASE = 95
GRAY_ACTIVE_STEP = 2

TMP_PATH = os.path.dirname(__file__) + "/static/tmp/"

@app.route("/render/<sim_id>")
def render_simulation_frame(sim_id):
    simulation = get_simulation(sim_id)
    frame_id = eval(request.args.get('frame','0'))
    frame = get_frame(simulation, frame_id)

    p = get_parameter(simulation)
    ps = get_particle_seed(simulation)
    pm = get_particle_MA(simulation, frame)
    t = get_t(frame)

    # reconstruct particle_SM_active and particle_SM_inactive list
    pa, pi = get_SM_particle_list(simulation, frame)

    lattice = np.zeros((p.Lx, p.Ly), int)
    number_active_max = (GRAY_INACTIVE -  GRAY_ACTIVE_BASE) / GRAY_ACTIVE_STEP
    pm.draw_on_lattice(GRAY_M, p.lx, p.ly, lattice)
    ps.draw_on_lattice(GRAY_SEED, p.lx, p.ly, lattice)
    i = 0
    for particle in pa:
        particle.draw_on_lattice(i*GRAY_ACTIVE_STEP+GRAY_ACTIVE_BASE,
                                p.lx, p.ly, lattice)
        i += 1
    for particle in pi:
        particle.draw_on_lattice(GRAY_INACTIVE, p.lx, p.ly, lattice)

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.imshow(lattice, cmap=colormap.gray, vmin=0, vmax=255)

    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


def make_psd(simulation, frame):
    pa, pi = get_SM_particle_list(simulation, frame)
    diameters = []
    for ipa in pa:
        if 2 * ipa.r > 0:
            diameters.append(2*ipa.r)
    for ipi in pi:
        if 2 * ipi.r >0:
            diameters.append(2*ipi.r)
    return diameters

@app.route("/_psd/<sim_id>")
def render_psd(sim_id):
    psd_type = request.args.get('psdtype')
    frame_id = request.args.get('frame',0,type=int)
    simulation = get_simulation(sim_id)
    frame = get_frame(simulation, frame_id)

    diameters = make_psd(simulation, frame)
    if diameters:
        bins = np.arange(0,500,20)
        fig = Figure()
        ax = fig.add_subplot(111)
        if psd_type == 'density':
            ax.hist(diameters,bins,normed=True)
        else:
            ax.hist(diameters,bins)
        ax.axis([-100,500,0,25])
        ax.set_xlabel('$d$',size='x-large')
        if psd_type == 'density':
            ax.set_ylabel('$f(d)/n(t)$',size='x-large')
        else:
            ax.set_ylabel('$f(d)$',size='x-large')

        canvas = FigureCanvas(fig)
        png_output = StringIO.StringIO()
        canvas.print_png(png_output)
        response = make_response(png_output.getvalue())
        response.headers['Content-Type'] = 'image/png'
        return response
    else:
        raise ValueError('Error: simulation ' + sim_id + 
                         ' does not have any particles.')

# lastone: make only the last frame PSD
def make_psdfile(sim_id, frame_low, frame_high, frame_interval,
                 lastone=True):
    simulation = get_simulation(sim_id)

    data_list = []
    if lastone:
        frame_last = get_frame(simulation, frame_high)
        diameters = []
        if not frame_last is None:
            diameters = make_psd(simulation, frame_last)
        data_list.append(diameters)
    else:
        frame_list = range(frame_low, frame_high+1, frame_interval)
        for frame_id in frame_list:
            frame = get_frame(simulation, frame_id)
            diameters = []
            if not frame is None:
                diameters = make_psd(simulation, frame)
            data_list.append(diameters)
    datafile = sim_id + '-psd.csv'
    datapath = TMP_PATH + datafile
    with open(datapath,'wb') as f:
        writer = csv.writer(f)
        # NOTE: each psd-data will be saved as a row other than a column
        writer.writerows(data_list)
    return datafile


def calc_volume(simulation, frame):
    pm = get_particle_MA(simulation, frame)
    ps = get_particle_seed(simulation)
    pa, pi = get_SM_particle_list(simulation, frame)

    area_M = 1e-6 * calc_area_M(pm, ps, pa, pi)
    area_MA = 1e-6 * np.pi * pm.r**2
    area_seed = 1e-6 * np.pi * ps.r**2
    area_SM = area_MA - area_seed - area_M
    vol_MA = area_M * 1.0 # because rho_MA=1.0
    vol_SM = area_SM * 2.0 # because rho_SM=2.0
    vol_total = vol_MA + vol_SM
    return vol_MA, vol_SM, vol_total


# TODO: make the full range and interval=1 file to cache the result
#       Next the same request will return directly
#       render_volume will use the existing file to retieve data
def make_volfile(sim_id, frame_low, frame_high, frame_interval):
    simulation = get_simulation(sim_id)
    pm = simulation['particle_MA']
    p = get_parameter(simulation)
    ps = get_particle_seed(simulation)
    frame_list = range(frame_low, frame_high+1, frame_interval)
    ti = get_ti(simulation)
    data_list = []
    area_seed = 1e-6 * np.pi * ps.r**2
    for tt in np.arange(0, ti, frame_interval * p.dt):
        pm.grow_by_function(tt)
        area_MA = 1e-6 * np.pi * pm.r**2
        area_M = area_MA - area_seed
        volm = area_M * 1.0
        vols = 0
        volt = volm
        data_list.append((tt, volm, vols, volt))
    for frame_id in frame_list:
        t = ti + frame_id * p.dt # t starts from ti
        frame = get_frame(simulation, frame_id)
        volm, vols, volt = ([], [], [])
        if not frame is None:
            volm, vols, volt = calc_volume(simulation, frame)
        data_list.append((t, volm, vols, volt))
    datafile = sim_id + '-vol.csv'
    datapath = TMP_PATH + datafile
    with open(datapath, 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(data_list)
    return datafile


@app.route("/_volume")
def render_volume():
    datafile = request.args.get('datafile')
    datapath = TMP_PATH + datafile
    t_list, volm_list, vols_list, volt_list = ([], [], [], [])
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
    ax.plot(t_list,volm_list,'b-',label='$V(1)$')
    ax.plot(t_list,vols_list,'r-',label='$V(0)$')
    ax.plot(t_list,volt_list,'g-',label='$V_t$')
    handles,labels = ax.get_legend_handles_labels()
    ax.legend(handles,labels,loc='upper left')
    ax.set_xlabel('$t$',size='x-large')
    ax.set_ylabel('$V(t)$',size='x-large')

    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route("/_group_volume")
def render_group_volume():
    vol_type = request.args.get('voltype')
    qkey = request.args.get('qkey')
    batchvar = request.args.get('batchvar')
    fig = Figure()
    ax = fig.add_subplot(111)

    sim_list = redis.get(qkey)
    for sim_id in sim_list.split(","):
        batch_val = get_batch_value(sim_id, batchvar)
        datapath = TMP_PATH + sim_id + '-vol.csv'
        t_list = []
        vol_list = []
        with open(datapath,"rb") as f:
            reader = csv.reader(f)
            for row in reader:
                t, volm, vols, volt = row
                t_list.append(t)
                if vol_type == 'volm':
                    vol_list.append(volm)
                elif vol_type == 'vols':
                    vol_list.append(vols)
                else:
                    vol_list.append(volt)
        label = batchvar + " = " + str(batch_val)
        ax.plot(t_list, vol_list, label=label)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left')
    ax.set_xlabel('$t$', size='x-large')
    if vol_type == 'volm':
        ax.set_ylabel('$V(1)$', size='x-large')
    elif vol_type == 'vols':
        ax.set_ylabel('$V(0)$', size='x-large')
    else:
        ax.set_ylabel('$V_t$', size='x-large')
    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


def calc_n(simulation, frame):
    pa, pi = get_SM_particle_list(simulation, frame)
    return len(pa)+len(pi)


def make_nucfile(sim_id, n_type, frame_low, frame_high, frame_interval):
    simulation = get_simulation(sim_id)
    p = get_parameter(simulation)
    ps = get_particle_seed(simulation)
    aseed = 1e-6 * np.pi * ps.r**2
    frame_list = range(frame_low, frame_high+1, frame_interval)
    ti = get_ti(simulation)
    data_list = []
    for tt in np.arange(0, ti, frame_interval * p.dt):
        data_list.append((tt,0))
    for frame_id in frame_list:
        t = ti + frame_id * p.dt # t start from ti
        frame = get_frame(simulation, frame_id)
        n = 0
        if not frame is None:
            n = calc_n(simulation, frame)
        if n_type == 'density':
            pm = get_particle_MA(simulation, frame)
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
    t_list, n_list = ([], [])
    with open(datapath,"rb") as f:
        reader = csv.reader(f)
        for row in reader:
            t, n = row
            t_list.append(t)
            n_list.append(n)

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(t_list, n_list, marker='o', markeredgewidth=0)
    ax.set_xlabel('$t$', size='x-large')
    ax.set_ylabel('$n(t)/A(t)$', size='x-large')

    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route("/_group_nucleation")
def render_group_nucleation():
    qkey = request.args.get('qkey')
    batchvar = request.args.get('batchvar')
    fig = Figure()
    ax = fig.add_subplot(111)

    sim_list = redis.get(qkey)
    for sim_id in sim_list.split(","):
        batch_val = get_batch_value(sim_id,batchvar)
        datapath = TMP_PATH + sim_id + '-nuc.csv'
        t_list, n_list = ([], [])
        with open(datapath,"rb") as f:
            reader = csv.reader(f)
            for row in reader:
                t, n = row
                t_list.append(t)
                n_list.append(n)
        label = batchvar + " = " + str(batch_val)
        ax.plot(t_list,n_list,label=label,marker='o',markeredgewidth=0)

    handles,labels = ax.get_legend_handles_labels()
    ax.legend(handles,labels,loc='upper left')
    ax.set_xlabel('$t$',size='x-large')
    ax.set_ylabel('$n(t)/A(t)$',size='x-large')
    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


def archive_group_data(gname, batchvar, sim_list, psdcheck, volmcheck,
                       volscheck, voltcheck, ncheck):
    batchinfo = gname + "-" + batchvar + "-info.ini"
    psdfile = gname + "-psd-" + batchvar + ".csv"
    volmfile = gname + "-volm-" + batchvar + ".csv"
    volsfile = gname + "-vols-" + batchvar + ".csv"
    voltfile = gname + "-volt-" + batchvar + ".csv"
    nfile = gname + "-N-" + batchvar + ".csv"
    # datafile is an archive of all above files
    datafile = gname + "-" + batchvar + ".tar.bz2"
    # .ini file
    # TODO: ini file should also record the following info:
    #       1. each batch value
    #       2. frame_low, frame_high, frame_interval
    #       3. psdcheck, volmcheck, volscheck, voltcheck, and ncheck
    description = db['sim_groups'][gname]['description']
    group_section = Group(gname, batchvar, sim_list, description)
    simlist = sim_list.split(",")
    simulation = get_simulation(simlist[0])
    params = get_parameter(simulation)
    param_section = Parameters(params)
    group_info = GroupInfo(group_section,param_section)
    group_info.write(TMP_PATH+batchinfo)
    # data file
    psd_group_list = []
    volm_group_list = []
    vols_group_list = []
    volt_group_list = []
    n_group_list = []
    for sim_id in sim_list.split(","):
        if psdcheck:
            datapath = TMP_PATH + sim_id + '-psd.csv'
            with open(datapath,"rb") as f:
                reader = csv.reader(f)
                for row in reader:
                    psd_group_list.append(row)
        if volmcheck or volscheck or voltcheck:
            datapath = TMP_PATH + sim_id + '-vol.csv'
            with open(datapath,"rb") as f:
                reader = csv.reader(f)
                i = 1
                j = 1
                k = 1
                for row in reader:
                    t, volm, vols, volt = row
                    if volmcheck:
                        if len(volm_group_list) < i:
                            volm_group_list.append([t,volm])
                        else:
                            volm_group_list[i-1].append(volm)
                        i = i + 1
                    if volscheck:
                        if len(vols_group_list) < j:
                            vols_group_list.append([t,vols])
                        else:
                            vols_group_list[j-1].append(vols)
                        j = j + 1
                    if voltcheck:
                        if len(volt_group_list) < k:
                            volt_group_list.append([t,volt])
                        else:
                            volt_group_list[k-1].append(volt)
                        k = k + 1
        if ncheck:
            datapath = TMP_PATH + sim_id + '-nuc.csv'
            with open(datapath,"rb") as f:
                reader = csv.reader(f)
                i = 1
                for row in reader:
                    t, n = row
                    if len(n_group_list) < i:
                        n_group_list.append([t,n])
                    else:
                        n_group_list[i-1].append(n)
                    i = i + 1
    if psdcheck:
        with open(TMP_PATH + psdfile,"wb") as f:
            writer = csv.writer(f)
            writer.writerows(psd_group_list)
    if volmcheck:
        with open(TMP_PATH + volmfile,"wb") as f:
            writer = csv.writer(f)
            writer.writerows(volm_group_list)
    if volscheck:
        with open(TMP_PATH + volsfile,"wb") as f:
            writer = csv.writer(f)
            writer.writerows(vols_group_list)
    if voltcheck:
        with open(TMP_PATH + voltfile,"wb") as f:
            writer = csv.writer(f)
            writer.writerows(volt_group_list)
    if ncheck:
        with open(TMP_PATH + nfile,"wb") as f:
            writer = csv.writer(f)
            writer.writerows(n_group_list)

    with tarfile.open(TMP_PATH+datafile,"w:bz2") as tar:
        def resetini(tarinfo):
            tarinfo.name = batchinfo
            return tarinfo
        def resetpsd(tarinfo):
            tarinfo.name = psdfile
            return tarinfo
        def resetvolm(tarinfo):
            tarinfo.name = volmfile
            return tarinfo
        def resetvols(tarinfo):
            tarinfo.name = volsfile
            return tarinfo
        def resetvolt(tarinfo):
            tarinfo.name = voltfile
            return tarinfo
        def resetn(tarinfo):
            tarinfo.name = nfile
            return tarinfo
        tar.add(TMP_PATH+batchinfo,filter=resetini)
        if psdcheck:
            tar.add(TMP_PATH+psdfile,filter=resetpsd)
        if volmcheck:
            tar.add(TMP_PATH+volmfile,filter=resetvolm)
        if volscheck:
            tar.add(TMP_PATH+volsfile,filter=resetvols)
        if voltcheck:
            tar.add(TMP_PATH+voltfile,filter=resetvolt)
        if ncheck:
            tar.add(TMP_PATH+nfile,filter=resetn)
    return datafile

