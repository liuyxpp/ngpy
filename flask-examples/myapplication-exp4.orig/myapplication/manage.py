# -*- coding:utf-8 -*-
from main import app, db, create_app, create_db

if __name__=="__main__":
    import sys
    args = sys.argv[1:]
    
    if "createdb" in args:
        create_db(db)
        print "Database tables created."
    elif "runserver" in args:
        create_app(app).run()
    else: 
        print "usage: %s [createdb|runserver|help]" % __file__ 
