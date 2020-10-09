# *****************************COPYRIGHT*******************************
# (C) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT.txt
# which you should have received as part of this distribution.
# *****************************COPYRIGHT*******************************
'''
Plots a mean profile of the variable in the supplied file
against height (calculated from pressure assuming isothermal atmos.)
'''

CONST = 287. * 250. / (9.80665 * 1000.0) #

from netCDF4 import Dataset
import sys
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    if (len(sys.argv) > 1):
        filename = sys.argv[1]
    else:
        raise RuntimeError('please enter a file name')

dgs = Dataset(filename)
name = filename[filename.find('.') + 1:]

lon = dgs.variables['lon'][:]
lat = dgs.variables['lat'][:]
p = dgs.variables['plev'][:]

n_lon = len(lon)
n_lat = len(lat)
layers= len(p)

var = dgs.variables[name][:]

vmean = np.zeros(layers)
for i in np.arange(layers):
    vmean[i] = np.sum(var[i, :, :]) / (n_lon * n_lat)

ax1 = plt.figure().add_subplot(111)
ax1.plot(vmean, -np.log(p/max(p))*CONST)
ax1.set_xlabel(name)
ax1.set_ylabel('Approx height (km)')
plt.show()

# plot,vmean,-alog(p/max(p))*const,xtitle=name,ytitle='Approx height (km)'

# print 'Pressure, ', name  
# for i in range(len(p)):
#     print "%*.3f  %*.3f" %(9, p[i], 6, vmean[i])
