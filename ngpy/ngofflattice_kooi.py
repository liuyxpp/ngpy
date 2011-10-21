#!/usr/bin/env python

"""
Off lattice Monte-Carlo simulation of nucleation and growth
Since 2011.8.19

Nucleation event is handled by a recursive procedure to maxmize the accuracy.

unstable phase (A, amorphous)
metastable phase (M, metastable)
stable phase (S, stable)
circular shape is assumed.
The particle stops growth when it touches at least one other particles.

REFERENCES:
    Pusztai, T; et al. PRB, 1998, 57, 14110
    Kooi, B. J. PRB, 2004, 70, 224108
    Kooi, B. J. PRB, 2006, 73, 54103

AUTHOUR:
    Yi-Xin Liu <liuyxpp@gmail.com>
    Fudan University

REVISION:
    2011.9.1

"""
import argparse
from ConfigParser import SafeConfigParser
import math
import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from persistent import Persistent

from .particle import Particle
from .vector2d import Vector2D


class Param(Persistent):
    def __init__(self,inifile):
        ini = SafeConfigParser()
        ini.read(inifile)
        # [Data]
        self.lx = eval(ini.get('Data','lx'))
        self.ly = eval(ini.get('Data','ly'))
        self.dx = eval(ini.get('Data','dx'))
        self.dy = eval(ini.get('Data','dy'))
        self.Lx = int(round(self.lx/self.dx))
        self.Ly = self.Lx
        self.dt = eval(ini.get('Data','dt'))
        self.Nx = int(round(eval(ini.get('Data','Nx'))))
        self.max_t = eval(ini.get('Data','max_t'))
        self.k_MA = eval(ini.get('Data','k_MA'))
        self.nu_MA = eval(ini.get('Data','nu_MA'))
        self.r0_SM = eval(ini.get('Data','r0_SM'))
        self.k_SM = eval(ini.get('Data','k_SM'))
        self.nu_SM = eval(ini.get('Data','nu_SM'))
        self.n_SM = eval(ini.get('Data','n_SM'))
        self.r_seed = eval(ini.get('Data','r_seed'))
        self.r_test = eval(ini.get('Data','r_test'))
        self.interval_sample = eval(ini.get('Data','interval_sample'))
        self.interval_show = eval(ini.get('Data','interval_show'))
        # [Program]
        self.exe_name = ini.get('Program','exe_name')
        self.exe_dir = ini.get('Program','exe_dir')
        self.database = ini.get('Program','database')
        self.base_dir = ini.get('Program','base_dir')


def calc_area_M(pm,ps,pa,pi):
    '''Since impingement is not allowed, we can safely caculate the area of
    metastable phase by
            area_M=area_particle_MA-area_seed-area_particle_SM_active-area_particle_SM_inactive
    '''
    area_M = pm.area()
    area_seed = ps.area()
    area_active = 0.0
    for p in pa:
        area_active += p.area()
    area_inactive = 0.0
    for p in pi:
        area_inactive += p.area()
    return (area_M - area_seed - area_active - area_inactive)


def calc_num_nucleation(dt,nSM,au,pm,ps,pa,pi):
    n_before = len(pa) + len(pi) #total nucleation events before this nucleation
    au_this = calc_area_M(pm,ps,pa,pi) * nSM * dt
    n_this = math.floor(sum(au) + au_this) - n_before
    au.append(au_this)
    return int(n_this)


def is_in_particle_list(pt,plist):
    for p in plist:
        if p.is_inner_point(pt):
            return True
    return False


def is_touch_particle(par,plist):
    for p in plist:
        if (not (p is par)) and  p.is_touch(par):
            return True
    return False


def particle_SM_nucleation(t,dn,r_test,r0,k,nu,pm,ps,pa,pi):
    n = int(dn)
    x_low_limit = pm.o.x-pm.r
    x_high_limit = pm.o.x+pm.r
    y_low_limit = pm.o.y-pm.r
    y_high_limit = pm.o.y+pm.r
    for i in xrange(n):
        while True:
            x = np.random.uniform(x_low_limit,x_high_limit)
            y = np.random.uniform(y_low_limit,y_high_limit)
            test_pt = Vector2D(x,y)
            test_particle = Particle(o=test_pt,r=r_test)
            if pm.is_inner_point(test_pt):
                #if not ps.is_inner_point(test_pt) and not is_in_particle_list (test_pt,pa) and not is_in_particle_list(test_pt,pi):
                if (not test_particle.is_touch(ps) and not
                    is_touch_particle(test_particle,pa) and not
                    is_touch_particle(test_particle,pi)):
                    pa.append(Particle(test_pt,r0,r0,t,k,nu))
                    break


def particle_SM_growth(t,pm,ps,pa,pi):
    pao = pa[:]
    pio = pi[:]
    for p in pao:
        p.grow_by_function(t)
        if (p.is_touch(ps) or is_touch_particle(p,pao) or
            is_touch_particle(p,pio)):
            pa.remove(p)
            pi.append(p)


def init_draw(lx,ly,dx,dy,ps):
    Lx = int(lx / dx)
    Ly = int(ly / dy)
    lattice = np.zeros((Lx,Ly),int)
    ps.draw_on_lattice(255,lx,ly,lattice)

    plt.ion()
    fig,((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2,figsize=(15,11.25))
    ax1.matshow(lattice,cmap=cm.gray,vmin=0,vmax=255)
    return fig,ax1,ax2,ax3,ax4


def draw_snap(ax,lx,ly,dx,dy,pm,ps,pa,pi):
    gray_M           = 63
    gray_seed        = 255
    gray_inactive    = 223
    gray_active_base = 95
    gray_active_step = 2

    number_active_max = (gray_inactive-gray_active_base) / gray_active_step
    Lx = int(lx / dx)
    Ly = int(ly / dy)
    lattice = np.zeros((Lx,Ly),int)
    pm.draw_on_lattice(gray_M,lx,ly,lattice)
    ps.draw_on_lattice(gray_seed,lx,ly,lattice)
    #if len(pa)+len(pi)>number_active_max:
        #print "Warning: too many metastable particles!"
    for i,p in enumerate(pa):
        p.draw_on_lattice(i*gray_active_step+gray_active_base,
                          lx,ly,lattice)
    for i,p in enumerate(pi):
        p.draw_on_lattice(gray_inactive,lx,ly,lattice)
    ax.clear()
    ax.matshow(lattice)
    plt.draw()


def draw_diameter_histogram(ax,pa,pi):
    diameters = []
    for p in pa:
        if 2 * p.r > 0:
            diameters.append(2 * p.r)
    for p in pi:
        if 2 * p.r > 0:
            diameters.append(2 * p.r)
    if diameters:
        bins = np.arange(0,500,20)
        ax.clear()
        ax.hist(diameters,bins)
        ax.axis([-100,500,0,25])
        plt.draw()


def run(args):
    if args.silent:
        import matplotlib
        matplotlib.use('Agg')

    pm = Param(args.param)
    lx           = pm.lx #7000.0 # nanometer
    ly           = pm.ly #lx # nanometer, simulation box (0,0)-(lx,ly)
    dx           = pm.dx #lx/512 # lattice size 512 x 512
    dy           = pm.dy #dx
    dt           = pm.dt #0.01 # time step, in minute
    Nx           = pm.Nx #int(round(1/dt))
    max_t        = pm.max_t #1000.0
    #k_MA        = 0.25e5
    k_MA         = pm.k_MA #0.012*dx/dt #0.26
    nu_MA        = pm.nu_MA #0.5
    r0_SM        = pm.r0_SM #dx/2 # the size of new born nucleus is exactly one pixel
    k_SM         = pm.k_SM #6.0 # 0.3*dx/(Nx*dt) # nm/min
    nu_SM        = pm.nu_SM #1.0
    n_SM         = pm.n_SM #6.0e-7 # 50/(lx*ly)
    r_seed       = pm.r_seed #1000.0
    r_test       = pm.r_test #20*r0_SM

    o_M = Vector2D(lx/2,ly/2)
    particle_MA = Particle(o_M,r_seed,r_seed,0,k_MA,nu_MA)
    particle_seed = Particle(o_M,r_seed,r_seed,0,0,0)
    particle_SM_active = []
    particle_SM_inactive = []
    t_list = []
    area_untransformed = [] # a list for area of untransformed M at time t
    number_density_nuclei = []
    vol_MA = []
    vol_SM = []
    vol_total = []
    dn = 0 # initial nucleation event

    fig,aximage,axhist,axVol,axN = init_draw(lx,ly,dx,dy,particle_seed)

    for i,t in np.ndenumerate(np.arange(dt,max_t,dt)):
        if 2 * particle_MA.r > lx:
            break
        print t
        index, = i # index starts from 0

        #tau=80*Nx*dt
        #I_SM=n_SM*np.exp(-(t-dt/2)/tau)
        #a=0.5
        #I_SM=n_SM*a*(t-dt/2)**(a-1)
        I_SM = n_SM
        dn = calc_num_nucleation(dt,I_SM,area_untransformed,
                                 particle_MA,particle_seed,
                                 particle_SM_active,particle_SM_inactive)
        N = len(particle_SM_active) + len(particle_SM_inactive)
        print "Nucleation event (total): ",dn," (",N,")"
        if dn > 0 and particle_MA.r - r_seed > r_test:
            particle_SM_nucleation(t,dn,r_test,
                                   r0_SM,k_SM,nu_SM,
                                   particle_MA,particle_seed,
                                   particle_SM_active,particle_SM_inactive)

        rr=0.0
        for p in particle_SM_active:
            rr += p.r
        rr *= k_SM
        #dr=(k_MA/2/np.pi-rr)*dt/particle_MA.r - dn*r0_SM*r0_SM/particle_MA.r # the supply of material is a constant (independent of the radius of MA)
        dr = (k_MA * dt - rr * dt / particle_MA.r -
              dn * r0_SM * r0_SM / (2 * particle_MA.r)) # the supply of material is proportial to the radius of MA
        #dr=k_MA*dt # the growth of MA is independent of the growth of SM.
        particle_MA.grow_by_dr(dr)

        particle_SM_growth(t,particle_MA,particle_seed,
                           particle_SM_active,particle_SM_inactive)

        t_list.append(t)
        area_M = 1e-6 * calc_area_M(particle_MA,particle_seed,
                                    particle_SM_active,particle_SM_inactive)
        area_MA = 1e-6 * np.pi * particle_MA.r**2
        area_seed=1e-6 * np.pi * particle_seed.r**2
        area_SM = area_MA-area_seed-area_M
        vol_MA.append(area_M * 1.0) #rho_MA=1.0
        vol_SM.append(area_SM * 2.0) #rho_SM=2.0
        vol_total.append(area_M * 1.0 + area_SM * 2.0)
        number_density_nuclei.append(N / (area_MA - area_seed)) #in um/s

        if args.figure and ((index + 1) % (3 * Nx)) == 0:
            draw_snap(aximage,lx,ly,dx,dy,
                      particle_MA,particle_seed,
                      particle_SM_active,particle_SM_inactive)
            draw_diameter_histogram(axhist,
                                    particle_SM_active,
                                    particle_SM_inactive)
            axN.clear()
            axN.plot(t_list,number_density_nuclei,'o')
            axVol.clear()
            axVol.plot(t_list,vol_MA,'b-')
            axVol.plot(t_list,vol_SM,'r-')
            axVol.plot(t_list,vol_total,'g-')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--param',default='./ngrc.ini',
                        help='the parameter file given by user')
    parser.add_argument('-s','--silent',action='store_true',
                        help='enable silent mode. Figures are saved to files instead of poping up windows')
    parser.add_argument('-f','--figure',action='store_true',
                        help='Figures are both showed in the popup window and saved to files instead of poping up windows')
    args = parser.parse_args()
    run(args)
    plt.show()


