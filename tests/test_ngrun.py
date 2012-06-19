#!/usr/bin/env python

from ngpy.ngrun import ngrun
from ngpy.ngzodb import connect_zodb, create_zodb, setup_simulation
from ngpy.ngofflattice_kooi import Param as FileParam

params = FileParam('ngpy/ngrc.ini')
db = connect_zodb(params.database)
if not db.has_key('simulations'):
    create_zodb(params.database)
sim_id = setup_simulation(db, params)
    
ngrun(params.database, str(sim_id))

