import datetime
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import RowPy as rp

var='U'
res='0.25x0.3125'
no_fs=res.replace('.', '')
time=datetime.datetime(2017,8,30,0,0)

metpath='/mnt/lustre/groups/chem-acm-2018/earth0_data/GEOS/ExtData/GEOS_%s/GEOS_FP/%s/%02d/GEOSFP.%s%02d%02d.A3dyn.%s.nc' % (res, time.year, time.month, time.year, time.month,time.day, no_fs)

import matplotlib.pyplot as plt

fh=Dataset(metpath)

lat=fh.variables['lat'][:]
lon=fh.variables['lon'][:]
lat[0]=-90.
lat[-1]=90.

u=fh.variables['U'][:,0]
v=fh.variables['V'][:,0]
u=np.mean(u,0)
v=np.mean(v,0)

m=rp.get_basemap(lllat=-30., urlat=30., lllon=-100, urlon=10.)
m.streamplot(lon, lat, u, v)
plt.savefig('./test.png')
