# -*- coding:utf-8 -*-

"""
Database models for auth and frontend using sqlalchemy.
author: italo maia
date: 30/07/2010
"""
from main import db
from sqlalchemy import Column, String, Text, Boolean, Integer
from werkzeug import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__="auth_users"
    username = Column(String(30), primary_key=True)
    pw_hash = Column(String(80))
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def get_pk(self): return self.username
    
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)
    
    def __repr__(self):
        return self.username
    
    password = property(fset=set_password)
