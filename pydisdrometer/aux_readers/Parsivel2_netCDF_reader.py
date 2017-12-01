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

        time = ma.array(self.nc_dataset.variables['Time'][:])
        self.time = self._get_epoch_time(time)

        Nd = np.power(10,ma.transpose(ma.array(
                self.nc_dataset.variables['VolumetricDrops'][:])))
        velocity = ma.array(
             [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.1, 1.3, 1.5, 1.7, 1.9,
             2.2, 2.6, 3.0, 3.4, 3.8, 4.4, 5.2, 6.0, 6.8, 7.6, 8.8, 10.4, 12.0, 13.6, 15.2,
             17.6, 20.8])
        rain_rate = ma.array(
                self.nc_dataset.variables['ParsivelIntensity'][:])
        self.diameter = ma.array(
			[0.062, 0.187, 0.312, 0.437, 0.562, 0.687, 0.812, 0.937, 1.062, 1.187, 
			1.375, 1.625, 1.875, 2.125, 2.375, 2.75, 3.25, 3.75, 4.25, 4.75, 
			5.5, 6.5, 7.5, 8.5, 9.5, 11., 13., 15., 17., 19., 21.5, 24.5])
        self.spread = ma.array(
			[0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.250,
			0.250, 0.250, 0.250, 0.250, 0.500, 0.500, 0.500, 0.500, 0.500, 1.000, 1.000,
			1.000, 1.000, 1.000, 2.000, 2.000, 2.000, 2.000, 2.000, 3.000, 3.000])

        # TODO: Move this to new metadata utility, and just add information from raw netcdf where appropriate
        self.bin_edges = common.var_to_dict(
                'bin_edges',
                np.hstack((0, self.diameter + np.array(self.spread) / 2)),
                'mm', 'Boundaries of bin sizes')
        self.spread = common.var_to_dict(
                'spread', self.spread,
                'mm', 'Bin size spread of bins')
        self.diameter = common.var_to_dict(
                'diameter', self.diameter,
                'mm', 'Particle diameter of bins')

        self.fields['Nd'] = common.var_to_dict(
                'Nd', np.ma.masked_where(Nd<1,Nd), 'm^-3 mm^-1',
                'Liquid water particle concentration')
        self.fields['velocity'] = common.var_to_dict(
                'velocity', velocity, 'm s^-1',
                'Terminal fall velocity for each bin')
        self.fields['rain_rate'] = common.var_to_dict(
                'rain_rate', rain_rate, 'mm h^-1',
                'Rain rate')

        # self.fields['num_drop'] = common.var_to_dict(
               # "num_drop", self.nc_dataset.variables['num_drop'][:], '#',
               # "Number of Drops")

        # self.fields['d_max'] = common.var_to_dict(
           # "d_max", self.nc_dataset.variables['d_max'][:],"mm",
           # "Diameter of largest drop"
        # )
        # self.fields['liq_water'] = common.var_to_dict(
            # "liq_water", self.nc_dataset.variables['liq_water'][:],
            # "gm/m^3", "Liquid water content")

        # self.fields['n_0'] = common.var_to_dict(
            # "n_0", self.nc_dataset.variables['n_0'][:],
            # "1/(m^3-mm)", "Distribution Intercept")
        # self.fields['lambda'] = common.var_to_dict(
            # "lambda", self.nc_dataset.variables['lambda'][:],
            # "1/mm", "Distribution Slope")

        for key in self.nc_dataset.ncattrs():
            self.info[key] =self.nc_dataset.getncattr(key)

    def _get_epoch_time(self, sample_times):
        """Convert time to epoch time and return a dictionary."""
        eptime = {'data': sample_times, 'units': common.EPOCH_UNITS,
                  'standard_name': 'Time', 'long_name': 'Time (UTC)'}
        return eptime
