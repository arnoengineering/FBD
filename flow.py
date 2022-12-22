import numpy as np
import matplotlib.pyplot as plt
from numpy import pi, log, cos,sin, arctan, sqrt, array

xy = np.linspace(-4,4)
x,y = np.meshgrid(xy,xy)


# class Vect:
#     def __init__(self):
#         self.x = None
#         self.y = None


class Flow:
    def __init__(self,a=0,b=0):
        self.phi_feild = None
        self.psi_feild=None  #todo calc vs store?
        self.v_vect = None
        self.pos = [a,b]
        self.x = x
        self.y = y

    @property
    def vel(self,pos=-1):
        if self.v_vect is None:
            self.v_vect = self.vel_calc(self.x,self.y)
        if pos >=0:
            return self.v_vect[pos]
        return self.v_vect

    def __index__(self,i):
        return self.vel(i) # todo is correct? dict, whole vect

    def __add__(self, other):
        return self.phi_feild + other  # todo what defualt, return instance?

    @property  # todo set other also onther set total: return condition
    def u(self):

        return self.vel(0)

    @property
    def v(self):
        return self.vel(1)

    @property  # todo what if no feild?
    def w(self):
        return self.vel(2)

    @property
    def a(self):
        return self.pos[0]

    @property
    def b(self):
        return self.pos[1]

    @property
    def phi(self):   # todo index
        if self.phi_feild is None:
            self.phi_feild = self.phi_p(self.x,self.y)
        return self.phi_feild

    @property
    def psi(self):   # todo index
        if self.psi_feild is None:
            self.psi_feild = self.psi_p(self.x,self.y)
        return self.phi_feild

class Point(Flow):
    def __init__(self, vol, l, a=0,b=0):
        super(Point, self).__init__(a, b)
        self.vol = vol
        self.le = l
        self.scale = self.vol / (2 * pi * self.le)

    def phi_p(self, x1,y1):
        phi = self.scale * sqrt((x1 - self.a) ** 2 + (y1 - self.b) ** 2)
        return phi

    def field_calc(self):  # todo wrap?
       pass

    def psi_p(self, x1,y1):
        dif = (y1-self.b)/(x1-self.a)
        return self.scale*arctan(dif)

    def vel_calc(self,x1,y1):
        dif = (y1 - self.b) / (x1 - self.a)
        v = self.scale*(y1-self.b)/(1+dif**2)/(x1-self.a)**2
        u = self.scale/(1+dif**2)/(x1-self.a)
        return array((u,v))


class Uniform(Flow):
    def __init__(self, vel, a=0, b=0,alpha=0):
        super().__init__(a, b)
        self.vol = vel
        self.alpha = alpha

    def phi_p(self, x1, y1=0):
        phi = self.vol*x1  # todo fix if Alpha !=0
        return phi

    def field_calc(self):  # todo wrap?   # todo vx/vy
        pass

    def psi_p(self, x1, y1):
        return self.vol*cos(self.alpha)*y1

    def vel_calc(self,x1,y1):
        au = np.ones(x1.shape)
        u = self.vol*cos(self.alpha)*au
        v = self.vol*sin(self.alpha)*au
        return array((u,v))


class Doublet(Flow):
    def __init__(self, vol, l, a=0, b=0,alpha=0,sep=2):  # todo both points, cos/l, one or cent, left r sorce
        super().__init__(a, b)
        p = [a,b]+[cos(alpha),sin(alpha)]*sep*[-1,1]  # todo by 2
        self.p1 = Point(vol, l, p[0])
        self.p2 = Point(vol, l, p[1])

    def phi_p(self, x1, y1):
        return self.p1.phi_p(x1,y1)+ self.p2.phi_p(x1,y1)

    def field_calc(self):  # todo wrap?
        pass

    def psi_p(self, x1, y1):
        return self.p1.psi_p(x1,y1)+ self.p2.psi_p(x1,y1)

    def vel_calc(self, x1, y1):
        return self.p1.vel_calc(x1,y1)+ self.p2.vel_calc(x1,y1)


class Vortex(Flow):
    def __init__(self, gamma, a=0, b=0):
        super().__init__(a, b)
        self.gamma = gamma
        self.scale = gamma/(2*pi)

    def psi_p(self, x1, y1):
        phi = self.scale * log(sqrt((x1 - self.a) ** 2 + (y1 - self.b) ** 2))
        return phi

    def field_calc(self):  # todo wrap?
        pass

    def phi_p(self, x1, y1):
        dif = (y1 - self.b) / (x1 - self.a)
        return self.scale * np.atan(dif)

    def vel_calc(self, x1, y1):
        dif = (y1 - self.b) / (x1 - self.a)
        u = (y1-self.b) / (1 + dif ** 2) / (x1 - self.a) ** 2
        v = 1 / (1 + dif ** 2) / (x1 - self.a)
        return array((u,v))


if __name__ == '__main__':
    p1 = Point(5,1)
    p2 = Uniform(2)
    v1 = p1.vel
    v2 = p2.vel
    v3 = v1+v2
    print(len(v3))
    plt.quiver(x,y,*v3)
    # plt.contour
    plt.streamplot(x,y,*v3)
    plt.show()
