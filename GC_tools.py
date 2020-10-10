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
import argparse
import sys
sys.path.append('/users/mjr583/scratch/python_lib')
from CVAO_dict import CVAO_dict as d


def get_arguments():
    """
    Get the arguments supplied from command line

    Returns
    -------
    inputs
    """
    parser = argparse.ArgumentParser(description="Parse arguments to pass to GC processing scripts")
    parser.add_argument("-r", "--rundir", type=str, 
                        help='Name of desired GC rundir')
    parser.add_argument("-s", "--var", type=str,
                        help="Name of GC variable")
    parser.add_argument("-v", "--version", type=str,
                        default='12.9.3',
                        help="Version of GEOS-Chem")
    parser.add_argument("-p", "--pres", type=bool,
                        default=False,
                        help="Include pressure isobars in contour plots")
    args=parser.parse_args()
    return args


def get_n_timesteps(rundir, version='12.9.3'):
    """
    Get the number of timesteps in a directory of GC output

    Parameters
    -------
    Rundir (str): Name of GC rundir to look for output in
    Version (str): Version of GC used
    
    Returns
    -------
    nt (int): Number of timesteps in output directory
    """
    nt=0
    for infile in sorted(glob.glob('/users/mjr583/scratch/GC/%s/%s/output/GEOSChem.SpeciesConc.*.nc4' % (version, rundir))):
        fh=Dataset(infile)
        t=len(fh.variables['time'][:])
        nt+=t

    return nt


def get_gc_var(rundir, variable, version='12.9.3'):
    """
    Get the number of timesteps in a directory of GC output

    Parameters
    -------
    Rundir (str): Name of GC rundir to look for output in
    Variable (str): Name of GC variable to process
    Version (str): Version of GC used
    
    Returns
    -------
    var (array): Array of specified variable
    lat (array): Latitudes of GC run
    lon (array): Longitudes of GC run
    lev (array): Levles of GC run
    times (datetime): Timesteps as datetime objects
    """

    gc_var=[] ; times=[]
    for i,infile in enumerate(sorted(glob.glob('/users/mjr583/scratch/GC/%s/%s/output/GEOSChem.SpeciesConc.*.nc4' % (version, rundir)))):
        if variable in d:
            gc_name=d[variable]['GC_name']
        else:
            gc_name=variable

        fh=Dataset(infile)
        var=fh.variables['SpeciesConc_%s' %gc_name][:]
        gc_var.append(var)
        
        time=fh.variables['time'][:]
        t0=fh.variables['time'].units
        t0=(int, re.findall(r'\d+', t0))[1]
        t0=datetime.datetime(int(t0[0]), int(t0[1]), int(t0[2]), int(t0[3]), int(t0[4]), int(t0[5]) )
        for dt in time:
            rounded_dt = hour_rounder(t0 + datetime.timedelta(minutes=dt))
            times.append(rounded_dt)
            #times.append( t0 + datetime.timedelta(minutes=dt) )
        
        if i==0:
            lat=fh.variables['lat'][:]
            lon=fh.variables['lon'][:]
            lev=fh.variables['lev'][:]

    times=np.array(times)
    var=np.array(gc_var)
    
    SHAPE=var.shape
    var=np.reshape(var, (SHAPE[0]*SHAPE[1], SHAPE[2], SHAPE[3], SHAPE[4]))
    
    if variable in d:
        if d[variable]['unit'] == 'ppmv':
            var=var*1e6
        elif d[variable]['unit'] == 'ppbv':
            var=var*1e9
        elif d[variable]['unit'] == 'pptv':
            var=var*1e12

    return var, lat, lon, lev, times


def hour_rounder(t):
    """
    Round datetime objects to the nearest hour by adding a timedelta hour if minute >= 30

    Parameters
    -------
    t (datetime): Datetime object
    
    Returns
    -------
    t (datetime): Rounded datetime object
    """
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
                               +datetime.timedelta(hours=t.minute//30))
