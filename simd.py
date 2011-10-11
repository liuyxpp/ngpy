#!/usr/bin/env python

from pickle import loads
from multiprocessing import Process

from ngrun import ngrun, ngabort

def queue_daemon(app,redis):
    jobs = {}
    while 1:
        msg = redis.blpop(app.config['REDIS_QUEUE_KEY'])
        key, cmd, zodb_uri, sim_id = loads(msg[1])
        if cmd == 'RUN':
            if not jobs.has_key(sim_id):
                p = Process(target=ngrun, args=(zodb_uri,sim_id))
                jobs[sim_id] = p
                p.start()
                print "RUN: %s" % sim_id
        elif cmd == 'ABORT':
            if jobs.has_key(sim_id):
                p = jobs[sim_id]
                p.terminate()
                p.join()
                ngabort(zodb_uri,sim_id)
                del jobs[sim_id]
                print "ABORT: %s" % sim_id


if __name__ == '__main__':
    from ngmc import app,redis
    queue_daemon(app,redis)

