#!/usr/bin/env python

import os
import uuid

from flask import Flask, make_response
from flask import request, redirect, render_template, url_for
from flaskext.zodb import ZODB

app = Flask(__name__)
app.config.from_object('config.Dev')
app.config.from_envvar('NGPY_SETTINGS',silent=True)

db = ZODB(app)

from ngzodb import setup_simulation,update_simulation
from forms import SelectSimulationForm,NewSimulationForm
from ngutil import FormParam

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        db['shoutout'] = request.form['message']
        return redirect(url_for('index'))
    else:
        message = db.get('shoutout','Be the first to shout!')
        return render_template('index.html',message=message)


@app.route("/hello")
def hello():
    return "Hello World!"


@app.route("/simple.png")
def simple():
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


@app.route("/create",methods=['Get','POST'])
def new_simulation():
    form = NewSimulationForm()
    simulations = db['simulations']
    if form.validate_on_submit():
        params = FormParam(form)
        sim_id = setup_simulation(db,params)
        return redirect(url_for('browse_simulation',sim_id=sim_id))
    else:
        return render_template('new.html',form=form)


@app.route("/edit",methods=['GET','POST'])
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
        return redirect(url_for('browse_simulation',sim_id=sim_id))
    else:
        return render_template('update.html',form=form)


@app.route("/delete",methods=['GET','POST'])
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


@app.route("/select",methods=['GET','POST'])
def select_simulation():
    form = SelectSimulationForm()
    simulations = db['simulations']
    if request.method == 'POST':
        sim_id = form.simulations.data
        return redirect(url_for('browse_simulation',sim_id=sim_id))
    else:
        form.simulations.choices = [
            (str(sim_id),str(sim_id)) for sim_id in simulations.keys()
            ]
        return render_template('select.html',form=form)


@app.route("/simulations/<sim_id>")
def browse_simulation(sim_id):
    simulations = db['simulations']
    simulation = simulations[uuid.UUID(sim_id)]
    return simulation['status']


@app.route("/live")
def live_simulation():
    return 'Live Simulation'


if __name__ == "__main__":
    app.run()

