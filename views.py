import multiprocessing
import os
import signal
import uuid

from flask import make_response, render_template
from flask import request, redirect, url_for

from ngmc import app, jobs
from database import db

from forms import SelectSimulationForm, NewSimulationForm
from ngrun import ngrun
from ngzodb import setup_simulation, update_simulation
from ngutil import FormParam, now2str
from ngplot import render_simulation_frame

@app.route('/',methods=['GET','POST'])
def index():
    simulations = db['simulations']
    new_simulations = []
    active_simulations = []
    for k in simulations.keys():
        if simulations[k]['status'] == 'NEW':
            new_simulations.append(str(k))
        if simulations[k]['status'] == 'ACTIVE':
            active_simulations.append(str(k))
    return render_template(
        'index.html',
        new_simulations=new_simulations,
        active_simulations=active_simulations,
    )


@app.route("/simple/<sim_id>")
def simple(sim_id):
    import numpy as np
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


@app.route("/create/",methods=['Get','POST'])
def new_simulation():
    form = NewSimulationForm()
    simulations = db['simulations']
    if form.validate_on_submit():
        params = FormParam(form)
        sim_id = setup_simulation(db,params)
        return redirect(url_for('view_simulation',sim_id=sim_id))
    else:
        return render_template('new.html',form=form)

@app.route('/view/<sim_id>',methods=['GET','POST'])
def view_simulation(sim_id):
    simulations = db['simulations']
    sim_uuid = uuid.UUID(sim_id)
    if not simulations.has_key(sim_uuid):
        return redirect(url_for('index'))
    simulation = simulations[sim_uuid]
    num_frames = 0
    if simulation.has_key('frames'):
        num_frames = len(simulation['frames'])
    update_time = None
    if simulation.has_key('update_time'):
        update_time = simulation['update_time']
    run_time = None
    if simulation.has_key('run_time'):
        run_time = simulation['run_time']
    abort_time = None
    if simulation.has_key('abort_time'):
        abort_time = simulation['abort_time']
    finish_time = None
    if simulation.has_key('finish_time'):
        finish_time = simulation['finish_time']
    return render_template(
        'view.html',
        sim_id=sim_id,
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
    form = SelectSimulationForm()
    simulations = db['simulations']
    if request.method == 'POST':
        sim_id = form.simulations.data
        return redirect(url_for('edit_simulation',sim_id=sim_id))
    else:
        form.simulations.choices = [
            (str(sim_id),str(sim_id)) for sim_id in simulations.keys()
            ]
        return render_template('edit.html',form=form)


@app.route("/edit/<sim_id>",methods=['GET','POST'])
def edit_simulation(sim_id):
    simulations = db['simulations']
    sim_uuid = uuid.UUID(sim_id)
    params = None
    if simulations.has_key(sim_uuid):
        simulation = simulations[sim_uuid]
        params = simulation['parameter']
    form = NewSimulationForm(request.form,params)
    if form.validate_on_submit():
        p = FormParam(form)
        update_simulation(db,sim_uuid,p)
        return redirect(url_for('view_simulation',sim_id=sim_id))
    else:
        return render_template('update.html',form=form)


@app.route("/delete/",methods=['GET','POST'])
def delete_simulation():
    form = SelectSimulationForm()
    simulations = db['simulations']
    if request.method == 'POST':
        sim_id = uuid.UUID(form.simulations.data)
        if simulations.has_key(sim_id):
            del simulations[sim_id]
        return redirect(url_for('delete_simulation'))
    else:
        form.simulations.choices = [
            (str(sim_id),str(sim_id)) for sim_id in simulations.keys()
            ]
        return render_template('delete.html',form=form)


@app.route("/delete/<sim_id>")
def delete_by_id(sim_id):
    simulations = db['simulations']
    sim_uuid = uuid.UUID(sim_id)
    if simulations.has_key(sim_uuid):
        del simulations[sim_uuid]
    return redirect("select_simulation")


@app.route("/simulations/",methods=['GET','POST'])
def select_simulation():
    form = SelectSimulationForm()
    simulations = db['simulations']
    if request.method == 'POST':
        sim_id = form.simulations.data
        return redirect(url_for('view_simulation',sim_id=sim_id))
    else:
        form.simulations.choices = [
            (str(sim_id),str(sim_id)) for sim_id in simulations.keys()
            ]
        return render_template('select.html',form=form)


@app.route("/browse/<sim_id>")
def browse_simulation(sim_id):
    simulations = db['simulations']
    simulation = simulations[uuid.UUID(sim_id)]
    frame_id = eval(request.args.get('frame','0'))
    frame_max = len(simulation['frames']) - 1
    return render_template('browse.html',
                           params=simulation['parameter'],
                           sim_id=sim_id,frame_id=frame_id,
                           frame_max=frame_max)


@app.route("/run/<sim_id>")
def run_simulation(sim_id):
    #sim_uuid = uuid.UUID(sim_id)
    p = multiprocessing.Process(target=ngrun,
                                args=(app.config['ZODB_STORAGE'],sim_id,))
    p.start()
    jobs[sim_id] = p
    return redirect(url_for('live_simulation',sim_id=sim_id))


@app.route("/abort/<sim_id>")
def abort_simulation(sim_id):
    simulations = db['simulations']
    sim_uuid = uuid.UUID(sim_id)
    simulation = simulations[sim_uuid]
    if jobs.has_key(sim_id):
        job = jobs.pop(sim_id)
        if job.is_alive():
            #os.kill(job.pid,signal.SIGINT)
            job.terminate()
            job.join()
        if not job.is_alive() and simulation['status'] == 'ACTIVE':
            simulation['status'] = 'ABORT'
            simulation['abort_time'] = now2str()
    return redirect(url_for('index'))


@app.route("/live/<sim_id>")
def live_simulation(sim_id):
    simulations = db['simulations']
    simulation = simulations[uuid.UUID(sim_id)]
    if simulation['status'] != 'ACTIVE' and simulation['status'] != 'NEW':
        return redirect(url_for('browse_simulation',sim_id=sim_id))
    if not simulation.has_key('frames'):
        frame_id = -1
        return render_template('live.html',
                           params=simulation['parameter'],
                           sim_id=sim_id,frame_id=frame_id)
    frame_id = len(simulation['frames']) - 1
    return render_template('live.html',
                           params=simulation['parameter'],
                           sim_id=sim_id,frame_id=frame_id)

