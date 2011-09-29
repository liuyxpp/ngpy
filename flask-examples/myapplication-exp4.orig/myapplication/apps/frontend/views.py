# -*- coding:utf-8 -*-

"""
    views.py
    ~~~~~~~~
    author: italo maia
    date: 30/07/2010
    
    Simple example for rendering a page with content.
"""

from .models import Page
from flask import Module, render_template, url_for, redirect

app = Module(__name__, 'frontpage')

@app.route("/")
@app.route("/show/<int:page_id>")
def index(page_id=None):
    queryset = Page.query.all()
    queryset_count = Page.query.count()
    
    show_in_menu = Page.query.filter(Page.show_in_menu==True)
    in_menu_count = show_in_menu.count()
    
    page = page_id is not None and Page.query.get(page_id) or None
    return render_template("index.html", page=page,
        show_in_menu=show_in_menu, in_menu_count=in_menu_count,
        queryset=queryset, queryset_count=queryset_count)
