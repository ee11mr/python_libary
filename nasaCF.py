
import xarray as xr
import numpy as np


file='https://opendap.nccs.nasa.gov/dods/gmao/geos-cf/assim/chm_tavg_1hr_g1440x721_v1'
ds = xr.open_dataset(file)

field=ds.sel(time=slice("2018-08-01", "2018-08-03"),lat=slice(-30,30),lon=slice(-180,180))

ch4=field['co'].data
print(ch4.shape)
ch4=np.squeeze(ch4.mean(axis=0))
print(ch4.shape)


from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import RowPy as rp

cf_lat=field['lat'].data
cf_lon=field['lon'].data

X,Y = np.meshgrid(cf_lon, cf_lat)
m=rp.get_basemap(lllat=-30, urlat=30)
m.contourf(X,Y,ch4)
plt.savefig('./Test.png')


stop

cf_su=field['pm25su_rh35_gcc'].data
cf_soa=field['pm25soa_rh35_gc'].data
cf_ss=field['pm25ss_rh35_gcc'].data
cf_oc=field['pm25oc_rh35_gcc'].data
cf_bc=field['pm25bc_rh35_gcc'].data
cf_du=field['pm25du_rh35_gcc'].data

cf_lat=field['lat'].data
cf_lon=field['lon'].data

print(cf_su.shape)

cf_su=np.squeeze(cf_su.mean(axis=0))
cf_soa=np.squeeze(cf_soa.mean(axis=0))
cf_ss=np.squeeze(cf_ss.mean(axis=0))
cf_oc=np.squeeze(cf_oc.mean(axis=0))
cf_bc=np.squeeze(cf_bc.mean(axis=0))
cf_du=np.squeeze(cf_du.mean(axis=0))

total=cf_su+cf_soa+cf_ss+cf_oc+cf_bc+cf_du

ratio_su=cf_su/total
ratio_soa=cf_soa/total
ratio_ss=cf_ss/total
ratio_oc=cf_oc/total
ratio_bc=cf_bc/total
ratio_du=cf_du/total

print(cf_su.shape)
print(cf_su)
