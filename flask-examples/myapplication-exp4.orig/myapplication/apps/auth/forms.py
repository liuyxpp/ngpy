# -*- coding:utf-8 -*-

"""
    forms.py
    ~~~~~~~~
    Application forms used in admin.
    
    author: italo maia
    date: 30/07/2010
"""

from wtforms import Form, validators, TextField, PasswordField

class UserForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=30)])
    password = PasswordField('Password', [validators.Length(min=4, max=30)])
