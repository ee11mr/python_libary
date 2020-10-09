'''
This file contains python functions that can be used to process, 
interpret, analyse and plot data from the Cape Verde Atmospheric 
Observatory (CVAO: XXXN, XXXW), and corresponding FLEXPART trajectory 
simulations.
Created by M.J Rowlinson
Last updated: 03/06/2020 16:54
'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
import seaborn as sns
import matplotlib.dates as mdates 
import datetime
from functools import reduce
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import shiftgrid
import matplotlib.colors as colors
import glob
from netCDF4 import Dataset
import CVAO_tools as CV
from CVAO_dict import CVAO_dict as d


def gen_file_list(start,end=False,site='cvao',res='05x05',add=''):
    if add != '':
        add='_'+add
    print('Get file list')
    file_list=[]
    if end:
        years=np.arange(int(start),int(end)+1,1)
    else:
        years=[str(start)]
    for y in years:
        y=str(y)
        print('/users/mjr583/scratch/flexpart/cvao/'+res+'/'+y+add+'/netcdfs/'+y+'*.nc')

        if site=='cvao':
            traj='/users/mjr583/scratch/flexpart/cvao/'+res+'/'+y+add+'/netcdfs/'+y+'*.nc'
        else:
            traj='/users/mjr583/scratch/flexpart/'+site+'/'+y+add+'/netcdfs/'+y+'*.nc'
        for nfile in sorted(glob.glob(traj)):
            file_list.append(nfile)
    return file_list


def gen_trajectory_dates(start,end,site='cvao',res='05x05'):
    print('Get list of dates of back-trajectories')
    file_list=[]
    from datetime import datetime, timedelta
    startdate=datetime(int(start[:4]),int(start[4:6]),int(start[6:8]))
    enddate=datetime(int(end[:4]),int(end[4:6]),int(end[6:8]))
    delta= enddate-startdate

    days=[]
    for i in range( delta.days +1):
        days.append((startdate + timedelta(days=i)).strftime('%Y%m%d'))
    
    for d in days:
        d=str(d)
        if site=='cvao':
            traj='/users/mjr583/scratch/flexpart/cvao/'+res+'/'+d[:4]+'/netcdfs/'+d+'*.nc'
        else:
            traj='/users/mjr583/scratch/flexpart/'+site+'/'+d[:4]+'/netcdfs/'+d+'*.nc'
        for nfile in sorted(glob.glob(traj)):
            file_list.append(nfile)
    return file_list

def get_datetimes(file_list):
    datetimes=[]
    import dateutil.parser as dparser
    import re
    from datetime import datetime
    for f in file_list:
        match=re.search(r'\d{4}\d{2}\d{2}\d{2}', f)
        date = datetime.strptime(match.group(),"%Y%m%d%H")#.date()
        date = datetime.strftime(date,"%d/%m/%Y %H:%M")
        datetimes.append(date)
    return datetimes


def get_coords(file_list):
    print('Get particle coordinates')
    lats=[] ; lons=[] ; alts=[]
    for infile in file_list:
        #print(infile) 
        fh=Dataset(infile)
        
        lon=fh.variables['Longitude'][:]
        lat=fh.variables['Latitude'][:]
        alt=fh.variables['Altitude'][:]
        
        lons.append(lon)
        lats.append(lat)
        alts.append(alt)

    lons=np.array(lons)
    lats=np.array(lats)
    alts=np.array(alts)

    return lons,lats,alts


def input_dates():
    start_date=input('Start date (MM/YYYY): ')
    end_date=input('End date (MM/YYYY): ')
    if end_date=='':
        end_date=start_date
    dates=[start_date, end_date]
    return dates


def get_CVAO_species(species, start=False, end=False, timestep='H'):
    df=CV.get_from_merge(d[str(species)],timestep=timestep)
    X,Y,time = CV.remove_nan_rows(df,df.index)
    if start:
        if not end:
            end=start
        Y=Y[str(start):str(end)]
    return Y


def add_months(sourcedate, months):
    import calendar
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.datetime(year, month, day)


def calculate_months(dates):
    start=datetime.datetime.strptime(dates[0], '%m/%Y')
    end=datetime.datetime.strptime(dates[1], '%m/%Y')
    end=add_months(end,1)
        
    delta=end-start
    alldays=[]
    for i in range(delta.days + 1):
        days = start + datetime.timedelta(days=i)
        alldays.append(days)
    months=pd.DataFrame(alldays)
    months.index=pd.to_datetime(alldays)
    months=months.resample('M').max()[:-1]
    months=np.array(months.index.strftime('%m/%Y'))
    return months


def get_trajectories(site='cvao',start=2007,end=2019,add='',
                        monthopt=False,dayopt=False,dates=False, res='05x05'):
    if monthopt and not dates:
        dates=input_dates()
    elif monthop and dayopt:
        sys.exit('Pick months or days - not both')
    
    if add != '':
        add='_'+str(add)
    df_list=[]
    all_lons=[] ; all_lats=[] ; all_alts=[]
    
    if monthopt:
        months=calculate_months(dates=dates)
        for mon in months:
            y=str(mon[-4:])
            m=str(mon[:2])
            if site=='cvao':
                path='/users/mjr583/scratch/flexpart/'+site+'/'+res+'/'+y+'/netcdfs/'
            else:
                path='/users/mjr583/scratch/flexpart/'+site+'/'+res+'/'+y+'/netcdfs/'
            for infile in sorted(glob.glob(path+'/'+y+m+'*.nc')):
                #print(infile)
                fh=Dataset(infile)

                lats=fh.variables['Latitude'][:]
                lons=fh.variables['Longitude'][:]
                alts=fh.variables['Altitude'][:]
    
                all_lons.append(lons)
                all_lats.append(lats)
                all_alts.append(alts)

        lats=np.array(all_lats)
        lons=np.array(all_lons)
        alts=np.array(all_alts)
  
        length = lats.shape[0]*lats.shape[1]*lats.shape[2]
        lat = (np.reshape(lats, length)+90.).astype(int)
        lon = np.reshape(lons, length).astype(int)
        alt = np.reshape(alts, length).astype(int)

        lats=np.array(lats)
        lons=np.array(lons)
        alts=np.array(alts)

    else:
        years=np.arange(int(start),int(end),1)
        for y in years:
            y=str(y)
            if site=='cvao':
                path='/users/mjr583/scratch/flexpart/'+site+'/'+res+'/'+y+'/netcdfs/'
            else:
                path='/users/mjr583/scratch/flexpart/'+site+'/'+res+'/'+y+'/netcdfs/'
            for infile in sorted(glob.glob(path+'/'+y+'*.nc')):
                #print(infile)
                fh=Dataset(infile)
                lats=fh.variables['Latitude'][:]
                lons=fh.variables['Longitude'][:]
                alts=fh.variables['Altitude'][:]
    
                all_lons.append(lons)
                all_lats.append(lats)
                all_alts.append(alts)

            lats=np.array(all_lats)
            lons=np.array(all_lons)
            alts=np.array(all_alts)
  
            length = lats.shape[0]*lats.shape[1]*lats.shape[2]
            lat = (np.reshape(lats, length)+90.).astype(int)
            lon = np.reshape(lons, length).astype(int)
            alt = np.reshape(alts, length).astype(int)

            month_lats.append(lats)
            month_lons.append(lons)
            month_alts.append(alts)

        lats=np.array(month_lats)
        lons=np.array(month_lons)
        alts=np.array(month_alts)
    return lats,lons,alts,months


def get_grid(lon, lat, alt=False, limit=100):
    grid=np.zeros((180,360))
    for i in range(len(lon)):
        if type(alt)==bool:
            if lon[i]<0.:
                lon[i]=lon[i]+360.
            grid[int(lat[i]),int(lon[i])]+=1
        else:
            if alt[i] < limit:
                if lon[i]<0.:
                    lon[i]=lon[i]+360.
                grid[int(lat[i]),int(lon[i])]+=1

    grid = np.concatenate((grid[:,180:],grid[:,:180]),axis=1)
    fltr=np.where(grid==0.)
    grid[fltr]=np.nan

    return grid



def trajectory_to_grid(lats,lons,alts,limit=100):
    lat=[] ; lon=[] ; alt=[]
    length = lats.shape[0]*lats.shape[1]*lats.shape[2]
    lat=np.reshape(lats, length)+90.
    lon=np.reshape(lons, length)
    alt=np.reshape(alts, length)
    
    grid=np.zeros((180,360))
    for i in range(len(lon)):
        if alt[i]<=limit:
            if lon[i]<0.:
                lon[i]=lon[i]+360.
            grid[int(lat[i]),int(lon[i])]+=1
        else:
            pass
    grid = np.concatenate((grid[:,180:],grid[:,:180]),axis=1)
    fltr=np.where(grid==0.)
    grid[fltr]=np.nan

    return grid



def plot_trajectories(lats,lons,alts,months='',limit=100,savepath='/users/mjr583/scratch/flexpart/postprocess/monthly/plots/',
                        add='',res='1x1',savenote='',monthopt=False):
    lat=[] ; lon=[] ; alt=[]
    length = lats.shape[0]*lats.shape[1]*lats.shape[2]
    lat=np.reshape(lats, length)+90.
    lon=np.reshape(lons, length)
    alt=np.reshape(alts, length)
    
    grid=np.zeros((180,360))
    for i in range(len(lon)):
        if alt[i]<=limit:
            if lon[i]<0.:
                lon[i]=lon[i]+360.
            grid[int(lat[i]),int(lon[i])]+=1
        else:
            pass
    grid = np.concatenate((grid[:,180:],grid[:,:180]),axis=1)
    fltr=np.where(grid==0.)
    grid[fltr]=np.nan
    
    plottable=[grid]
    f,ax=create_figure(1)
    for i in range(len(plottable)):
        m=get_basemap(lllat=0., urlat=77, lllon=-100,urlon=40,ax=ax[i],lsmask=True)

        lats=range(-90,90)
        lons=range(-180,180)
        X,Y=np.meshgrid(lons,lats)
        m.pcolormesh(X,Y,grid,norm=colors.LogNorm(vmin=np.nanmin(grid), 
            vmax=np.nanmax(grid)),cmap='jet',zorder=10)
        if len(months)==1:
            ax[i].title.set_text(months[0])
        else:
            ax[i].title.set_text(months[0]+' - '+months[-1])

    save_plot(savepath,months,savenote,plot='traj',add=add,monthopt=monthopt,res=res)
    return


def get_trajectory_pc(path='/users/mjr583/scratch/flexpart/',site='cvao',start=2007,end=2021,alt='100m',add='',
                        monthopt=False,dates=False, res='05x05',boxes=1):
    if site=='cvao':
        path+='cvao/'+res+'/airmass_files/'
    else:
        path+=site+'/airmass_files/'

    if boxes==1:
        cols=['Sahara','Sahel','West Africa','Central Africa','Upwelling','Europe',
                'North America','South America','North Atlantic','South Atlantic']
    elif boxes==0:
        path='/users/mjr583/scratch/flexpart/postprocess/boxes/csv_files/boxes_0/'
        cols=['African Sahara','African Coast','European','Atlantic Marine','Atlantic Continental',
                    'Local NE','Local NW','Local SW','Local SE']

    if add != '':
        add='_'+str(add)
    df_list=[]
    years=np.arange(start,end,1)
    for y in years:
        year=str(y)
        x = pd.read_csv(path+year+'_'+res+'_'+alt+add+'.csv',index_col=0)
        df_list.append(x)
    df=pd.concat(df_list)
    
    x=[]
    for i in df.index:
        try:
            x.append(pd.to_datetime(i, format='%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M'))
        except:
            x.append(pd.to_datetime(i, format='%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M'))
    x=np.array(x)
    df.index=pd.to_datetime(x, format='%Y-%m-%d %H:%M')
    df=df[cols]

    if monthopt:
        df=df[str(dates[0]):str(dates[1])]
    return df


def is_square(apositiveint):
    x = apositiveint // 2
    seen = set([x])
    while x * x != apositiveint:
        x = (x + (apositiveint // x)) // 2
        if x in seen: return False
        seen.add(x)
    return True


def plot_layout(n,ax=False):
    factors= set(reduce(list.__add__, 
                        ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))
    if len(factors)<=2:
        n+=1
        factors= set(reduce(list.__add__, 
                        ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))  
    factors=np.array(list(sorted(factors)))
    if is_square(n):
        nrows=factors[int((len(factors)/2.))]
        ncols=factors[int((len(factors)/2.))]
    else:
        nrows=factors[int((len(factors)/2.)-1)]
        ncols=factors[int((len(factors)/2.))]
    return nrows,ncols


def get_figsize(x,y,default=10.):
    if x==y:
        fx=default
        fy=default
    elif x<y:
        pc=x/y
        fx=default/pc
        fy=default
    elif y<x:
        pc=y/x
        fy=default/pc
        fx=default

    return fx,fy


def create_figure(n,plot=False,figsize=False,vertical=False):
    if n==1:
        if not plot or plot=='pie':
            fig, (ax1) = plt.subplots(1,1,figsize=(8,8))
            ax=[ax1]   
        elif plot=='line' or plot=='stacked':
            fig, (ax1) = plt.subplots(1,1,figsize=(10,4))
            ax=[ax1]
    elif n==2:
        if vertical:
            if figsize:
                fig, (ax1,ax2) = plt.subplots(2,1,figsize=figsize)
                ax=[ax1,ax2]
            else:
                fig, (ax1,ax2) = plt.subplots(2,1,figsize=(5,10))
                ax=[ax1,ax2]
        else:
            fig, (ax1,ax2) = plt.subplots(1,2,figsize=(10,5))
            ax=[ax1,ax2]
    elif n==3:
        if figsize:
            if vertical:
                fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=figsize)
            else:
                fig, (ax1,ax2,ax3) = plt.subplots(1,3,figsize=figsize)
        else:
            fig, (ax1,ax2,ax3) = plt.subplots(1,3,figsize=(9,3,))
        ax=[ax1,ax2,ax3]
    else:
        if vertical==True:
            nrows=n
            ncols=1
        else:
            nrows,ncols=plot_layout(n)
        if figsize:
            fx,fy=figsize
        else:
            fx,fy=get_figsize(nrows,ncols)
        fig, axes = plt.subplots(nrows,ncols,figsize=(fx,fy))
        ax=[]
        for a in axes:
            if vertical==True:
                ax.append(a)
            else:
                for b in a:
                    ax.append(b)
        if len(ax) != n:
            plt.delaxes(ax[-1])

    return fig, ax


def make_autopct(values):
    fltr=np.where(values<1.)
    values[fltr]=np.nan
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct


def create_pie(df,savepath='/users/mjr583/scratch/flexpart/postprocess/boxes/plots/',savenote='', 
                    inc_local=True,autopct=False,add='', monthopt=False, dates=False,res='1x1', title=False):
    years=np.arange(df.index[0].year,df.index[-1].year+1,1)
    mean=[]
    for y in years:
        y=str(y)
        mean.append(df[y].mean(axis=0))

    cm=get_my_colors()

    hori=-.3
    if len(years)==1:
        hori=-.1

    f,ax=create_figure(len(years))
    for i in range(len(years)):
        if autopct:
            ax[i].pie(mean[i],startangle=90,autopct='%.1f',pctdistance=1.2, colors=cm)
            ax[i].set_title(str(years[i])+' '+str(add),fontsize=20)
            ax[0].legend(labels=df.columns,ncol=len(df.columns),loc='upper left',bbox_to_anchor=(hori,1.24),prop={'size': 8}, frameon=False)
        else:
            ax[i].pie(mean[i],startangle=90,colors=cm)#,autopct='%.1f',pctdistance=1.2)
            ax[i].set_title(str(years[i])+' '+str(add),fontsize=20)
            labels=['%s, %1.1f%%' % (l, s) for l, s in zip(df.columns, mean[i].values)]
            ax[i].legend(labels=labels,loc='upper left',bbox_to_anchor=(hori,.94),prop={'size': 8}, frameon=False)
    if title:
        plt.title(title)
    save_plot(savepath,years,savenote,plot='pie',add=add,monthopt=monthopt,dates=dates,res=res)
    return


def create_lines(df,savepath='/users/mjr583/scratch/flexpart/postprocess/boxes/plots/',savenote='', freq='Y',
                        autopct=False,add='', title=False,colors=False):
    years=np.arange(df.index[0].year,df.index[-1].year+1,1)
    #df = df.resample(freq).mean()
    f,ax=create_figure(1,plot='line')
    if colors:
        cm=colors
    else:
        cm=get_my_colors()
    for i in range(len(ax)):
        df.plot(color=cm, ax=ax[i])

        box = ax[i].get_position()
        ax[i].set_position([box.x0, box.y0 + box.height * 0.1,box.width, box.height * 0.9])
        ax[i].legend(loc='lower center',labels=df.columns,ncol=int((len(df.columns)+1)/2), 
                frameon=False,bbox_to_anchor=(.5,-.3))
    plt.ylabel('%')
    plt.xlabel('')
    if title:
        plt.title(title)


    save_plot(savepath,years,savenote,plot='line',add=add)
    return


def create_stacked(df,savepath='./plots/',savenote='',inc_local=True,
                    freq='Y',autopct=False,add='',monthopt=False,dates=False,res='1x1',title=False,boxes=1,colors=False):
    years=np.arange(df.index[0].year,df.index[-1].year+1,1)
    f,ax=create_figure(1,plot='stacked')
    for i in range(len(ax)):
        cm=get_my_cmap(boxes=boxes, inc_local=inc_local,colors=colors)

        ncol=int((len(df.columns)+1)/2)     
        vert=-.3

        if inc_local=='False':
            df=df.iloc[:,0:5]
            x=df.sum(axis=1)
            df = df.divide(x,axis=0) * 100
            ncol=5 ; vert=-.25
        
        im=df.plot.area(ax=ax[i],linewidth=0.,colormap=cm)

        ax[i].set_xlim([df.index[0], df.index[-1]])
        ax[i].set_ylim([0,100])
        box = ax[i].get_position()
        ax[i].set_position([box.x0, box.y0 + box.height * 0.1,box.width, box.height * 0.9])
        leg=ax[i].legend(loc='lower center',labels=df.columns,ncol=ncol,frameon=False,bbox_to_anchor=(.5,vert))
        for legobj in leg.legendHandles:
            legobj.set_linewidth(2.0)
    #df=df.resample('M').mean()
    #x_labels=df.index.strftime('%b')
    #im.set_xticklabels(x_labels)
    if title:
        plt.title(title)
    plt.ylabel('%')
    plt.xlabel('')
    save_plot(savepath,years,savenote,plot='stacked', inc_local=inc_local,add=add,monthopt=monthopt,dates=dates,res=res)
    return


def get_my_cmap(boxes=1,inc_local=True, colors=False):
    from matplotlib.colors import LinearSegmentedColormap
    #from palettable.cartocolors.qualitative import Bold_10
    if boxes==0:
        if inc_local=='False':
            colors=['darkred','lime','red','deepskyblue','yellow']
            cmap_name='my_cmap'
            cm=LinearSegmentedColormap.from_list(cmap_name,colors,N=5)
        else:
            colors=['darkred','lime','red','deepskyblue','yellow','#1b9e77','#d95f02','#7570b3','#e7298a']
            cmap_name='my_cmap'
            cm=LinearSegmentedColormap.from_list(cmap_name,colors,N=9)
    elif boxes==1:
        if not colors:
            colors=['#8dd3c7','#ffffb3','#bebada','#fb8072','#bc80bd','#fdb462','#b3de69','#fccde5','#80b1d3','#d9d9d9']#,'#bc80bd']
            cmap_name='my_cmap'
            cm=LinearSegmentedColormap.from_list(cmap_name,colors,N=10)
        else:
            colors=colors
            cmap_name='my_cmap'
            cm=LinearSegmentedColormap.from_list(cmap_name,colors,N=10)
    return cm

def get_my_colors(boxes=1, inc_local=''):
    if boxes==0:
        if inc_local=='False':
            colors=['darkred','lime','red','deepskyblue','yellow']
        else:
            colors=['darkred','lime','red','deepskyblue','yellow','#1b9e77','#d95f02','#7570b3','#e7298a']
    elif boxes==1:
        ######   sahara   sahel   W Africa  N Africa  Upwelli Europe    N Ameri   S Ameri  N Atlan   S Atlant
        colors=['darkred','lime','m','orange','violet','red','yellow','darkgreen','deepskyblue','blue']

    return colors


def save_plot(savepath, years, savenote, plot='',inc_local='',add='',monthopt=False,dates=False,res='1x1'):
    if plot=='traj':
        if len(years)==1:
            time=years[0][:2]+years[0][-4:]
        else:
            time=years[0][:2]+years[0][-4:]+'-'+years[-1][:2]+years[-1][-4:]
        plt.savefig(savepath+plot+'_'+time+'.png')
    else:
        if res != '1x1':
            plot=plot+'_'+res

        if inc_local=='False':
            suff='_NoLocal.png'
        else:
            suff='.png'

        if len(years)==1:
            if monthopt:
                if dates[0][:2]==dates[1][:2]:
                    year_string=dates[0][:2]+str(years[0])
                else:
                    year_string=dates[0][:2]+str(years[0])+'-'+dates[1][:2]+str(years[0])
            else:
                year_string=str(years[0])
        else:
            if monthopt:
                if dates[0][:2]==dates[1][:2]:
                    year_string=dates[0][:2]+str(years[0])
                else:
                    year_string=dates[0][:2]+str(years[0])+'-'+dates[1][:2]+str(years[-1])
            else:
                year_string=str(years[0])+'-'+str(years[-1])

        if add != '':
            year_string=year_string+'_'+str(add)

        if savenote != '':
            plt.savefig(savepath+plot+'_'+year_string+'_'+savenote+suff)
        else:
            plt.savefig(savepath+plot+'_'+year_string+suff)
    return


def get_basemap(proj='cyl', resolution='c', lllon=-180,urlon=180.,lllat=-90,urlat=90,lines=True,freq=30,lsmask=False,ax=False):
    if ax:
        m = Basemap(projection=proj, llcrnrlon=lllon,
                 urcrnrlon=urlon,llcrnrlat=lllat,urcrnrlat=urlat,resolution=resolution,ax=ax)
    else:
        m = Basemap(projection=proj, llcrnrlon=lllon,
                 urcrnrlon=urlon,llcrnrlat=lllat,urcrnrlat=urlat,resolution=resolution)
    m.drawcoastlines()
    m.drawmapboundary()
    if lines:
        m.drawparallels(np.arange(-90.,120.,freq),labels=[1,0,0,0])
        m.drawmeridians(np.arange(-180.,180.,freq),labels=[0,0,0,1])
    if lsmask:
        m.drawmapboundary(fill_color='grey')
        m.fillcontinents(color='lightgrey',zorder=1)
    return m


def gaw_data(species):
    import urllib.request
    import datetime 
    import glob
    file_list=url_file_list('http://thredds.nilu.no/thredds/catalog/ebas/catalog.html')
    if species=='O3':
        url=[s for s in file_list if "ozone" in s][0]
        varname='ozone_nmol_per_mol_amean'
        #gaw_file='/users/mjr583/scratch/flexpart/postprocess/cvao_trends/gaw_data.nc'
        gaw_file='./gaw_data.nc'
        print(url)
        urllib.request.urlretrieve(url,gaw_file)
        fh=Dataset(gaw_file)
        var=fh.variables[varname][:]
        time=fh.variables['time'][:]
    elif species=='CO':
        url=sorted([s for s in file_list if "carbon_monoxide" in s][:])
        varname='carbon_monoxide_amean'
        co=[] ; times=[]
        for n,u in enumerate(url):
            #gaw_file='/users/mjr583/scratch/flexpart/postprocess/cvao_trends/gaw_data_'+str(n)+'.nc'
            gaw_file='./gaw_data_'+str(n)+'.nc'

            urllib.request.urlretrieve(u,gaw_file)
            fh=Dataset(gaw_file)
            var=fh.variables[varname][:]
            time=fh.variables['time'][:]
            co.append(var)
            times.append(time)
        var=np.concatenate(co)
        time=np.concatenate(times)
    os.system('rm gaw_data*.nc')
    new_time=[]
    for t in time:
        x = datetime.datetime(1900,1,1,0,0) + datetime.timedelta(days=t)
        new_time.append(x)
    time=np.array(new_time)
    
    df = pd.DataFrame({'var':var}, index=time)
    X,df,time=CV.remove_nan_rows(df,df.index)

    return df


def url_file_list(url):
    from urllib.request import Request, urlopen, urlretrieve
    from bs4 import BeautifulSoup
    file_list=[]
    url = url.replace(" ","%20")
    req = Request(url)
    a = urlopen(req).read()
    soup = BeautifulSoup(a, 'html.parser')
    x = (soup.find_all('a'))
    for i in x:
        file_name = i.extract().get_text()
        url='https://thredds.nilu.no/thredds/fileServer/ebas/'
        url_new = url + file_name
        #url_new = url_new.replace(" ","%20")
        if(file_name[-1]=='/' and file_name[0]!='.'):
            read_url(url_new)
        if "CVO" in url_new: 
            file_list.append(url_new)
    return file_list


def find_nearest(array,value):
    import numpy as np
    idx=(np.abs(array-value)).argmin()
    return idx


def clear_screen():
    """
    Clear the screen of the terminal for the UI
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    return
