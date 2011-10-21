#!/usr/bin/env python

"""
A class for cicular particle
Since 2011.8.19

AUTHOUR:
    Yi-Xin Liu <liuyxpp@gmail.com>
    Fudan University
REVISION:
    2011.8.22
"""
import numpy as np
from persistent import Persistent
from .vector2d import Vector2D

class Particle(Persistent):
    def __init__(self,o=Vector2D(),r0=0.0,r=0.0,t0=0.0,k=1.0,nu=1.0):
        self.o=o        # center of the circular particle
        self.r0=float(r0)
        self.r=float(r)
        self.t0=float(t0)  # particle born time
        self.k=float(k)
        self.nu=float(nu)      # growth kinetics: r=k*(t-t0)^nu
    def __str__(self):
        return 'Particle of radius '+str(self.r)+' locates at '+str(self.o)+' with growth kinetics r= '+str(self.k)+' * t^'+str(self.nu)
    def __eq__(self,other):
        return ((self.o==other.o) and (self.r==other.r))
    def r2(self):
        return self.r*self.r
    def area(self):
        return np.pi*self.r*self.r
    def perimeter(self):
        return 2*np.pi*self.r
    def grow_by_function(self,t):
        if self.nu==0.0:
            pass
        elif self.nu==1.0:
            self.r=self.r0+self.k*(t-self.t0)
        else:
            self.r=self.r0+self.k*(t-self.t0)**self.nu
    def grow_by_dr(self,dr):
        self.r += dr
    def is_inner_point(self,pt):
        '''Boundary points are also inner points'''
        return (self.o.distance2(pt) <= self.r2())
    def is_boundary_point(self,pt):
        return (abs(self.o.distance2(pt)-self.r2())<1e-12)
    def is_touch(self,other):
        '''is self touches other'''
        d2=self.o.distance2(other.o)
        rr=self.r+other.r
        rr *= rr
        return (d2 <= rr)
    def draw_on_lattice(self,color,lx,ly,lattice):
        Lx,Ly=np.shape(lattice)
        dx=lx/Lx
        dy=ly/Ly
        Ox=int(self.o.x/dx)
        Oy=int(self.o.y/dy)
        R=int(self.r/dx) # dx=dy is assumed. isotropic square cell
        grids=np.indices((2*R+1,2*R+1)).reshape(2,-1).T - R
        for i in grids:
            ix,iy=i
            if (ix*ix+iy*iy<=R*R) and (0<=ix+Ox<Lx) and (0<=iy+Oy<Ly):
                lattice[ix+Ox,iy+Oy]=color

def test():
    p0=Particle() # particle at (0,0) with zero radius
    print p0
    dt=0.1
    max_t=10
    o1=Vector2D(0.2,0.3)
    p1=Particle(o1)
    o2=Vector2D(0.2,0.7)
    p2=Particle(o2,r=0.1)
    test_pt1=Vector2D()
    test_pt2=Vector2D(-0.1,0.1)
    test_pt3=Vector2D(0.3,0.2)
    test_pt4=Vector2D(0.5,-0.1)
    print p1
    print p1.r2()
    print p1.area()
    print p1.perimeter()
    print p1.is_inner_point(test_pt1)
    print p1.is_inner_point(test_pt2)
    print p1.is_inner_point(test_pt3)
    print p1.is_boundary_point(test_pt4)
    for t1 in np.arange(dt,max_t,dt):
        p1.grow(t1)
        print p1
        print p1.r2()
        print p1.area()
        print p1.perimeter()
        print p1.is_inner_point(test_pt1)
        print p1.is_inner_point(test_pt2)
        print p1.is_inner_point(test_pt3)
        print p1.is_boundary_point(test_pt4)
        print 'touched?',p1.is_touch(p2)
        raw_input()

if __name__=='__main__':
    test()
