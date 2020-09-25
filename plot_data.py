import sys
import numpy as np
import matplotlib.pyplot as plt

datafile = sys.argv[1]
data = np.loadtxt(datafile)
sample_rate = 20000.0
dt = 1/sample_rate

numpts = data.shape[0]
numchan = data.shape[1]-1

ind = data[:,0]
t = dt*ind


for i in range(numchan):
    if i == 0:
        ax = plt.subplot(numchan,1,i+1)
    else:
        plt.subplot(numchan,1,i+1, sharex=ax)

    plt.plot(t,data[:,i+1])
    plt.ylabel('chan{} (V)'.format(i))
    plt.grid(True)
    plt.ylim(-10,10)

    if i==(numchan-1):
        plt.xlabel('time (sec)')

plt.show()



