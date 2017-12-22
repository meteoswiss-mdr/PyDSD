import numpy as np
import numpy.ma as ma
import itertools
import scipy.optimize
from pytmatrix.psd import GammaPSD
import csv
import datetime
from netCDF4 import Dataset

from ..DropSizeDistribution import DropSizeDistribution
from ..io import common
import os


def read_parsivel2_netCDF(filename):
    '''
    Takes a filename pointing to an OTT Parsivel2 netcdf file and returns
    a drop size distribution object.

    Usage:
    dsd = read_parsivel2_netCDF(filename)

    Returns:
    DropSizeDistrometer object

    '''

    reader = Parsivel2_netCDF(filename)

    if reader:
        return DropSizeDistribution(reader)
    else:
        return None

    del (reader)


class Parsivel2_netCDF(object):
    '''
    This class reads and parses parsivel2 disdrometer data from ARM netcdf
    files. These conform to document (Need Document).

    Use the read_parsivel2_netCDF() function to interface with this.
    '''

    def __init__(self, filename):
        '''
        Handles setting up a reader.
        '''
        self.fields = {}
        self.info = {}

        self.nc_dataset = Dataset(filename)
        self.filename = filename

        self.time = common.ncvar_to_dict(self.nc_dataset.variables['Time'])
        self.time['data'] = ma.array(self.get_datetime_from_epoch(self.time['data'][:]))
        self.time['units'] = "Datetime objects"
        del self.time['_FillValue']

        self.fields['Nd'] = common.ncvar_to_dict(self.nc_dataset.variables['VolumetricDrops'])
        self.fields['Nd']['data'] = ma.transpose(np.power(10,self.fields['Nd']['data']))
        del self.fields['Nd']['_FillValue']
        self.fields['Nd']['units'] = "1/m^3 1/mm"
        ma.set_fill_value(self.fields['Nd']['data'],np.power(10,self.fields['Nd']['data'].fill_value))

        self.fields['rain_rate']  = common.ncvar_to_dict(self.nc_dataset.variables['ParsivelIntensity'])
        self.fields['rain_rate']['data'] = ma.masked_array(self.fields['rain_rate']['data'])
        ma.set_fill_value(self.fields['rain_rate']['data'],self.fields['rain_rate']['_FillValue'])
        del self.fields['rain_rate']['_FillValue']

        self.fields['reflectivity']  = common.ncvar_to_dict(self.nc_dataset.variables['Reflectivity'])
        del self.fields['reflectivity']['_FillValue']

        self.fields['num_particles']  = common.ncvar_to_dict(self.nc_dataset.variables['RawDrops'])
        self.fields['num_particles']['data'] = ma.masked_array(self.fields['num_particles']['data'])
        ma.set_fill_value(self.fields['num_particles']['data'],self.fields['num_particles']['_FillValue'])
        del self.fields['num_particles']['_FillValue']
        
        diameter = ma.array([  0.0625 ,   0.1875 ,   0.3125 ,   0.4375 ,   0.5625 ,   0.6875 ,   0.8125 ,   0.9375 ,   1.0625 ,
                               1.1875 ,   1.375  ,   1.625  ,   1.875  ,   2.125  ,   2.375  ,   2.75   ,   3.25   ,   3.75   ,
                               4.25   ,   4.75   ,   5.5    ,   6.5    ,   7.5    ,   8.5    ,    9.5   ,  11.     ,  13.     ,
                              15.     ,  17.     ,  19.     ,   21.5   ,  24.5    ])

        spread = ma.array([ 0.125 ,  0.125 ,  0.125 ,  0.125 ,  0.125 ,  0.125 ,  0.125 ,  0.125 ,  0.125 ,  0.125 ,  0.250 ,
                            0.250 ,  0.250 ,  0.250 ,  0.250 ,  0.500 ,  0.500 ,  0.500 ,  0.500 ,  0.500 ,  1.000 ,  1.000 ,
                            1.000 ,  1.000 ,  1.000 ,  2.000 ,  2.000 ,  2.000 ,  2.000 ,  2.000 ,  3.000 ,  3.000 ])
        
        velocity = ma.array([ 0.05,  0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.1, 1.3 , 1.5 , 1.7 , 1.9 ,
             		      2.2 ,  2.6 , 3.0 , 3.4 , 3.8 , 4.4 , 5.2 , 6.0 , 6.8 , 7.6 , 8.8, 10.4, 12.0, 13.6, 15.2,
             		     17.6 , 20.8])

        self.bin_edges = common.var_to_dict(
                'bin_edges',
                np.hstack((0, diameter + np.array(spread) / 2)),
                'mm', 'Boundaries of bin sizes')
        self.spread = common.var_to_dict(
                'spread', spread,
                'mm', 'Bin size spread of bins')
        self.diameter = common.var_to_dict(
                'diameter', diameter,
                'mm', 'Particle diameter of bins')
        self.fields['terminal_velocity'] = common.var_to_dict(
                'velocity', velocity, 'm s^-1',
                'Terminal fall velocity for each bin')
        
        for key in self.nc_dataset.ncattrs():
            self.info[key] =self.nc_dataset.getncattr(key)

    def get_datetime_from_epoch(self, sample_times):
        """Convert time from epoch time to datetime and return a dictionary."""
        base = datetime.datetime.fromtimestamp(sample_times[0])
        arr = np.array([base + datetime.timedelta(seconds=30*i) for i in range(2880)])
        return arr
