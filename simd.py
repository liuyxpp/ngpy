#!/usr/bin/env python

from pickle import loads
from multiprocessing import Process

from redis import Redis

from ngpy.ngrun import ngrun, ngabort

def queue_daemon(redis,qkey):
    jobs = {}
    while 1:
        msg = redis.blpop(qkey)
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
    # In production mode, 
    # the 'console' and 'simQ' should be provided in the command line.
    redis = Redis('console')
    queue_daemon(redis,'simQ')

