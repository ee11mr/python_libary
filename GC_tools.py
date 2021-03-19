#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error, r2_score
from matplotlib.offsetbox import AnchoredText
import netCDF4
from netCDF4 import Dataset
import datetime     
import os
import glob
import re
import calendar
import argparse
import xarray as xr
import sys
sys.path.append('/users/mjr583/python_lib')
from CVAO_dict import CVAO_dict as d
from CVAO_dict import GC_dict as g
import RowPy as rp


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
    parser.add_argument("-v", "--var", type=str,
                        help="Name of GC variable")
    parser.add_argument("-V", "--version", type=str,
                        default='12.9.3',
                        help="Version of GEOS-Chem")
    parser.add_argument("-p", "--plot_ps", type=bool,
                        default=False,
                        help="Include pressure isobars in contour plots")
    parser.add_argument("-s", "--strmfunc", type=bool,
                        default=False,
                        help="Include stream function plot")
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
    for infile in sorted(glob.glob('/users/mjr583/scratch/GC/%s/rundirs/%s/OutputDir/GEOSChem.SpeciesConc.*.nc4' % (version, rundir))):
        fh=Dataset(infile)
        t=len(fh.variables['time'][:])
        nt+=t

    return nt


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
        
        try:
            fh=Dataset(infile)        
            var=fh.variables['SpeciesConc_%s' %gc_name][:]
        except:
            continue

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
    
    if '12' in version:
        var = var / d[variable]['GC_molratio']
    #if variable=='ethane':
    #    var = var / 2

    return var, lat, lon, lev, times


def HEMCO_Diag_read(rundir, version='12.9.3', variable='', year=False):
    times=[] ; ems=[]
    if year:
        filein = '/users/mjr583/scratch/GC/%s/rundirs/%s/OutputDir/HEMCO_diag*%s*.nc' % (version, rundir, year) 
    else:
        filein = '/users/mjr583/scratch/GC/%s/rundirs/%s/OutputDir/HEMCO_diag*.nc' % (version, rundir)
    for infile in sorted(glob.glob(filein)):
        #print(infile)
        try:
            fh=Dataset(infile)
        except:
            continue
        time=fh.variables['time'][:]
        t0=fh.variables['time'].units
        t0=(int, re.findall(r'\d+', t0))[1]
        t0=datetime.datetime(int(t0[0]), int(t0[1]), int(t0[2]), int(t0[3]), int(t0[4]), int(t0[5]) )
        for dt in time:
            times.append( t0 + datetime.timedelta(minutes=dt) )

        emission=fh.variables[variable][:]
        #print(emission.shape)
        ems.append(emission)

    lat=fh.variables['lat'][:]
    lon=fh.variables['lon'][:]
    lev=fh.variables['lev'][:]
    area=fh.variables['AREA'][:]
    ems=np.concatenate(ems)
    unit=fh.variables[variable].units
    #print(ems.shape)
    var_list=list(fh.variables.keys())[8:]
    
    return ems, times, lat, lon, lev, area, var_list, unit

def plot_all_gc_ems(rundir, variable=None,version='12.9.3',plot=False, year=''):
    """
    Creates timeseries plot of every variable in the HEMCO_Diagnostic file for a particular run directory 

    Parameters
    -------
    Rundir (str): Name of GC rundir to look for output in
    Version (str): Version of GC used
    
    Returns
    -------
    """
    if rundir == None:
        sys.exit('Please give the run directory')
    times=[]
    for infile in sorted(glob.glob('/users/mjr583/scratch/GC/%s/rundirs/%s/OutputDir/HEMCO_diag*.nc' % (version, rundir))):
        try:
            fh=Dataset(infile)
        except:
            continue
        time=fh.variables['time'][:]
        lat=fh.variables['lat'][:]

        lon=fh.variables['lon'][:]
        lev=fh.variables['lev'][:]
        AREA=fh.variables['AREA'][:]

        t0=fh.variables['time'].units
        t0=(int, re.findall(r'\d+', t0))[1]
        t0=datetime.datetime(int(t0[0]), int(t0[1]), int(t0[2]), int(t0[3]), int(t0[4]), int(t0[5]) )
        for dt in time:
            times.append( t0 + datetime.timedelta(minutes=dt) )
    
    times=np.array(times)
    lat=fh.variables['lat'][:]
    lon=fh.variables['lon'][:]
    lev=fh.variables['lev'][:]
    
    names=list(fh.variables.keys())[8:]
    names = [s for s in names if "BioBurn" in s]
    print(names)
    if variable != None:
        names= [s for s in names if variable+'_' in s]
    for var in names:  
        print(var)
        mw=False
        gc_em=[]
        for i,infile in enumerate(sorted(glob.glob('/users/mjr583/scratch/GC/%s/rundirs/%s/OutputDir/HEMCO_diag*%s*.nc' % (version, rundir, year)))):
            fh=Dataset(infile)
            em=fh.variables[var]
            unit=em.units
            long_name=em.long_name

            em=np.array(np.squeeze(em[:]))
            days_in_month=calendar.monthrange(times[i].year, times[i].month)[1]
            if mw:
                unit='Tg'
                if len(em.shape) == 3:  ## Convert from kg/m2/s to Tg month-1
                    hold_em=[]
                    for i in range(47):
                        x = em[i] * AREA             ## kg/m2/s to kg/s per gridbox
                        x = x * 86400 * days_in_month           ## kg/s/gridbox to kg/gridbox/month
                        hold_em.append( x * 1e-9)    ## kg to Tg
                    em=np.array(hold_em)
                else:
                    x = em * AREA           ## kg/m2/s to kg/s per gridbox
                    x = x * 86400 * 30      ## kg/s/gridbox to kg/gridbox/month
                    em =  x * 1e-9          ## kg to Tg
            gc_em.append(em)
         
        ems=np.array(gc_em)
        if ems.ndim == 4:
            ems=np.sum(np.sum(np.sum(ems[:,:,:,:],1),1),1)
        elif ems.ndim == 3:
            ems=np.sum(np.sum(ems,1),1)
        else: # This shouldn't happen
            print(ems)
            print('What now?')
            sys.exit()
        df=pd.DataFrame({'Value':ems}, index=times)
        print('Annual total =', df.groupby(df.index.year).sum())
        
        if plot:
            f,ax= plt.subplots(figsize=(12,4))
            ax.plot(times, ems, 'orchid', label=long_name)
            plt.ylabel(unit)
            plt.legend()
            plt.savefig('/users/mjr583/scratch/GC/%s/%s/emissions/%s.png' % (version, rundir, long_name) )
            plt.close()

            f,ax= plt.subplots(figsize=(12,4))
            ax.plot(ems[2:14], 'orchid', label='2008')
            ax.plot(ems[-12:], 'aqua', label='2019')
            plt.title(long_name)
            plt.ylabel(unit)
            plt.legend()
            plt.savefig('/users/mjr583/scratch/GC/%s/%s/emissions/%s_2008-2019.png' % (version, rundir, long_name) )
            plt.close()
            return
        else:
            return df,ems


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


def find_timestep(times):
    """
    Find the timestep of a GC run

    Parameters
    -------
    times (array): Array of datetime objects
    
    Returns
    -------
    step (str): String indicating timestep, applicable to pandas DataFrame resample function
    interval (int): X-tick interval in number of days or months
    """
    delta = times[1] - times[0]
    if delta >= datetime.timedelta(days=365):
        step='Y'
        interval=12
    elif datetime.timedelta(days=28) <= delta <= datetime.timedelta(days=31):
        step='M'
        interval=12
    elif delta == datetime.timedelta(days=1):
        step='D'
        interval=4
    elif delta == datetime.timedelta(minutes=60):
        step='H'
        interval=2
    else:
        step='M'
        interval=12
    return step, interval


def get_gc_input(time, filetype='I3',var='PS', res='0.25x0.3125'):
    """
    Get the number of timesteps in a directory of GC output

    Parameters
    -------
    time (datetime): time to get the met input
    filetype (str): Determines which file to access for desired variable
    var (str): The netcdf variable name to read
    res (str): Resolution to read

    Returns
    -------
    var (array): 4d array of variable
    lat (array): 1d array of latitudes
    lon (array): 1d array of longitudes
    """
    no_fs= res.replace('.', '')
    metpath='/mnt/lustre/groups/chem-acm-2018/earth0_data/GEOS/ExtData/GEOS_%s/GEOS_FP/%s/%02d/GEOSFP.%s%02d%02d.%s.%s.nc' % (res,time.year,time.month,time.year, time.month,time.day, filetype, no_fs)
    
    fh=Dataset(metpath)
    var=fh.variables[var][int(time.hour / 3)]
    lat=fh.variables['lat'][:]
    lon=fh.variables['lon'][:]

    return var, lat,lon


def get_interp_gc_input(ms, time, filetype='I3',var='PS', res='0.25x0.3125'):
    """
    Get the number of timesteps in a directory of GC output

    Parameters
    -------
    ms (datetime): Time of closest input data
    time (datetime): Time of model run for which to get the met input
    filetype (str): Determines which file to access for desired variable
    var (str): The netcdf variable name to read
    res (str): Resolution to read

    Returns
    -------
    var (array): 4d array of variable
    lat (array): 1d array of latitudes
    lon (array): 1d array of longitudes
    """
    if ms < time:
        ms1=ms
        ms2=ms + datetime.timedelta(hours=3)
    else:
        ms2=ms
        ms1=ms - datetime.timedelta(hours=3)

    no_fs= res.replace('.', '')
    metpath_1='/mnt/lustre/groups/chem-acm-2018/earth0_data/GEOS/ExtData/GEOS_%s/GEOS_FP/%s/%02d/GEOSFP.%s%02d%02d.%s.%s.nc' % (res,ms1.year,ms1.month,ms.year, ms1.month,ms1.day, filetype, no_fs)

    metpath_2='/mnt/lustre/groups/chem-acm-2018/earth0_data/GEOS/ExtData/GEOS_%s/GEOS_FP/%s/%02d/GEOSFP.%s%02d%02d.%s.%s.nc' % (res,ms2.year,ms2.month,ms2.year, ms2.month,ms2.day, filetype, no_fs)

    fh=Dataset(metpath_1)
    var1=fh.variables[var][int(ms.hour / 3)]

    fh2=Dataset(metpath_2)
    var2=fh2.variables[var][int(ms2.hour / 3)]
    
    n = (var2 - var1) / 3
     
    print(time, ms, ms2)
    print(var1[0,0,0])
    print(var2[0,0,0])
    if  time - ms < ms2 - time:
        print('Closer to earlier hour')
        var = var1 + n
    else:
        var = var1 +n*2
    
    print(var[0,0,0])

    lat=fh.variables['lat'][:]
    lon=fh.variables['lon'][:]

    return var, lat,lon


def closest_met(time):
    """
    Get the closest time available for met date for GC output

    Parameters
    -------
    time (array): array of datetime objects from GC

    Returns
    -------
    metsteps (array): array of datetime objects adjusted to closest available met field
    
    """
    ms=[]
    t=time
    #for t in time:
    metsteps=[]
    for n in range(0,24,3):
        metsteps.append(datetime.datetime(t.year, t.month, t.day, n, 0))
    a=min(metsteps, key=lambda d: abs(d - t))
    ms.append(a)

    metsteps=np.array(ms)
    return a


def dt_difference(a, b):
    """
    Gives the time difference between 2 datetime objects in hours

    Parameters
    -------
    a (datetime object)
    b (datetime object)

    Returns
    -------
    d (int): difference between a and b in hours
    
    """
    if a > b:
        d = (a - b).seconds / 3600
    else:
        d = (b - a).seconds / 3600

    return d


def makeStreamLegend(strm, lx, convertFunc, nlines=5, color='k', fmt='{:g}'):
    ''' Make a legend for a streamplot on a separate axes instance '''
    # Get the linewidths from the streamplot LineCollection
    lws = np.array(strm.lines.get_linewidths())
    
    # Turn off axes lines and ticks, and set axis limits
    lx.axis('off')
    lx.set_xlim(0, 1)
    lx.set_ylim(0, 1)
    
    # Loop over the desired number of lines in the legend
    for i, y in enumerate(np.linspace(0.1, 0.9, nlines)):
        # This linewidth
        lw = lws.min()+float(i) * lws.ptp()/float(nlines-1)
        
        # Plot a line in the legend, of the correct length
        lx.axhline(y, 0.1, 0.4, c=color, lw=lw)
        
        # Add a text label, after converting the lw back to a speed
        lx.text(0.5, y, fmt.format(convertFunc(lw)), va='center')


def LWToSpeed(lw):
    ''' The inverse of speedToLW, to get the speed back from the linewidth '''
    return (lw - 0.5) * 5.


def gc_var_to_csv(rundir, variables=[], year='', version='12.9.3'):
    
    print(variables)

    gc_var=[] ; times=[]
    for i,infile in enumerate(sorted(glob.glob('/users/mjr583/scratch/GC/%s/%s/output/GEOSChem.SpeciesConc.*%s*.nc4' % (version, rundir, year)))):
        print(infile)
    
        for gc_name in variables:
            if gc_name in d:
                gc_name=d[variable]['GC_name']
            
            fh=Dataset(infile)
            var=fh.variables['SpeciesConc_%s' %gc_name][:]
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


def get_gc_bc(rundir, var, version='12.9.3'):
    print('here')
    CO=[] ; times=[]
    for infile in sorted(glob.glob('/users/mjr583/scratch/GC/%s/rundirs/%s/GC_BC/GEOSChem.Boundary*201708*.nc4' %(version, rundir))):
        print(infile)
        fh=Dataset(infile)
        lat=fh.variables['lat'][:]
        lon=fh.variables['lon'][:]
        lev=fh.variables['hyam'][:]

        co = fh.variables['SpeciesBC_%s' %var][:]*1e9
        CO.append(co)
        time=fh.variables['time']
        times.append( GC_time_to_datetime(fh, time) ) 
    var=np.concatenate(CO)

    return var, lat, lon, lev, time


def GC_time_to_datetime(fh,time):
    t0=fh.variables['time'].units
    t0=(int, re.findall(r'\d+', t0))[1]
    t0=datetime.datetime(int(t0[0]), int(t0[1]), int(t0[2]), int(t0[3]), int(t0[4]), int(t0[5]) )
    times=[]
    for dt in time[:]:
        times.append( t0 + datetime.timedelta(minutes=dt) )
    times=np.array(times)
    return times


def get_var_group(d, rundir, version, year=False):
    #key=list(d.keys())

    variable=[] ; times=[]
    if year:
        path='/users/mjr583/scratch/GC/%s/rundirs/%s/OutputDir/GEOSChem.SpeciesConc.*%s*.nc4' % (version, rundir, year)
    else:
        path='/users/mjr583/scratch/GC/%s/rundirs/%s/OutputDir/GEOSChem.SpeciesConc.*.nc4' % (version, rundir)

    for i,infile in enumerate(sorted(glob.glob(path))):
        print(infile)
        fh=Dataset(infile)
        var=fh.variables['SpeciesConc_%s' %d['comp'][0]][:]
        
        for i,ii in enumerate(d['comp'][1:]):
            var+= ( fh.variables['SpeciesConc_%s' %ii][:] ) * d['sf'][i]
        variable.append(var)
        
        time=fh.variables['time'][:]
        t0=fh.variables['time'].units
        t0=(int, re.findall(r'\d+', t0))[1]
        t0=datetime.datetime(int(t0[0]), int(t0[1]), int(t0[2]), int(t0[3]), int(t0[4]), int(t0[5]) )
        for dt in time:
            times.append( t0 + datetime.timedelta(minutes=dt) )
        
        lat=fh.variables['lat'][:]
        lon=fh.variables['lon'][:]
        lev=fh.variables['hyam'][:]

    try:
        var=np.array(variable)
        SHAPE=var.shape
        var=np.reshape(var, (SHAPE[0]*SHAPE[1], SHAPE[2], SHAPE[3], SHAPE[4]))
        var=np.array(var)
    except:
        var=np.concatenate(variable)

    var = var * d['conv']

    return var, lat, lon, lev, times
 

def read_collection(data_dir, collection):
    """
    Reads data from all of specified collection netCDF files
    into a single xarray Dataset.

    Args:
    -----
        data_dir : str
            Directory containing data files.
            Default: "./OutputDir".

    Returns:
    --------
        ds : xarray Dataset
    """

    # Find a list of all MeanOH collection files in data_dir.
    # Walk through subdirectories of data_dir if they exist.
    path='/users/mjr583/scratch/GC/GEOS-Chem/rundirs/'
    data_dir = path+data_dir+"/OutputDir"
    file_list = []
    for root, dirs, files in os.walk(data_dir):
        if len(dirs) > 0:
            for d in dirs:
                for f in files:
                    if ".%s." %collection in f:
                        file_list.append(os.path.join(root, d, f))
        else:
            for f in files:
                if ".%s." %collection in f:
                    file_list.append(os.path.join(root, f))
    # Combine data into a single dataset
    # Exit if we do not have all necessary metrics variables
    ds = combine_dataset(file_list)

    return ds


def combine_dataset(file_list=None):
    """
    Wrapper for xarray.open_mfdataset, taking into account the
    extra arguments needed in xarray 0.15 and later.

    Args:
    -----
        file_list : list of str

    Returns:
    --------
        ds : xarray Dataset
    """

    # netCDF variables that we should skip reading
    # (These are from older versions of GCHP output)
    skip_these_vars = ["anchor",
                       "ncontact",
                       "orientation",
                       "contacts",
                       "cubed_sphere"]

    # Return a single Dataset containing data from all MeanOH files.
    # NOTE: Need to add combine="nested" and concat_dim="time"
    # for xarray 0.15 and higher!!!
    v = xr.__version__.split(".")
    if int(v[0]) == 0 and int(v[1]) >= 15:
        try:
            ds = xr.open_mfdataset(
                file_list,
                drop_variables=skip_these_vars,
                combine="nested",
                concat_dim="time"
            )
        except FileNotFoundError:
            msg = "Could not find one or more files in {}".format(file_list)
            raise FileNotFoundError(msg)
    else:
        try:
            ds = xr.open_mfdataset(
                file_list,
                drop_variables=skip_these_vars
            )
        except FileNotFoundError:
            msg = "Could not find one or more files in {}".format(file_list)
            raise FileNotFoundError(msg)

    return ds


### DICTIONARIES ####

Iy = { 'name' : 'Iy',
        'abbr' : '$I_y$',
        'comp' : ['I2', 'HOI','IO','OIO','HI','INO','I2O2','I2O3','I2O4'],
        'sf' : [2,1,1,1,1,1,2,2,2],
        'conv' : 1e12,
        'unit' : 'ppt'
        }

Bry = { 'name' : 'Bry',
        'abbr' : '$Br_y$',
        'comp' : ['Br', 'Br2','HOBr','BrO','HBr','BrNO2','BrNO3','IBr','BrCl'],
        'sf' : [1,2,1,1,1,1,1,1,1],
        'conv' : 1e12,
        'unit' : 'ppt'
        }

Cly = { 'name' : 'Cly',
        'abbr' : '$Cl_y$',
        'comp' : ['Cl','Cl2','HOCl','ClO','HCl','ClNO2','ClNO3','ICl','BrCl','ClOO','OClO','Cl2O2'],
        'sf' : [1,2,1,1,1,1,1,1,1,1,1,2],
        'conv' : 1e12,
        'unit' : 'ppt'
        }

NOx = { 'name' : 'NOx',
        'abbr' : '$NO_x$',
        'comp' : ['NO', 'NO2'],
        'sf' : [1,1],
        'conv' : 1e12,
        'unit' : 'ppt'
        }

