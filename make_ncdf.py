#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 17:54:07 2017
Script for editing the effective radius input to the radiation model
@author: ee11mr
"""
import sys
sys.path.append('/nfs/annie/ee11mr/python_lib/')
from nctools import ncout3d
import numpy as np
from netCDF4 import Dataset
from glob import glob
import os

def tidy(regex):
    for fn in glob(regex):
        os.remove(fn)
    return

print 'Reading in dimensions from standard effective radius input file'
filepath = '/nfs/annie/ee11mr/Radiation_code/calc_inp_test/'
fh = Dataset(filepath+'Mar_day75.re','r')

lats=np.array([88.59375, 85.78125, 82.96875, 80.15625, 77.34375, 74.53125, 71.71875, 68.90625, 66.09375, 
    63.28125, 60.46875, 57.65625, 54.84375, 52.03125, 49.21875, 46.40625, 43.59375, 40.78125, 37.96875, 
    35.15625, 32.34375, 29.53125, 26.71875, 23.90625, 21.09375, 18.28125, 15.46875, 12.65625, 9.84375, 
    7.03125, 4.21875, 1.40625, -1.40625, -4.21875, -7.03125, -9.84375, -12.65625, -15.46875, -18.28125, 
    -21.09375, -23.90625, -26.71875, -29.53125, -32.34375, -35.15625, -37.96875, -40.78125, -43.59375,
    -46.40625, -49.21875, -52.03125, -54.84375, -57.65625, -60.46875, -63.28125, -66.09375, -68.90625, 
    -71.71875, -74.53125, -77.34375, -80.15625, -82.96875, -85.78125, -88.59375 ])
lons=   np.array([1.40625, 4.21875, 7.03125, 9.84375, 12.65625, 15.46875, 18.28125, 21.09375, 23.90625, 
    26.71875, 29.53125, 32.34375, 35.15625, 37.96875, 40.78125, 43.59375, 46.40625, 49.21875, 52.03125, 
    54.84375, 57.65625, 60.46875, 63.28125, 66.09375, 68.90625, 71.71875, 74.53125, 77.34375, 80.15625, 
    82.96875, 85.78125, 88.59375, 91.40625, 94.21875, 97.03125, 99.84375, 102.6562, 105.4688, 108.2812, 
    111.0938, 113.9062, 116.7188, 119.5312, 122.3438, 125.1562, 127.9688, 130.7812, 133.5938, 136.4062, 
    139.2188, 142.0312, 144.8438, 147.6562, 150.4688, 153.2812, 156.0938, 158.9062, 161.7188, 164.5312, 
    167.3438, 170.1562, 172.9688, 175.7812, 178.5938, 181.4062, 184.2188, 187.0312, 189.8438, 192.6562, 
    195.4688, 198.2812, 201.0938, 203.9062, 206.7188, 209.5312, 212.3438, 215.1562, 217.9688, 220.7812, 
    223.5938, 226.4062, 229.2188, 232.0312, 234.8438, 237.6562, 240.4688, 243.2812, 246.0938, 248.9062, 
    251.7188, 254.5312, 257.3438, 260.1562, 262.9688, 265.7812, 268.5938, 271.4062, 274.2188, 277.0312,
    279.8438, 282.6562, 285.4688, 288.2812, 291.0938, 293.9062, 296.7188, 299.5312, 302.3438, 305.1562, 
    307.9688, 310.7812, 313.5938, 316.4062, 319.2188, 322.0312, 324.8438, 327.6562, 330.4688, 333.2812, 
    336.0938, 338.9062, 341.7188, 344.5312, 347.3438, 350.1562, 352.9688, 355.7812, 358.5938 ])
plevs= np.array([1050, 3000, 5000, 7000, 9006.88, 11057.7, 13211.2, 15511.5, 17985.3, 
    20646.5, 23499.4, 26541.4, 29764.8, 33160.6, 36717, 40423.5, 44269.2, 48242.5, 
    52331.6, 56523.2, 60800.8, 65142, 69516.6, 73882.6, 78183.5, 82344.5, 86265.8, 
    89819.7, 92843.8, 95134.8, 96442.8])

print 'Reading control and perturbed CDN fields from TOMCAT runs'
filepath = '/nfs/annie/ee11mr/CDN_calculation/'
CDN_ctrl='CDNout_TOMCAT_gld305.nc'
CDN_ptb='CDNout_TOMCAT_so2_G50d.nc'
fh = Dataset(filepath+CDN_ctrl,'r')
CDN_ctrl=fh.variables['cdn4d'][:]
fh = Dataset(filepath+CDN_ptb,'r')
CDN_ptb=fh.variables['cdn4d'][:]

re_ctrl=np.zeros((31,64,128)) ; re_ctrl[:]=10.0e-6
re_ptb=np.zeros((12,31,64,128)) ; re_ptb[:]=10.0e-6

print 'Calculating perturbed effective radius from CDN fields'
for l in range(12):
    for i in range(128):
        print l,' ',i
        for j in range(64):
            for k in range(20,31):
                re_ptb[l,k,j,i]=10.0e-6*(CDN_ctrl[l,k,j,i]/CDN_ptb[l,k,j,i])**(1./3.)
print re_ptb.shape                       
print 'Deleting previous files and creating new netCDF input files for each month'             
filepath='/nfs/annie/ee11mr/Radiation_code/re_ptb/'
tidy('%s/*.*' % filepath)

init_months=['Jan_day15_init.re','Feb_day45_init.re','Mar_day75_init.re','Apr_day105_init.re',\
             'May_day136_init.re','Jun_day166_init.re','Jul_day196_init.re','Aug_day228_init.re',\
             'Sep_day258_init.re','Oct_day288_init.re','Nov_day319_init.re','Dec_day349_init.re',]

months=['Jan_day15.re','Feb_day45.re','Mar_day75.re','Apr_day105.re','May_day136.re','Jun_day166.re',\
        'Jul_day196.re','Aug_day228.re','Sep_day258.re','Oct_day288.re','Nov_day319.re','Dec_day349.re',]

re_ptb=np.swapaxes(re_ptb,1,3)
for i in range(12):
    print 'Creating '+months[i][:3]+' file'
    ncout3d(filepath+months[i],lons,lats,plevs,re_ptb[i],name='re',longname='Effective Radii',units='m')

for i in range(12):
    print 'Creating '+init_months[i][:3]+' init file'
    ncout3d(filepath+init_months[i],lons,lats,plevs,re_ptb[i],name='re',longname='Effective Radii',units='m')
print 'Done'