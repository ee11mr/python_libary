#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 12:52:32 2020

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
import glob


def get_from_merge(d, timestep=False):
    filepath  = '/users/mjr583/scratch/NCAS_CVAO/CVAO_datasets/'
    filen = glob.glob(filepath+'*erge.csv')[0]
    dtf = pd.read_csv(filen, index_col=0,dtype={'Airmass':str, 'New_Airmass':str})
    try:
        dtf.index = pd.to_datetime(dtf.index,format='%d/%m/%Y %H:%M')
    except:
        dtf.index = pd.to_datetime(dtf.index,format='%Y-%m-%d %H:%M:%S')


    filen=filepath+'cv_ovocs_2018_M_Rowlinson.csv'
    odf = pd.read_csv(filen, index_col=0)
    try:
        odf.index = pd.to_datetime(odf.index,format='%d/%m/%Y %H:%M')
    except:
        odf.index = pd.to_datetime(odf.index,format='%Y-%m-%d %H:%M:%S')
    
    cols=list(dtf) ; ocols = list(odf)
    if d['merge_name'] in cols:
        df = dtf[d['merge_name']]
    elif d['merge_name'] in ocols:
        df = odf[d['merge_name']]
    else:
        print(cols)
        print(ocols)
        print(d['merge_name'])

    df = df.loc[~(df <= 0. )]
    df = pd.DataFrame(df) ; df.columns = [d['variable']]
    
    if timestep:
        mindex = df.resample(timestep).mean().index
        df = pd.DataFrame({'mean':df[df.columns[0]].resample(timestep).mean(),
            'median':df[df.columns[0]].resample(timestep).median(),
            #'min':df[df.columns[0]].resample(timestep).min(),
            #'max':df[df.columns[0]].resample(timestep).max(),
            '10th':df[df.columns[0]].resample(timestep).quantile(0.1),
            '90th':df[df.columns[0]].resample(timestep).quantile(0.9)},
            index=mindex)
    else:
        df.columns=['Value']
    
    return df


def get_dataset_from_merge(d, timestep='M', ):
    filepath  = '/users/mjr583/scratch/NCAS_CVAO/CVAO_datasets/'
    filen = filepath+'20200908_CV_Merge.csv'
    dtf = pd.read_csv(filen, index_col=0,dtype={'Airmass':str, 'New_Airmass':str})
    dtf.index = pd.to_datetime(dtf.index,format='%Y-%m-%d %H:%M:%S')

    filen=filepath+'cv_ovocs_2018_M_Rowlinson.csv'
    odf = pd.read_csv(filen, index_col=0)
    odf.index = pd.to_datetime(odf.index,format='%d/%m/%Y %H:%M')
    
    cols=list(dtf) ; ocols = list(odf)
    for col in cols:
        try:
            dtf[col] = dtf[col].loc[~(dtf[col] <= 0. )]
        except:
            pass
    for col in ocols:
        odf = odf.loc[~(odf[col] <= 0.)]
    cols=cols+ocols
        
    df=dtf.resample('H').mean()
    odf=odf.resample('H').mean()
    dtf=pd.concat([df,odf], axis=1, sort=False)
    dtf = dtf[d['merge_name']]
    dtf = pd.DataFrame(dtf)
    dtf.columns = [d['variable']]

    df = dtf.resample(timestep).mean()
    dates = df.index
    return df, dates


def get_met_data_from_merge(d, timestep='M'):
    filepath  = '/users/mjr583/scratch/NCAS_CVAO/CVAO_datasets/'
    filen = filepath+'20200908_CV_Merge.csv'
    dtf = pd.read_csv(filen, index_col=0,dtype={'Airmass':str, 'New_Airmass':str})
    dtf.index = pd.to_datetime(dtf.index,format='%d/%m/%Y %H:%M')
    
    dtf = dtf[d['merge_name']]
    if d['negs'] == 'No':
        try:
            dtf = dtf.loc[~(dtf <= 0. )]
        except:
            pass

    dtf = pd.DataFrame(dtf)
    dtf.columns = [d['variable']]
    df = dtf.resample(timestep).mean()
    dates = df.index
    return df, dates


def get_dataset_as_df(D, timestep='M'):    
    dataset = netCDF4.Dataset(D['ebas_url'])
    time = dataset.variables['time'][:]
    time=np.array(timestamp_to_date(time))
    mean = dataset.variables[D['ebas_var_name']][:] 
    flag = dataset.variables[D['ebas_var_name']+'_qc'][:][0]
    
    fltr = np.where(flag!=0)
    mean[fltr]=np.nan
    
    dtf = pd.DataFrame(mean)
    dtf.index = time
    dtf.columns = [D['variable']]

    df = dtf.resample(timestep).mean()
    dates=df.index
    return dataset, df, dates, flag


def get_nox_data(d, timestep='M'):
    filepath  = '/users/mjr583/scratch/NCAS_CVAO/CVAO_datasets/'
    filen = filepath+'Hourly_NOx_2007-2018_with_flags.csv'
    df = pd.read_csv(filen, index_col=0)
    df.index = pd.to_datetime(df.index,format='%Y-%m-%d %H:%M:%S')
    
    cols=list(df) 
    for col in cols:
        try:
            df[col] = df[col].loc[~(df[col] < 0. )]
        except:
            pass

    if d['variable'] == 'NOx':
        no_flag = df.loc[df['NO_Ozone_corrected_Flag'] == 0.0]
        no = no_flag['NO_pptV_Ozone_corrected']
    
        no2_flag = df.loc[df['NO2_Ozone_corrected_Flag'] == 0.0]
        no2 = no2_flag['NO2_pptV_Ozone_corrected']
        
        df = pd.DataFrame(no+no2)
    else:
        df = df.loc[df[d['variable']+'_Ozone_corrected_Flag'] == 0.0]
        df = df[d['variable']+'_pptV_Ozone_corrected']
        df = pd.DataFrame(df)
    df.columns = [d['variable']]
    df = df.resample(timestep).mean()
    dates = df.index
    return df, dates


def get_start_year(dataset, d):   
    try:
        start_year = eval(dataset.comment)['Startdate'][:4]
    except:
        start_year=d['start_year'] 
    from datetime import datetime
    end_year=datetime.today().strftime('%Y')
    years=np.arange(int(start_year),int(end_year))
    return start_year, end_year, years


def get_start_year_merge(df):
    start_year = df.index[0].strftime('%Y')
    end_year = df.index[-1].strftime('%Y')
    years=np.arange(int(start_year),int(end_year))
    return start_year, end_year, years


def timestamp_to_date(times):
    new_date=[]
    for t, tt in enumerate(times):
        print(tt)
        tt=int(tt)
        x = (datetime.datetime(1900,1,1,0,0) + datetime.timedelta(tt-1))
        new_date.append(x)
    return new_date


def dates_to_datetime(year,month,day,hour,mins=False,sec=False):

    return dt


def curve_fit_function(df,X,Y, start, timestep='monthly'):
    ''' Guess of polynomial terms '''
    z, p = np.polyfit(X, Y, 1)
    a = np.mean(Y.resample('A').mean())
    b = z
    c2 = .00001
    A1 = 5.1 
    A2 = 0.5
    B1 = 0.1
    B2 = 0.5
    s1 = 1/8760 * 2*np.pi
    s2 = 5000/8760 * 2*np.pi   
    s3 = 12/24 * np.pi
    s4 = 2/24 * np.pi
    if timestep == 'monthly' or timestep == 'Monthly' or timestep =='M':
        def re_func(t,a,b,c2,A1,s1,A2,s2):
            return a + b*t + c2*t**2 + A1*np.sin(t/12*2*np.pi + s1) + A2*np.sin(2*t/12*2*np.pi + s2)
        guess = np.array([a, b, c2, A1, s1,A2,s2])

        c,cov = curve_fit(re_func, X, Y, guess)
        perr = np.sqrt(np.diag(cov))
        n = len(X)
        y = np.empty(n)
        for i in range(n):
            y[i] = re_func(X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6])

    elif timestep == 'weekly' or timestep == 'Weekly' or timestep == 'W':
        def re_func(t,a,b,c2,A1,s1,A2,s2, B1, s3, B2, s4):
            return a + b*t + c2*t**2 + A1*np.sin(t/52*2*np.pi + s1) + A2*np.sin(2*t/52*2*np.pi + s2) + B1*np.sin(t/24*2*np.pi + s3) + B2*np.sin(2*t/24*2*np.pi + s4)
        guess = np.array([a, b, c2, A1, s1,A2,s2,B1,s3,B2,s4])
        c,cov = curve_fit(re_func, X, Y, guess, maxfev=500000)
        n = len(X)
        y = np.empty(n)
        for i in range(n):
            y[i] = re_func(X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[8],c[9],c[10])

    elif timestep == 'hourly' or timestep == 'Hourly' or timestep == 'H':
        def re_func(t,a,b,c2,A1,s1,A2,s2, B1, s3, B2, s4):
            return a + b*t + c2*t**2 + A1*np.sin(t/8760*2*np.pi + s1) + A2*np.sin(2*t/8760*2*np.pi + s2) + B1*np.sin(t/24*2*np.pi + s3) + B2*np.sin(2*t/24*2*np.pi + s4)
        guess = np.array([a, b, c2, A1, s1,A2,s2,B1,s3,B2,s4])
        c,cov = curve_fit(re_func, X, Y, guess, maxfev=500000)
        n = len(X)
        y = np.empty(n)
        for i in range(n):
            y[i] = re_func(X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[8],c[9],c[10])
    else:
        print(timestep)
        raise Exception('Invalid timestep argument, must be daily ("D") or monthly ("M")')
    var = c[0] + c[1]*X + c[2]*X**2
    rmse = np.round(np.sqrt(mean_squared_error(Y,re_func( X, *c))),2)
    r2 = np.round(r2_score(Y,re_func( X, *c))*100,1)
    return y, var, z, rmse, r2, c


def curve_fit_function_NAO(df,X,Y, start, timestep='monthly'):
    nao = get_nao_index()
    idx = nao.index.intersection(Y.index)
    nao = ((nao.loc[idx]).values).flatten()
    ''' Guess of polynomial terms '''
    z, p = np.polyfit(X, Y, 1)
    a = np.mean(Y.resample('A').mean())
    b = z
    c2 = .00001
    N = 0.1
    A1 = 5.1 
    A2 = 0.5
    B1 = 0.1
    B2 = 0.5
    s1 = 1/8760 * 2*np.pi
    s2 = 5000/8760 * 2*np.pi   
    s3 = 12/24 * np.pi
    s4 = 2/24 * np.pi
    if timestep == 'monthly' or timestep == 'Monthly' or timestep =='M':
        def init_func(t,a,b,c2,A1,s1,A2,s2,N):
            return a + b*t + c2*t**2 + A1*np.sin(t/12*2*np.pi + s1) + A2*np.sin(2*t/12*2*np.pi + s2) + N*nao*t
        guess = np.array([a, b, c2, A1, s1,A2,s2,N])
        c,cov = curve_fit(init_func, X, Y, guess)
        
        def re_func(n,t,a,b,c2,A1,s1,A2,s2,N):
            return a + b*t + c2*t**2 + A1*np.sin(t/12*2*np.pi + s1) + A2*np.sin(2*t/12*2*np.pi + s2) + N*nao[n]
        n = len(X)
        y = np.empty(n)
        for i in range(n):
            y[i] = re_func(i, X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7])

    elif timestep == 'hourly' or timestep == 'Hourly' or timestep == 'H':
        def re_func(t,a,b,c2, A1,s1,A2,s2, B1, s3, B2, s4):
            return a + b*t + c2*t**2 +  A1*np.sin(t/8760*2*np.pi + s1) + A2*np.sin(2*t/8760*2*np.pi + s2) + B1*np.sin(t/24*2*np.pi + s3) + B2*np.sin(2*t/24*2*np.pi + s4)
        guess = np.array([a, b, c2, A1, s1,A2,s2,B1,s3,B2,s4])
        c,cov = curve_fit(re_func, X, Y, guess, maxfev=500000)
        n = len(X)
        y = np.empty(n)
        for i in range(n):
            y[i] = re_func(X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[8],c[9],c[10])
    else:
        raise Exception('Invalid timestep argument, must be daily ("D") or monthly ("M")')
    var = c[0] + c[1]*X + c[2]*X**2
    rmse = np.round(np.sqrt(mean_squared_error(Y,init_func( X, *c))),2)
    r2 = np.round(r2_score(Y,init_func( X, *c))*100,1)
    return y, var, z, rmse, r2, c


def log_conc_curve_fit_function(df,X,Y, start, timestep='monthly'):
    ''' Guess of polynomial terms '''
    Y = np.log(Y)
    z, p = np.polyfit(X, Y, 1)
    a = np.mean(Y.resample('A').mean())
    b = z
    c2 = .00001
    A1 = 5.1 
    A2 = 0.5
    B1 = 0.1
    B2 = 0.5
    s1 = 1/8760 * 2*np.pi
    s2 = 5000/8760 * 2*np.pi   
    s3 = 12/24 * np.pi
    s4 = 2/24 * np.pi
    if timestep == 'monthly' or timestep == 'Monthly' or timestep =='M':
        def re_func(t,a,b,c2,A1,s1,A2,s2):
            return a + b*t + c2*t**2 + A1*np.sin(t/12*2*np.pi + s1) + A2*np.sin(2*t/12*2*np.pi + s2)
        guess = np.array([a, b, c2, A1, s1,A2,s2])
        c,cov = curve_fit(re_func, X, Y, guess)
        n = len(X)
        y = np.empty(n)
        for i in range(n):
            y[i] = re_func(X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6])

    elif timestep == 'hourly' or timestep == 'Hourly' or timestep == 'H':
        def re_func(t,a,b,c2,A1,s1,A2,s2, B1, s3, B2, s4):
            return a + b*t + c2*t**2 + A1*np.sin(t/8760*2*np.pi + s1) + A2*np.sin(2*t/8760*2*np.pi + s2) + B1*np.sin(t/24*2*np.pi + s3) + B2*np.sin(2*t/24*2*np.pi + s4)
        guess = np.array([a, b, c2, A1, s1,A2,s2,B1,s3,B2,s4])
        c,cov = curve_fit(re_func, X, Y, guess, maxfev=500000)
        n = len(X)
        y = np.empty(n)
        for i in range(n):
            y[i] = re_func(X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[8],c[9],c[10])
    else:
        raise Exception('Invalid timestep argument, must be daily ("D") or monthly ("M")')
    var = c[0] + c[1]*X + c[2]*X**2
    rmse = np.round(np.sqrt(mean_squared_error(Y,re_func( X, *c))),2)
    r2 = np.round(r2_score(Y,re_func( X, *c))*100,1)
    c = np.exp(c)
    y = np.exp(y)
    Y = np.exp(Y)
    var = np.exp(var)
    return y, var, z, rmse, r2, c


def plot_trend_breakdown(d, X, Y, c, start_year,times,timestep,savepath=''):
    detrended = [Y[i] - c[1]*i for i in range(0, len(X))]
    detrended2 = np.array([detrended[i] - c[2]*i**2 for i in range(0, len(X))])
    plt.plot(times,Y, label='Obervations')
    plt.plot(times,detrended,label='Detrend b')
    plt.plot(times,detrended2,label='Detrend b + c')
    plt.ylabel(d['abbr']+' ('+d['unit']+')')
    plt.legend()
    plt.savefig(savepath+d['variable']+'_trend_breakdown.png', dpi=200)
    plt.close()
    return


def plot_fitted_curve(d,X,Y,output,times,timestep, savepath=''):
    if timestep=='H':
        t='hourly'
        s=0.05
        l=0.2
    elif timestep=='M':
        t='monthly'
        s=0.5
        l=2
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(times, Y, 'ro', markersize=s)
    ax1.plot(times, output[0], '--', linewidth=l )
    ax1.plot(times, output[1], 'k')
    ''' Uncomment to add linear trendline and print trend 
    z = np.polyfit(X,Y,1)
    p = np.poly1d(z)    
    ax1.plot(times, p(X), '--', color='k', alpha=0.7)
    if timestep == 'M':
        tt = 12
    else:
        tt=8760
    print('Linear trend = ', np.round(z[0]*tt,2), d['unit'], '$yr^{-1}$')
    '''
    if 'abbr' in d:
        ax1.set_ylabel(d['abbr']+' ('+d['unit']+')')
    else:
        ax1.set_ylabel(d['longname']+' ('+d['unit']+')')
    
    if 'yscale' in d:
        yb, yt = ax1.get_ylim()
        if yt-yb > 1e4:
            ax1.set_yscale(d['yscale'])
    if output[2]>0.: # moves legend based on direction of trend
        loc=2
    elif output[2]<0.:
        loc=1
    txt = AnchoredText('RMSE='+str(output[3])+' '+d['unit']+'\n$r^2$='+str(output[4])+'%', loc=loc)
    ax1.add_artist(txt)
    plt.savefig(savepath+d['variable']+'/'+d['variable']+'_'+t+'_mean.png', dpi=200)
    plt.close()
    return


def plot_o3_curve_from_df(d,X,Y,output,timestep, pref='cv', savepath=''):
    if timestep=='H':
        t='hourly'
        s=0.05
        l=0.2
    elif timestep=='M':
        t='monthly'
        s=0.5
        l=2
    fig = plt.figure()
    times=Y.index
    ax1 = fig.add_subplot(111)
    ax1.plot(times, Y, 'ro', markersize=s)
    ax1.plot(times, output[0], '--', linewidth=l)
    ax1.plot(times, output[1], 'k')
    ax1.set_ylabel('$O_3$ (ppb)')
    if output[2]>0.: # moves legend based on direction of trend
        loc=2
    elif output[2]<0.:
        loc=1
    txt = AnchoredText('RMSE='+str(output[3])+' ppb \n$r^2$='+str(output[4])+'%', loc=loc)
    ax1.add_artist(txt)
    plt.savefig(savepath+pref+'_ozone_'+t+'_mean.png', dpi=300)
    plt.close()
    return


def plot_residual(d,X,Y,output,times,timestep, savepath='', nbins=25):
    if timestep=='H':
        t='hourly'
    elif timestep=='M':
        t='monthly'
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax1.plot(times, Y-output[0], 'g', label='Residual')
    if 'abbr' in d:
        label=d['abbr']+' ('+d['unit']+')'
    else:
        label=d['longname']+' ('+d['unit']+')'
    ax1.set_ylabel(label)
    
    ax2 = fig.add_subplot(212)
    ax2.hist( Y-output[0], bins=nbins, density=True, alpha=0.6, color='g')
    ax2.set_xlabel(label)
    ax2.set_ylabel('freq')
    fig.suptitle('Residual - '+t+' means')
    plt.savefig(savepath+d['variable']+'/'+d['variable']+'_'+t+'_residual.png', dpi=200)
    plt.close()
    return


def remove_nan_rows(df,times):
    '''
    Remove nan values from dataset.

    Parameters
    ----------
    df (array): Pandas DataFrame - Variable dataset
    times (array): Index/timestep for df

    Returns
    -------
    X (array) : Nan corrected array of time integers
    Y (pd.Series) : Nan corrected concentrations
    time (array) : Nan corrected datetime array
    Notes
    '''
    cols=df.columns
    df_list=[]
    for i in range(len(cols)):
        XX = np.arange(len(df[df.columns[i]]))
        idx = np.isfinite(df[df.columns[i]])
        Y = df[df.columns[i]][idx]
        df_list.append(Y)
        X = XX[idx]
        time = times[idx]
    Y =  pd.concat(df_list, axis=1)    
    
    return X, Y, time


def import_gaw_data(url='ftp://aftp.cmdl.noaa.gov/data/ozwv/SurfaceOzone/PCO/pco_o3_ppb_2001-2015.dat', path='/users/mjr583/scratch/NCAS_CVAO/GAW_data/', start='2006'):
    import urllib
    import pandas as pd
    fname = url.split('/')[-1]
    urllib.request.urlretrieve(url, path+fname)
    
    df=pd.read_csv(path+fname, header=22, delimiter=';', index_col=0)
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d  %H:%M').strftime('%Y/%m/%d %H:%M')
    df.index = pd.to_datetime(df.index)
    df.columns = ['Value']
    df = df[df.Value != -999.0]
    df = df['2006':]
    return df


def create_directories(d, savepath):
    directory = savepath+d['variable']+'/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    return

def plot_trend_with_func_from_dict(d, timestep='M', force_merge=False,\
                                   savepath='/users/mjr583/scratch/NCAS_CVAO/trend_plots/'):
    '''
    Get CVAO for data in dict and plot over time with curved fit.
    Can extract data from merge_file or url. 

    Parameters
    ----------
    d (dict): Dictionary of desired species with relevant fields
    Timestep (str): Timestep for trend fit, hourly ("H") or monthly ("M")
    force_merge (bool): Takes all datasets from merge file, default is to attmpet url first.
    savepath (str): path to save directory for plots.

    Returns
    -------
    (plots)

    Notes
    '''
    for i in d:
        create_directories(d[i], savepath)
        if force_merge == False:
            if i == 'NO' or i=='NO2' or i=='NOx':
                df, time = get_nox_data(d[i], timestep=timestep)
                start, end, years = get_start_year_merge(df)  
            else:
                try:
                    dataset, df, time = get_dataset_as_df(d[i], timestep=timestep)
                    start, end, years = get_start_year(dataset, d[i]) 
                except:
                    df, time = get_dataset_from_merge(d[i], timestep=timestep)
                    start, end, years = get_start_year_merge(df)                
        elif force_merge== True:
            df, time = get_dataset_from_merge(d[i], timestep=timestep)
            start, end, years = get_start_year_merge(df) 
        print(type(df))
        X, Y, time = remove_nan_rows(df, time)
        if X.size == 0:
            print('No values for ', df.columns[0])
            pass
        elif Y.size <=5:
            print('Insufficient data for ', i)
            pass
        else:
            if d[i]['yscale']=='linear':
                output = curve_fit_function(df, X, Y, start, timestep=timestep)
            elif d[i]['yscale']=='log':
                output = log_conc_curve_fit_function(df, X, Y, start, timestep=timestep)
                    
            plot_fitted_curve(d[i],X, Y, output, times=time, timestep=timestep, savepath=savepath)
            plot_residual(d[i],X, Y, output, times=time, timestep=timestep, savepath=savepath)
            #if timestep=='M':
                #plot_trend_breakdown(d[i], X, Y, output[5], start, times=time, timestep=timestep,savepath=savepath)
            print(i, 'done')
    return 


def met_trends_with_func_from_dict(d, timestep='M', force_merge=True,\
                                   savepath='/users/mjr583/scratch/NCAS_CVAO/trend_plots/'):
    '''
    Get CVAO trends for MET data in dict and plot over time with curved fit.
    Can extract data from merge_file or url. 

    Parameters
    ----------
    d (dict): Dictionary of desired species with relevant fields
    Timestep (str): Timestep for trend fit, hourly ("H") or monthly ("M")
    force_merge (bool): Takes all datasets from merge file, default is to attmpet url first.
    savepath (str): path to save directory for plots.

    Returns
    -------
    (plots)

    Notes
    '''
    for i in d:
        create_directories(d[i], savepath)
        df, time = get_met_data_from_merge(d[i], timestep=timestep)
        start, end, years = get_start_year_merge(df) 
            
        X, Y, time = remove_nan_rows(df[i], time)
        if X.size == 0:
            print('No values for ', df.columns[0])
            pass
        elif Y.size <=5:
            print('Insufficient data for ', i)
            pass
        else:
            if d[i]['yscale']=='linear':
                output = curve_fit_function(df, X, Y, start, timestep=timestep)
            elif d[i]['yscale']=='log':
                output = log_conc_curve_fit_function(df, X, Y, start, timestep=timestep)
                         
            plot_fitted_curve(d[i],X, Y, output, times=time, timestep=timestep, savepath=savepath)
            plot_residual(d[i],X, Y, output, times=time, timestep=timestep, savepath=savepath)
            #if timestep=='M':
                #plot_trend_breakdown(d[i], X, Y, output[5], start, times=time, timestep=timestep,savepath=savepath)
            print(i, 'done')
    return 


def get_nao_index():
    path='/users/mjr583/scratch/NCAS_CVAO/CVAO_datasets/nao_index.txt'
    nao = pd.read_csv(path, header=0, delimiter=',')
    nao['Datetime'] = nao['Date'].map(str)
    from pandas.tseries.offsets import MonthEnd
    nao.index = pd.to_datetime(nao['Datetime'], format="%Y%m")# + MonthEnd(1)
    nao = pd.DataFrame(nao['Value'])
    return nao


def get_enso_index():
    path='/users/mjr583/scratch/NCAS_CVAO/CVAO_datasets/enso_mei2.txt'
    enso = pd.read_csv(path, sep='\t', lineterminator='\r')
    enso=np.array(enso)
    enso=np.reshape(enso,(43*12))
    enso=pd.DataFrame({'enso':enso})
    
    start=datetime.datetime(1979,1,1,0,0)
    dates=[]
    from dateutil.relativedelta import relativedelta
    for i in range(len(enso)):
        x=start + relativedelta(months=+i) 
        dates.append(x)
    dates=np.array(dates)
    enso.index=dates
    
    enso=enso[:'2020']
    return enso

def get_percentiles(d, timestep='M'):
    df  = get_from_merge(d, timestep='M')
    hf  = get_from_merge(d, timestep='H')
    X, Y, time = remove_nan_rows(df, df.index)
    YY =Y
    if len(Y) < 10:
        print('Not enough data')
        pass
    else:
        hold=[]
        fig,(ax,ax2)=plt.subplots(nrows=2, gridspec_kw={'height_ratios' : [3,1]}, sharex=True)
        ax.scatter(hf.index,hf['mean'],s=1.7,color='k', alpha=0.1)
        colors=['','','r','g']
        for ii in reversed(range(len(YY.columns))):
            Y = YY[YY.columns[ii]]
            
            z, p = np.polyfit(X, Y, 1)
            a = np.mean(Y.resample('A').mean())
            b = z
            c2 = .00001
            A1 = 5.1 
            A2 = 0.5
            B1 = 0.1
            B2 = 0.5
            s1 = 1/8760 * 2*np.pi
            s2 = 5000/8760 * 2*np.pi   
            s3 = 12/24 * np.pi
            s4 = 2/24 * np.pi
            if timestep == 'monthly' or timestep == 'Monthly' or timestep =='M':
                def re_func(t,a,b,c2,A1,s1,A2,s2):
                    return a + b*t + c2*t**2 + A1*np.sin(t/12*2*np.pi + s1) + A2*np.sin(2*t/12*2*np.pi + s2)
                guess = np.array([a, b, c2, A1, s1,A2,s2])
                c,cov = curve_fit(re_func, X, Y, guess)
                n = len(X)
                y = np.empty(n)
                for i in range(n):
                    y[i] = re_func(X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6])
        
            elif timestep == 'hourly' or timestep == 'Hourly' or timestep == 'H':
                def re_func(t,a,b,c2,A1,s1,A2,s2, B1, s3, B2, s4):
                    return a + b*t + c2*t**2 + A1*np.sin(t/8760*2*np.pi + s1) + A2*np.sin(2*t/8760*2*np.pi + s2) + B1*np.sin(t/24*2*np.pi + s3) + B2*np.sin(2*t/24*2*np.pi + s4)
                guess = np.array([a, b, c2, A1, s1,A2,s2,B1,s3,B2,s4])
                c,cov = curve_fit(re_func, X, Y, guess, maxfev=500000)
                n = len(X)
                y = np.empty(n)
                for i in range(n):
                    y[i] = re_func(X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[8],c[9],c[10])
            else:
                raise Exception('Invalid timestep argument: Must be daily ("D") or monthly ("M")')
            var = c[0] + c[1]*X + c[2]*X**2
            hold.append(var)
            if 'th' in YY.columns[ii]:
                ax.plot(time,var, label=(YY.columns[ii]+' (z='+str(np.round(z*12,2))+' '+d['unit']+' $yr^{-1}$)'), color=colors[ii])
                ax.plot(time,y, linestyle='--', color=colors[ii])
        ax2.get_shared_x_axes().join(ax2,ax)
        
        pc = (hold[3]-hold[2])/YY['mean'].mean() * 100
        
        ax2.plot(time, hold[3]-hold[2], 'k--', label='Seasonal range')
        ax3=ax2.twinx()
        ax3.plot(time, pc, 'k--', label='Seasonal range')
        
        ax.set_ylabel(d['abbr']+' ('+d['unit']+')')
        ax.legend(ncol=1,loc=0)
        ax2.set_ylabel(d['unit'])
        ax3.set_ylabel('% of mean')
        ax2.set_title('Seasonal amplitude')
        plt.subplots_adjust(hspace=.3)
        plt.savefig('/users/mjr583/scratch/NCAS_CVAO/percentile_plots/'+d['variable']+'.png')
        plt.close()
      

def get_timeseries(d, timestep='M'):
    df  = get_from_merge(d, timestep='M')
    hf  = get_from_merge(d, timestep='H')
     
    if 'acet' in d['variable'] or 'meoh' in d['variable']:
        df=df['2015':]
        hf=hf['2015':]

    X, Y, time = remove_nan_rows(df, df.index)
    
    YY =Y
    if len(Y) < 10:
        print('Not enough data')
        pass
    else:
        hold=[]
        fig,(ax)=plt.subplots()
        ax.scatter(hf.index,hf['mean'],s=1.7,color='k', alpha=0.1)
        colors=['r','g','r','g']
        for ii in reversed(range(len(YY.columns))):
            Y = YY[YY.columns[ii]]
            
            z, p = np.polyfit(X, Y, 1)
            a = np.mean(Y.resample('A').mean())
            b = z
            c2 = .00001
            A1 = 5.1 
            A2 = 0.5
            B1 = 0.1
            B2 = 0.5
            s1 = 1/8760 * 2*np.pi
            s2 = 5000/8760 * 2*np.pi   
            s3 = 12/24 * np.pi
            s4 = 2/24 * np.pi
            if timestep == 'monthly' or timestep == 'Monthly' or timestep =='M':
                def re_func(t,a,b,c2,A1,s1,A2,s2):
                    return a + b*t + c2*t**2 + A1*np.sin(t/12*2*np.pi + s1) + A2*np.sin(2*t/12*2*np.pi + s2)
                guess = np.array([a, b, c2, A1, s1,A2,s2])
                c,cov = curve_fit(re_func, X, Y, guess)
                n = len(X)
                y = np.empty(n)
                for i in range(n):
                    y[i] = re_func(X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6])
        
            elif timestep == 'hourly' or timestep == 'Hourly' or timestep == 'H':
                def re_func(t,a,b,c2,A1,s1,A2,s2, B1, s3, B2, s4):
                    return a + b*t + c2*t**2 + A1*np.sin(t/8760*2*np.pi + s1) + A2*np.sin(2*t/8760*2*np.pi + s2) + B1*np.sin(t/24*2*np.pi + s3) + B2*np.sin(2*t/24*2*np.pi + s4)
                guess = np.array([a, b, c2, A1, s1,A2,s2,B1,s3,B2,s4])
                c,cov = curve_fit(re_func, X, Y, guess, maxfev=500000)
                n = len(X)
                y = np.empty(n)
                for i in range(n):
                    y[i] = re_func(X[i],c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[8],c[9],c[10])
            else:
                raise Exception('Invalid timestep argument: Must be daily ("D") or monthly ("M")')
            var = c[0] + c[1]*X + c[2]*X**2
            hold.append(var)
            if 'mean' in YY.columns[ii]:
                ax.plot(time,var, color=colors[ii])# label=(YY.columns[ii]+' (z='+str(np.round(z*12,2))+' '+d['unit']+' $yr^{-1}$)'), color=colors[ii])
                ax.plot(time,y, linestyle='--', color=colors[ii])
        
        pc = (hold[3]-hold[2])/YY['mean'].mean() * 100
        
        
        ax.set_ylabel(d['abbr']+' ('+d['unit']+')')
        #ax.legend(ncol=1,loc=0)
        plt.savefig('/users/mjr583/scratch/NCAS_CVAO/timeseries/'+d['variable']+'.png')
        plt.close()
