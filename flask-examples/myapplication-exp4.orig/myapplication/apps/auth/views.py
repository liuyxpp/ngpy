# -*- coding:utf-8 -*-

"""
    views.py
    ~~~~~~~~
    author: italo maia
    date: 30/07/2010

Simple module for auth. It allows one to sign in the application. It 
is not very safe, tough.
"""

from flask import Module, render_template, url_for, redirect, flash, \
    request, session

from datetime import datetime
from blinker import Namespace

# here we create our custom signal. 
auth_signals = Namespace()
login_accepted = auth_signals.signal('login_accepted') 

from database import db
from .models import User

app = Module(__name__, 'auth', url_prefix="/auth")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username and password:
            user = User.query.get(username)
            if user is not None:
                if user.check_password(password):
                    session['logged_in'] = True
                    
                    flash('You were logged in')
                    # our signal is sent when someone logs in
                    # we give as argument the time of the log in.
                    login_accepted.send(user, time=datetime.now())
                    return redirect('/')
                else: error = 'Password does not match.'
            else:
                error = 'Informed `user` does not exist.'
        else: error = 'Inform username AND password.'
    return render_template('auth/login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect('/')

# this simple method will just tell as what time the sender (User)
# logged in
def log(sender, time):
    print "%s logged at %s" % (unicode(sender), unicode(time))

# we make sure log is listening to the signal
login_accepted.connect(log)
