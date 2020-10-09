#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error, r2_score
from matplotlib.offsetbox import AnchoredText
import netCDF4
from netCDF4 import Dataset
import datetime     
import os
import glob
import re
import sys
sys.path.append('/users/mjr583/scratch/python_lib')
from CVAO_dict import CVAO_dict as d

def get_n_timesteps(rundir, version='12.9.3'):
    nt=0
    for infile in sorted(glob.glob('/users/mjr583/scratch/GC/%s/%s/output/GEOSChem.SpeciesConc.*.nc4' % (version, rundir))):
        fh=Dataset(infile)
        t=len(fh.variables['time'][:])
        nt+=t

    return nt


def get_gc_var(rundir, species, version='12.9.3'):
    gc_var=[] ; times=[]
    for i,infile in enumerate(sorted(glob.glob('/users/mjr583/scratch/GC/%s/%s/output/GEOSChem.SpeciesConc.*.nc4' % (version, rundir)))):
        fh=Dataset(infile)
        var=fh.variables['SpeciesConc_%s' %species][:]
        gc_var.append(var)
        
        time=fh.variables['time'][:]
        t0=fh.variables['time'].units
        t0=(int, re.findall(r'\d+', t0))[1]
        t0=datetime.datetime(int(t0[0]), int(t0[1]), int(t0[2]), int(t0[3]), int(t0[4]), int(t0[5]) )
        for dt in time:
            times.append( t0 + datetime.timedelta(minutes=dt) )
        
        if i==0:
            lat=fh.variables['lat'][:]
            lon=fh.variables['lon'][:]
            lev=fh.variables['lev'][:]

    times=np.array(times)
    var=np.array(gc_var)
    
    SHAPE=var.shape
    var=np.reshape(var, (SHAPE[0]*SHAPE[1], SHAPE[2], SHAPE[3], SHAPE[4]))
    
    if d[species]['unit'] == 'ppmv':
        var=var*1e6
    elif d[species]['unit'] == 'ppbv':
        var=var*1e9
    elif d[species]['unit'] == 'pp7v':
        var=var*1e12

    return var, lat, lon, lev, times

