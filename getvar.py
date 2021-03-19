#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
import netCDF4
from netCDF4 import Dataset
import datetime     
import os
import glob
import re
import argparse
import sys
sys.path.append('/users/mjr583/python_lib')
from CVAO_dict import CVAO_dict as d
import RowPy as rp


def get_gc_var(rundir, variable, version='12.9.3', year=None):
    """
    Get the number of timesteps in a directory of GC output

    Parameters
    -------
    Rundir (str): Name of GC rundir to look for output in
    Variable (str): Name of GC variable to process
    Version (str): Version of GC used
    year (str): Option to read output only for particular year
    
    Returns
    -------
    var (array): Array of specified variable
    lat (array): Latitudes of GC run
    lon (array): Longitudes of GC run
    lev (array): Levles of GC run
    times (datetime): Timesteps as datetime objects
    """
    global d

    gc_var=[] ; times=[]
    if year==None:
        year=''
    for i,infile in enumerate(sorted(glob.glob('/users/mjr583/scratch/GC/%s/rundirs/%s/OutputDir/GEOSChem.SpeciesConc.*%s*.nc4' % (version, rundir, year)))):
        print(infile)
        if variable in d:
            gc_name=d[variable]['GC_name']
        elif variable in g:
            d=g
            gc_name=d[variable]['GC_name']
        else:
            gc_name=variable
        
        fh=Dataset(infile)        
        var=fh.variables['SpeciesConc_%s' %gc_name][:]
        #except:
        #    continue

        gc_var.append(var)
        
        time=fh.variables['time'][:]
        t0=fh.variables['time'].units
        t0=(int, re.findall(r'\d+', t0))[1]
        t0=datetime.datetime(int(t0[0]), int(t0[1]), int(t0[2]), int(t0[3]), int(t0[4]), int(t0[5]) )
        for dt in time:
            #rounded_dt = hour_rounder(t0 + datetime.timedelta(minutes=dt))
            #times.append(rounded_dt)
            times.append( t0 + datetime.timedelta(minutes=dt) )
        
        if i==0:
            lat=fh.variables['lat'][:]
            lon=fh.variables['lon'][:]
            lev=fh.variables['hyam'][:]

    times=np.array(times)

    try:
        var=np.array(gc_var)
        SHAPE=var.shape
        var=np.reshape(var, (SHAPE[0]*SHAPE[1], SHAPE[2], SHAPE[3], SHAPE[4]))
    except:
        var=np.concatenate(gc_var)
    
    if variable in d:
        if d[variable]['unit'] == 'ppmv':
            var=var*1e6
        elif d[variable]['unit'] == 'ppbv':
            var=var*1e9
        elif d[variable]['unit'] == 'pptv':
            var=var*1e12
    
    var = var / d[variable]['GC_molratio']
    #if variable=='ethane':
    #    var = var / 2

    return var, lat, lon, lev, times

