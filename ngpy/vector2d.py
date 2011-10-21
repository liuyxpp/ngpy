#!/usr/bin/env python

import math

"""
2D math vector
Since 2011.8.19

AUTHOUR:
    Yi-Xin Liu <liuyxpp@gmail.com>
    Fudan University
REVISION:
    2011.8.22

"""
from persistent import Persistent

class Vector2D(Persistent):
    def __init__(self,x=0.0,y=0.0):
        self.x=float(x)
        self.y=float(y)
    def __sub__(self,other):
        return Vector2D(self.x-other.x,self.y-other.y)
    def __isub__(self,other):
        self.x -= other.x
        self.y -= other.y
    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+")"
    def __eq__(self,other):
        return ((self.x==other.x) and (self.y==other.y))
    def length2(self):
        dx=self.x
        dy=self.y
        return dx*dx + dy*dy
    def length(self):
        return math.sqrt(self.length2())
    def distance2(self,other):
        return (self-other).length2()
    def distance(self,other):
        return (self-other).length()

def test():
    x1=1.1
    y1=-3
    x2=-2.3
    y2=0
    point0=Vector2D()
    point1=Vector2D(x1,y1)
    point2=Vector2D(x2,y2)
    print point0,'= (0,0)?'
    print point1,'= (',x1,',',y1,')?'
    print point2,'= (',x2,',',y2,')?'
    print point1.length(),'= ',math.sqrt(x1*x1+y1*y1),'?'
    print point2.length2(),'= ',x2*x2+y2*y2,'?'
    print point0.distance2(point2),'= ',(0-x2)**2+(0-y2)**2,'?'
    print point1.distance(point2),'= ',math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)),'?'

if __name__=='__main__':
    test()

