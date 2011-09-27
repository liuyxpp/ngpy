#!/usr/bin/env python

from flask import Flask, make_response
from flask import request, redirect, render_template, url_for
from flaskext.zodb import ZODB

app = Flask(__name__)
#app.config['ZODB_STORAGE'] = 'file:///export/home/lyx/opt/lyx/web/ngmc.fs'
app.config['ZODB_STORAGE'] = 'zconfig://' + app.root_path + '/zeo.conf'

db = ZODB(app)

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


if __name__ == "__main__":
    app.debug = True
    app.run()

