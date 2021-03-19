import numpy as np
import glob
from netCDF4 import Dataset

def get_tropopause_ps(filepath):
    fh=Dataset(filepath)
    
    Tlev=fh.variables['Met_TropLev'][:]
    ad=fh.variables['Met_AD'][:]
    return Tlev, ad

zboltz=1.3807e-23       #Boltzmann constantn
Rd=287.05               #gas constant
avc=6.022e23            #Avogadro's constant
mm_da=avc*zboltz/Rd     #molar mass of dry air (approx 28 g/mol)


##---------------------MAIN SCRIPT---------------------------------------------##

## Delete these 2 lines of mine and instead get your Geos-Chem species variable - you can copy from one of your other scripts
## This needs to be 3D (lev, lat, lon) so either choose a time or average over time. 
## Also the variable needs to be in mol mol-1, NOT ppb/ppt.

variable, lat,lon,lev,time = GC.get_gc_var(rundir='tropchem_merra_4x5', variable='O3', version='12.9.3',year='2016') #replace
variable= variable[0] * 1e-9 #replace


# This function gets the GC tropospause level (Tlev) and air mass per grid box (AD).
# I'll send you the necessary file but you'll need to change the path passed to the function.
Tlev, AD = get_tropopause_ps(filepath='/users/mjr583/scratch/GC/12.9.3/rundirs/tropchem_merra_4x5/OutputDir/GEOSChem.StateMet.20150101_0000z.nc4')
Tlev = Tlev[0]  
AD= AD[0]  # These lines just take the first timestep for these too

# This loops over lons, lat and levels, determining whether each gridbox is within the troposphere
# (using the tropopause level calculated by Geos-Chem (Tlev)
# If not in the tropopause, the value is changed to NaN
for ilon in range(len(lon)):
    for ilat in range(len(lat)):
        for ilev in range(1,48):            
            if (ilev > Tlev[ilat,ilon]):
                variable[ilev-1,ilat,ilon] = np.nan

# Here you need to change the molecular mass for whichever species you are looking at (in kg/mol)
mm=0.0479982 

# Then, looping over each level you sum the variable conc multiplied by the mass of air and the 
# fraction which is that species. Then convert to Tg (e-9)
var=np.zeros(47) * np.nan
for i in range(47):
    var[i] = np.nansum( variable[i,:,:] * AD[i,:,:] * mm/mm_da) * 1e-9

## Sum the result, round to 2 decimal places and then print the result. 
burd = np.round(np.nansum(var),2)
print('Tropospheric Ozone burden is %s Tg' %burd )
