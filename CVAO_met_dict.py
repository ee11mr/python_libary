#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 10:21:20 2020
Dictionary of variables measured at Cape Verde Observtory and relevent 
information for dataset access, processing and plotting. 
@author: mjr583
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error, r2_score
from matplotlib.offsetbox import AnchoredText
import netCDF4
import datetime     
import os



#'WINDSPD_10M (m/s)', 'WINDDIR_10M (deg)',
#       'TEMP_10M (degC)', 'RH_10M (%)', 'FILLED_TEMP (degC)', 'FILLED_RH (%)',
#       'RAINFALL (mm)', 'H2O (%)',
#       'ATMOSPHERIC PRESSURE (HPA)_CV-MET-CAMPBELL ',
#       'SOLAR RADIATION (WM-2)_CV-MET-CAMPBELL', 'JO1D (s-1)',

MET_dict = {
     'wspd_10' : {'variable' : 'wspd_10',   
                 'longname' : 'Wind Speed at 10m',
                 'unit': 'm $s^1$',
                 'start_year' : '2006',
                 'yscale' : 'linear',
                 'negs' : 'No',
                 'merge_name' : 'WINDSPD_10M (m/s)',
                 'instrument' : ''
                 },
     'wdir_10' : {'variable' : 'wdir_10',   
                 'longname' : 'Wind Direction at 10m',
                 'unit': 'deg',
                 'start_year' : '2006',
                 'yscale' : 'linear',
                 'negs' : 'No',
                 'merge_name' : 'WINDDIR_10M (deg)',
                 'instrument' : ''
                 },
     'temp_10' : {'variable' : 'temp_10',   
                 'longname' : 'Temperature at 10m',
                 'unit': 'degC',
                 'start_year' : '2006',
                 'yscale' : 'linear',
                 'negs' : 'Yes',
                 'merge_name' : 'TEMP_10M (degC)',
                 'instrument' : ''
                 },
     'RH_10' : {'variable' : 'RH_10',   
                 'longname' : 'Relative Humidity at 10m',
                 'unit': '%',
                 'start_year' : '2006',
                 'yscale' : 'linear',
                 'negs' : 'No',
                 'merge_name' : 'RH_10M (%)',
                 'instrument' : ''
                 },
     'filled_temp' : {'variable' : 'filled_temp',   
                 'longname' : 'Filled Temperature',
                 'unit': 'degC',
                 'start_year' : '2006',
                 'yscale' : 'linear',
                 'negs' : 'Yes',
                 'merge_name' : 'FILLED_TEMP (degC)',
                 'instrument' : ''
                 },
     'filled_rh' : {'variable' : 'filled_rh',   
                 'longname' : 'Filled Relative Humidity',
                 'unit': 'm $s^1$',
                 'start_year' : '2006',
                 'yscale' : 'linear',
                 'negs' : 'No',
                 'merge_name' : 'FILLED_RH (%)',
                 'instrument' : ''
                 },
     'rainfall' : {'variable' : 'rainfall',   
                 'longname' : 'Rainfall',
                 'unit': 'mm',
                 'start_year' : '2006',
                 'yscale' : 'linear',
                 'negs' : 'No',
                 'merge_name' : 'RAINFALL (mm)',
                 'instrument' : ''
                 },
     'H2O' : {'variable' : 'H2O',   
                 'longname' : 'H2O',
                 'unit': '%',
                 'start_year' : '2006',
                 'yscale' : 'linear',
                 'negs' : 'No',
                 'merge_name' : 'H2O (%)',
                 'instrument' : ''
                 },
     'atmos_pres' : {'variable' : 'atmos_pres',   
                 'longname' : 'Atmospheric Pressure ',
                 'unit': 'hPa',
                 'start_year' : '2006',
                 'yscale' : 'linear',
                 'negs' : 'No',
                 'merge_name' : 'ATMOSPHERIC PRESSURE (HPA)_CV-MET-CAMPBELL ',
                 'instrument' : ''
                 },
     'solar_radiation' : {'variable' : 'solar_radiation',   
                 'longname' : 'Solar Radiation',
                 'unit': 'W$M^{-2}$',
                 'start_year' : '2006',
                 'yscale' : 'log',
                 'negs' : 'No',
                 'merge_name' : 'SOLAR RADIATION (WM-2)_CV-MET-CAMPBELL',
                 'instrument' : ''
                 },
     'jo1d' : {'variable' : 'jo1d',   
                 'longname' : 'Photolysis',
                 'unit': '$s^{-1}$',
                 'start_year' : '2006',
                 'yscale' : 'log',
                 'negs' : 'No',
                 'merge_name' : 'JO1D (s-1)',
                 'instrument' : ''
                 },
     
     }