# -*- coding:utf-8 -*-
import inspect
from .models import User, Page

__all__ = sorted(name for name, obj in locals().items() \
    if not (name.startswith('_') or inspect.ismodule(obj)))


def create_tables(db):
    _globals = globals()
    for varname in __all__:
        model = _globals[varname]
        model.metadata.create_all(db.engine)
