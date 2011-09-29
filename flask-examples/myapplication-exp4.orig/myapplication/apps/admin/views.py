# -*- coding:utf-8 -*-

"""
Admin mockup. Slightly inspired in django-admin but fewer options.
Basically you register your model within admin_models dictionary and
that's it. This should not be used in production as it has no 
authentication backend with it.

author: italo maia
date: 30/07/2010
"""

from database import db

from apps.auth.models import User
from apps.auth.forms import UserForm

from apps.frontend.models import Page
from apps.frontend.forms import PageForm

from flask import Module, render_template, url_for, redirect, \
    flash, request

app = Module(__name__, 'admin', url_prefix="/admin")

admin_models = {
    "User":{"model":User, "name":User.__name__, "form":UserForm},
    "Page":{"model":Page, "name":Page.__name__, "form":PageForm}
}

@app.route("/")
def index():
    return render_template("admin/index.html", admin_models=admin_models)

@app.route("/<model_name>/create", methods=["GET", "POST"])
def create(model_name):
    admin_model = admin_models[model_name]
    model = admin_model["model"]
    form_cls = admin_models[model_name]["form"]
    
    if request.method=="POST":
        form = form_cls(request.form)
        
        if form.validate():
            obj = model(**form.data)
            db.session.add(obj)
            db.session.commit()
            flash('New %s added.' % model_name)
            return redirect(url_for('admin.list', model_name=model_name))
    else: form = form_cls()
    return render_template("admin/create.html", form=form,
        admin_model=admin_model)

@app.route("/<model_name>/edit/<ident>", methods=["GET", "POST"])
def edit(model_name, ident):
    admin_model = admin_models[model_name]
    model = admin_model["model"]
    form_cls = admin_models[model_name]["form"]
    obj = model.query.get_or_404(ident)
    
    if request.method=="POST":
        form = form_cls(request.form)
        
        if form.validate():
            for k, v in form.data.items():
                setattr(obj, k, v)
            db.session.add(obj)
            db.session.commit()
            flash('New %s edited.' % model_name)
            return redirect(url_for('admin.index'))
    else: form = form_cls(**obj.__dict__)
    return render_template("admin/edit.html", form=form, obj=obj, 
        admin_model=admin_model)

@app.route("/<model_name>/remove/<ident>", methods=["GET", "POST"])
def remove(model_name, ident):
    admin_model = admin_models[model_name]
    model = admin_model["model"]
    obj = model.query.get_or_404(ident)
    
    if request.method=="POST":
        db.session.delete(obj)
        db.session.commit()
        flash('%s removed.' % model_name)
        return redirect(url_for('admin.index'))
    
    return render_template("admin/delete.html", obj=obj, 
        admin_model=admin_model)

@app.route("/<model_name>/list")
def list(model_name):
    "Lists all records within a model"
    admin_model = admin_models[model_name]
    model = admin_model["model"]
    queryset = model.query.all()
    queryset_count = model.query.count()
    return render_template("admin/list.html", admin_model=admin_model, 
        queryset=queryset, queryset_count=queryset_count)
