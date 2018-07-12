#!/usr/local/bin/python
"""graph_potential_path.py
Graphical tester for potential_path.py
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import potential_path as pp


def plot_grid_potential(map_test):
    fig = plt.figure()
    ax = fig.add_subplot(2,2,1,projection='3d')

    X = np.arange(-15,15,0.25)
    Y = np.arange(-15,15,0.25)
    X, Y = np.meshgrid(X, Y)

    #Heatmap
    Z=()
    for xlist, ylist in zip(X,Y):
        zlist=()
        for x,y in zip(xlist,ylist):
            zlist=zlist+(map_test.potential((x,y)),)
        Z = Z + (zlist,)
    surf = ax.plot_surface(X,Y,np.asarray(Z), cmap=cm.coolwarm, linewidth = 0, antialiased=False)

    ax.set_zlim(0,100)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    fig.colorbar(surf, shrink=0.5, aspect=5)

    #Path
    step_size=0.01
    ax2 = fig.add_subplot(2,2,4, projection='3d')
    
    x_path=(-10,)
    y_path=(-10,)
    potential=(0,)
    time = (0,)

    for x in range(1,1000):
        time = time+(x,)
        step = map_test.gradient((x_path[-1],y_path[-1]))
        potential = potential + (map_test.potential((x_path[-1], y_path[-1])),)
        x_path = x_path + (x_path[-1]+step[0]*step_size,)
        y_path = y_path + (y_path[-1]+step[1]*step_size,)

    ax2.plot(x_path ,y_path, time, label="path") 
    ax2.set_xlabel("x axis")
    ax2.set_ylabel("y axis")
    ax2.set_zlabel("time")

    #Potential on Path
    ax3 = fig.add_subplot(2,2,2)
    ax3.plot(time, potential, label="Potential v. Time")
    ax3.set_xlabel("time")
    ax3.set_ylabel("potential")

    ax4 = fig.add_subplot(2,2,3)
    ax4.plot(x_path,y_path)
    
    print("{0},{1}".format(x_path[-1],y_path[-1]))
    plt.show()

plot_grid_potential(pp.MapPotential(goal=pp.GoalPotential(location=(3,1),z=0.5,kind=2, d_threshold=5),obstacles=(pp.ObstaclePotential(location=(-3,-3), d_safe=15, r=2,n=10),pp.ObstaclePotential(location=(1,7), d_safe=10, r=3, n = 10))))
