# -*- coding:utf-8 -*-

"""
Database models for auth and frontend using sqlalchemy.
author: italo maia
date: 30/07/2010
"""

from main import db
from flask import Markup
from sqlalchemy import Column, String, Text, Boolean, Integer


class Page(db.Model):
    """ Page model for frontend """
    __tablename__="frontend_page"
    id = Column(Integer, primary_key=True)
    show_in_menu = Column(Boolean, default=False)
    pagename = Column(String(100))
    content = Column(Text, nullable=True, default=None)
    
    def __init__(self, show_in_menu, pagename, content=None, ):
        self.pagename = pagename
        self.content = content
        self.show_in_menu = show_in_menu
    
    def __repr__(self):
        return self.pagename
    
    def get_pk(self): return self.id
    
    def to_html(self):
        return Markup(self.content or 'No content defined.')



