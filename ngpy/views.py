import uuid
from pickle import dumps
from time import time

from flask import make_response, render_template
from flask import request, redirect, url_for
from flask import jsonify, abort

from ngpy import app, db, redis
import numpy as np

from .forms import NewSimulationForm, SelectSimulationForm
from .forms import SearchSimulationForm, NewGroupForm
from .ngzodb import setup_simulation, update_simulation, del_simulation
from .ngzodb import find_simulations, setup_group, update_group
from .ngzodb import find_simulations_by_group
from .ngzodb import execute_simulation, cancel_simulation
from .ngzodb import get_simulation, get_parameter, get_frame
from .ngzodb import get_particle_seed
from .ngzodb import get_frame_max, get_frame_interval, get_num_frames
from .ngutil import FormParam, now2str
from .ngplot import render_simulation_frame, render_psd,calc_volume, calc_n
from .ngplot import render_volume, render_nucleation
from .ngplot import render_group_nucleation
from .ngplot import make_psdfile, make_nucfile, make_volfile
from .ngplot import make_tcfile, archive_group_data

@app.route('/',methods=['GET','POST'])
def index():
    simulations = db['simulations']
    groups = db['sim_groups']
    new_simulations = []
    active_simulations = []
    finish_simulations = []
    abort_simulations = []
    for k in simulations.keys():
        simulation = simulations[k]
        if simulation['status'] in ('NEW','UPDATE'):
            new_simulations.append((str(k),simulation))
        if simulation['status'] == 'ACTIVE':
            active_simulations.append((str(k),simulation))
        if simulation['status'] == 'FINISH':
            finish_simulations.append((str(k),simulation))
        if simulation['status'] == 'ABORT':
            abort_simulations.append((str(k),simulation))
    return render_template(
        'index.html',
        groups = groups,
        new_simulations=new_simulations,
        active_simulations=active_simulations,
        finish_simulations=finish_simulations,
        abort_simulations=abort_simulations,
    )


@app.route('/error/',methods=['GET','POST'])
def error():
    return render_template('error.html',message=request.args.get('message'))


@app.route("/simple/<sim_id>")
def simple(sim_id):
    import StringIO

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure

    fig=Figure()
    ax=fig.add_subplot(111)
    t = np.arange(0.01, 10.0, 0.01)
    s1 = np.exp(t)
    ax.plot(t, s1, 'b-')

    canvas = FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route("/creategroup/",methods=['GET','POST'])
def new_group():
    form = NewGroupForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        owner = 'lyx'
        batchvar = form.batchvar.data
        description = form.description.data
        res = setup_group(db,name,owner,batchvar,description)
        if not res:
            return redirect(url_for('error',
                                    message='The group '+name+'exsits'))
        return redirect(url_for('index'))
    else:
        return render_template('newgroup.html',form=form)


@app.route("/group/",methods=['GET','POST'])
@app.route("/group/<gname>",methods=['GET','POST'])
def view_group():
    if request.method == 'POST':
        gname = request.form['groups']
    else:
        gname = request.args.get('groups')
    groups = db['sim_groups']
    if not groups.has_key(gname):
        return redirect(url_for("error",message="No group "+gname))
    group = groups[gname]
    batchvar = group['batchvar']
    group_simulations = find_simulations_by_group(db, gname, True)
    # find the max available frame number
    skey, s0 = group_simulations[0]
    dt = s0['parameter'].dt
    max_t = s0['parameter'].max_t
    frame_max = int(round(max_t/dt)) - 1
    frame_interval = get_frame_interval(s0)
    # number of frames for each simulation
    frame_list = {}
    for (sim_id,sim) in group_simulations:
        frame_list[sim_id] = get_num_frames(sim)
    return render_template("group.html",
                           gname=gname, group=group,
                           batchvar=batchvar,
                           frame_max=frame_max,
                           frame_interval=frame_interval,
                           framelist=frame_list,
                           number_simulations=len(group_simulations),
                           group_simulations=group_simulations
                          )


@app.route("/_groupfeed",methods=['GET','POST'])
def group_analysis_feed():
    gname = request.form['gname']
    batchvar = request.form['batchvar']
    sim_list = request.form['simlist']
    psdcheck = int(request.form['psdcheck']) # bool(u'0') is True! use int
    ncheck = int(request.form['ncheck'])
    volmcheck = int(request.form['volmcheck'])
    volscheck = int(request.form['volscheck'])
    voltcheck = int(request.form['voltcheck'])
    tccheck = int(request.form['tccheck'])
    n_type = request.form['ntype']
    frame_low = int(request.form['framelow'])
    frame_high = int(request.form['framehigh'])
    frame_interval = int(request.form['frameinterval'])
    # find the actual frame_high
    for sim_id in sim_list.split(","):
        simulation = get_simulation(sim_id)
        frame_cur = get_frame_max(simulation)
        if frame_cur < frame_high:
            frame_high = frame_cur
    user = 'lyx'
    qkey = user + ':' + gname + ':simulations'
    redis.set(qkey, sim_list)
    for sim_id in sim_list.split(","):
        if psdcheck:
            psdfile = make_psdfile(sim_id,
                                   frame_low, frame_high, frame_interval)
        if ncheck:
            nucfile = make_nucfile(sim_id, n_type,
                                   frame_low, frame_high, frame_interval)
        if volmcheck or volscheck or voltcheck:
            volfile = make_volfile(sim_id,
                                   frame_low, frame_high, frame_interval)
    if tccheck:
        tcfile = make_tcfile(sim_list, gname, batchvar)
    nsrc = ""
    volmsrc = ""
    volssrc = ""
    voltsrc = ""
    tcsrc = ""
    if ncheck:
        # add timestamp to enforce refreshing image
        nsrc = url_for("render_group_nucleation",
                       qkey=qkey, batchvar=batchvar, t=str(time()))
    if volmcheck:
        # add timestamp to enforce refreshing image
        volmsrc = url_for("render_group_volume",
                          voltype = 'volm',
                          qkey=qkey, batchvar=batchvar, t=str(time()))
    if volscheck:
        # add timestamp to enforce refreshing image
        volssrc = url_for("render_group_volume",
                          voltype='vols',
                          qkey=qkey, batchvar=batchvar, t=str(time()))
    if voltcheck:
        # add timestamp to enforce refreshing image
        voltsrc = url_for("render_group_volume",
                          voltype='volt',
                          qkey=qkey, batchvar=batchvar, t=str(time()))
    if tccheck:
        # add timestamp to enforce refreshing image
        tcsrc = url_for("render_group_tc",
                          datafile=tcfile, t=str(time()))
    datahref = "#"
    datatext = "At least select one term to analyze"
    if psdcheck or ncheck or volmcheck or volscheck or voltcheck or tccheck:
        datatext = archive_group_data(gname, batchvar, sim_list,
                                      psdcheck, ncheck, volmcheck,
                                      volscheck, voltcheck, tccheck)
        datahref = url_for("static", filename="tmp/"+datatext)
    return jsonify(volmsrc=volmsrc,
                   volssrc=volssrc,
                   voltsrc=voltsrc,
                   tcsrc=tcsrc,
                   nsrc=nsrc,
                   datahref=datahref,
                   datatext=datatext
                  )


@app.route("/create/",methods=['Get','POST'])
@app.route("/create/<sim_id>",methods=['Get','POST'])
def new_simulation(sim_id=None):
    if sim_id is None:
        simulation = None
    else:
        simulation = get_simulation(sim_id)
    if simulation is None:
        params = None
    else:
        params = get_parameter(simulation)
    form = NewSimulationForm(request.form, params)
    groups = db['sim_groups']
    form.group.choices = [(group,group) for group in groups.keys()]
    if request.method == 'POST':# and form.validate():
        params = FormParam(form)
        owner = 'lyx' # which should be modified after introduction of
                     # authentication
        name = form.name.data
        group = form.group.data
        sim_id = setup_simulation(db, params, name, owner, group)
        if form.mode.data:
            # batch_var is in
            # (lx,Lx,dt,max_t,k_MA,nu_MA,k_SM,nu_SM,n_SM,r_seed,r_seed)
            batch_var = form.batchvar.data
            update_group(db, group, batch_var)
            batch_step = form.batchstep.data
            batch_max = form.batchmax.data + batch_step
            batch_min = form.batchmin.data + batch_step
            for val in np.arange(batch_min, batch_max, batch_step):
                params.setval(batch_var, val)
                sim_id = setup_simulation(db, params, name, owner, group)
        return redirect(url_for('view_simulation', sim_id=sim_id))
    else:
        if params is not None:
            form.group.data = simulation['group']
        return render_template('new.html',form=form)


@app.route('/view/<sim_id>',methods=['GET','POST'])
def view_simulation(sim_id):
    simulation = get_simulation(sim_id)
    if simulation is None:
        return redirect(url_for('index'))
    num_frames = get_num_frames(simulation)
    update_time = simulation['update_time']
    run_time = simulation['run_time']
    abort_time = simulation['abort_time']
    finish_time = simulation['finish_time']
    return render_template(
        'view.html',
        sim_id=sim_id,
        name=simulation['name'],
        group=simulation['group'],
        params=simulation['parameter'],
        status=simulation['status'],
        create_time=simulation['create_time'],
        update_time=update_time,
        run_time=run_time,
        abort_time=abort_time,
        finish_time=finish_time,
        num_frames=num_frames
    )


@app.route("/edit/",methods=['GET','POST'])
def issue_edit():
    simulations = db['simulations']
    form = SelectSimulationForm(request.form)
    form.simulations.choices = [
        (str(sim_id),str(sim_id)) for sim_id in simulations.keys()]
    if request.method == 'POST': #form.validate_on_submit():
        sim_id = form.simulations.data
        return redirect(url_for('edit_simulation',sim_id=sim_id))
    else:
        return render_template('edit.html',form=form)


@app.route("/edit/<sim_id>",methods=['GET','POST'])
def edit_simulation(sim_id):
    simulation = get_simulation(sim_id)
    if simulation is None:
        return redirect(url_for('index'))
    if simulation['status'] not in ('NEW','UPDATE'):
        return redirect(url_for('index'))
    params = get_parameter(simulation)
    form = NewSimulationForm(request.form, params)
    groups = db['sim_groups']
    form.group.choices = [(group, group) for group in groups.keys()]
    if form.validate_on_submit():
        p = FormParam(form)
        update_simulation(db, sim_id, p, form.name.data, form.group.data)
        return redirect(url_for('view_simulation', sim_id=sim_id))
    else:
        form.name.data = simulation['name']
        form.group.data = simulation['group']
        return render_template('update.html',form=form)


@app.route("/delete/",methods=['GET','POST'])
def delete_simulation():
    simulations = db['simulations']
    form = SelectSimulationForm(request.form)
    form.simulations.choices = [
        (str(sim_id), str(sim_id)) for sim_id in simulations.keys()
        ]
    if request.method == 'POST':
        del_simulation(db, form.simulations.data)
        return redirect(url_for('delete_simulation'))
    else:
        return render_template('delete.html', form=form)


@app.route("/delete/<sim_id>")
def delete_by_id(sim_id):
    del_simulation(db, sim_id)
    return redirect(url_for('delete_simulation'))


@app.route("/simulations/",methods=['GET','POST'])
def select_simulation():
    simulations = db['simulations']
    new_simulations = []
    active_simulations = []
    for k in simulations.keys():
        if simulations[k]['status'] == 'NEW':
            new_simulations.append(str(k))
        if simulations[k]['status'] == 'ACTIVE':
            active_simulations.append(str(k))
    return render_template(
        'select.html',
        new_simulations=new_simulations,
        active_simulations=active_simulations,
    )


@app.route("/browse/<sim_id>",methods=['GET','POST'])
def browse_simulation(sim_id):
    simulation = get_simulation(sim_id)
    params = get_parameter(simulation)
    frame_max = get_frame_max(simulation)
    frame_interval = get_frame_interval(simulation)
    frame_id = eval(request.args.get('frame','0'))
    return render_template('browse.html', params=params,
                           sim_id=sim_id, frame_id=frame_id,
                           frame_max=frame_max, 
                           frame_interval=frame_interval)


@app.route("/_browsefeed",methods=['GET','POST'])
def browse_feed():
    sim_id = request.args.get("simid")
    frame_id = request.args.get("frame",0,type=int)
    simulation = get_simulation(sim_id)
    frame_max = get_frame_max(simulation)

    if frame_id < 0 or frame_id > frame_max:
        frame_id = -1
        return jsonify(imgsrc="",frame=frame_id)

    return jsonify(imgsrc=url_for("render_simulation_frame",
                                  sim_id=sim_id,frame=frame_id),
                   frame=frame_id
                  )


@app.route("/run/<sim_id>")
def run_simulation(sim_id):
    simulation = get_simulation(sim_id)
    if simulation is None:
        abort(404)
    if simulation['status'] not in ('NEW','UPDATE'):
        abort(404)
    execute_simulation(redis, sim_id)
    return redirect(url_for('live_simulation', sim_id=sim_id))


@app.route("/batchrun",methods=['GET','POST'])
def batch_run_simulation():
    simulations = db['simulations']
    last_run = None
    if request.method == 'POST':
        for sim_id in request.form.keys():
            simulation = get_simulation(sim_id)
            if simulation is None:
                continue
            if simulation['status'] in ('NEW','UPDATE'):
                execute_simulation(redis, sim_id)
                last_run = sim_id
        if last_run is None:
            return redirect(url_for('error', 
                                    message='No simulation executed in batch_run_simulation'))
        else:
            return redirect(url_for('live_simulation', sim_id=last_run))
    else:
        return redirect(url_for('error',
                                message='Only POST method is supported in batch_run_simulation'))


@app.route("/abort/<sim_id>")
def abort_simulation(sim_id):
    cancel_simulation(redis, sim_id)
    return redirect(url_for('view_simulation', sim_id=sim_id))


@app.route("/batchabort",methods=['POST'])
def batch_abort_simulation():
    simulations = db['simulations']
    last_abort = None
    if request.method == 'POST':
        for sim_id in request.form.keys():
            simulation = get_simulation(sim_id)
            if simulation is None:
                continue
            if simulation['status'] == 'ACTIVE':
                cancel_simulation(redis, sim_id)
                last_abort = sim_id
        if last_abort is None:
            return redirect(url_for('error',
                                    message='No simulation executed in batch_abort_simulation'))
        else:
            return redirect(url_for('view_simulation', sim_id=last_abort))
    else:
        return redirect(url_for('error',
                                message='Only POST method is supported in batch_abort_simulation'))


@app.route("/live/<sim_id>")
def live_simulation(sim_id):
    simulation = get_simulation(sim_id)
    params = get_parameter(simulation)
    if simulation['status'] != 'ACTIVE':
        return redirect(url_for('browse_simulation', sim_id=sim_id))
    return render_template('live.html',
                           sim_id=sim_id,
                           params=params)


@app.route("/_livefeed")
def live_feed():
    sim_id = request.args.get("simid")
    simulation = get_simulation(sim_id)
    params = get_parameter(simulation)
    frame_max = params.max_t / params.dt
    frame_interval = get_frame_interval(simulation)

    if simulation['status'] != 'ACTIVE':
        return jsonify(redirect=True,
                       url=url_for('browse_simulation',sim_id=sim_id))

    frame_id = get_frame_max(simulation)
    if frame_id == -1:
        return jsonify(imgsrc="")

    progress = (frame_id + 1) / frame_max
    progress = int(round(progress * 100))
    return jsonify(imgsrc=url_for("render_simulation_frame",
                                  sim_id=sim_id, frame=frame_id),
                   frame=frame_id, progress=progress
                  )


@app.route("/search",methods=['GET','POST'])
def search_simulation():
    form = SearchSimulationForm(request.form)
    groups = db['sim_groups']
    form.group.choices = [(group,group) for group in groups.keys()]
    form.group.choices.append(('all','All'))
    if request.method == 'POST': #and form.validate():
        results = find_simulations(db,form)
        return render_template('search_result.html',simulations = results)
    else:
        form.group.data = 'all'
        form.status.data = 'all'
        return render_template('search.html',form=form)


@app.route("/_psdfeed",methods=['GET','POST'])
def psd_feed():
    sim_id = request.args.get("simid")
    frame_id = request.args.get("frame",0,type=int)
    psd_type = request.args.get("psdtype",'density')
    simulation = get_simulation(sim_id)

    frame_max = get_frame_max(simulation)
    if frame_id < 0 or frame_id > frame_max:
        return jsonify(imgsrc="")

    return jsonify(imgsrc=url_for("render_psd",
                                  sim_id=sim_id,
                                  frame=frame_id,
                                  psdtype=psd_type,
                                  t=str(time()))
                  )


@app.route("/_volfeed",methods=['GET','POST'])
def volume_feed():
    sim_id = request.args.get("simid")
    frame_id = request.args.get("frame",0,type=int)
    simulation = get_simulation(sim_id)

    frame_max = get_frame_max(simulation)
    if frame_id < 0 or frame_id > frame_max:
        return jsonify(volm=0,vols=0,volt=0)

    frame = get_frame(simulation, frame_id)
    volm, vols, volt = calc_volume(simulation, frame)
    return jsonify(volm=volm, vols=vols, volt=volt)


@app.route("/_simvolfeed",methods=['GET','POST'])
def simulation_volume_feed():
    sim_id = request.args.get("simid")
    simulation = get_simulation(sim_id)

    frame_max = get_frame_max(simulation)
    frame_interval = get_frame_interval(simulation)
    frame_low = request.args.get("framelow", 0, type=int)
    frame_high = request.args.get("framehigh", frame_max, type=int)
    frame_interval = request.args.get("frameinterval",
                                      frame_interval, type=int)

    datafile = make_volfile(sim_id, frame_low, frame_high, frame_interval)
    return jsonify(imgsrc=url_for("render_volume",
                                  datafile=datafile, t=str(time())),
                   datahref=url_for("static", filename="tmp/"+datafile)
                  )


@app.route("/_nucfeed",methods=['GET','POST'])
def nucleation_feed():
    sim_id = request.args.get("simid")
    frame_id = request.args.get("frame",0,type=int)
    simulation = get_simulation(sim_id)

    frame_max = get_frame_max(simulation)
    if frame_id < 0 or frame_id > frame_max:
        return jsonify(n=0)

    frame = get_frame(simulation, frame_id)
    n = calc_n(simulation, frame)
    return jsonify(n=n)


@app.route("/_simnucfeed",methods=['GET','POST'])
def simulation_nucleation_feed():
    sim_id = request.args.get("simid")
    simulation = get_simulation(sim_id)

    frame_max = get_frame_max(simulation)
    frame_interval = get_frame_interval(simulation)
    n_type = request.args.get("ntype",'density')
    frame_low = request.args.get("framelow", 0, type=int)
    frame_high = request.args.get("framehigh", frame_max, type=int)
    frame_interval = request.args.get("frameinterval", 
                                      frame_interval, type=int)

    datafile = make_nucfile(sim_id,n_type,
                            frame_low,frame_high,frame_interval)
    return jsonify(imgsrc=url_for("render_nucleation",
                                  datafile=datafile, t=str(time())),
                   datahref=url_for("static", filename="tmp/"+datafile)
                  )
