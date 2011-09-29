class Dev(object):
    DEBUG = True
    SECRET_KEY = 'this is a secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'

class Prd(object):
    DEBUG = False
    SECRET_KEY = 'hard to guess secret key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
