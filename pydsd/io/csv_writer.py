"""
csv_writer.py
=============

This script writes a CSV file containing
the time series of a variable for one day.

"""

from __future__ import print_function
import glob
import csv
import pathlib
import numpy as np


np.set_printoptions(threshold=np.inf)


def get_fieldname_pyrad(datatype):
    """
    maps the PyDSD data type name into the corresponding Pyrad
    field name

    Parameters
    ----------
    datatype : str
        PyDSD data type name

    Returns
    -------
    field_name : str
        Pyrad field name

    """
    if datatype == 'Nd':
        field_name = 'Nd'
    elif datatype == 'RR':
        field_name = 'RR'
    elif datatype == 'W':
        field_name = 'LWC'
    elif datatype == 'Zh':
        field_name = 'dBZ'
    elif datatype == 'Zv':
        field_name = 'dBZv'
    elif datatype == 'Zdr':
        field_name = 'ZDR'
    elif datatype == 'cross_correlation_ratio_hv':
        field_name = 'RhoHV'
    elif datatype == 'specific_differential_phase_hv':
        field_name = 'DeltaCo'
    elif datatype == 'Ai':
        field_name = 'Ah'
    elif datatype == 'Av':
        field_name = 'Av'
    elif datatype == 'Adr':
        field_name = 'Adp'
    elif datatype == 'Kdp':
        field_name = 'KDP'
    elif datatype == 'LDR':
        field_name = 'LDR'
    else:
        raise ValueError('ERROR: Unknown data type '+datatype)

    return field_name


def write_csv_file(dsd, date, var, fillvalue=float(-9999)):
    """
    writes time series of data

    Parameters
    ----------
    dsd : object
        dsd object containing the time series data

    date : str
        string of the date of the dsd object

    """
    fname = (date+'_'+dsd.info['StationName']+'_' +
             str(dsd.scattering_freq*10**-9)[0:3]+'GHz_' +
             get_fieldname_pyrad(var)+'_el90.0.csv')
    basepath = '/data/disdrometer/mals_parsivel/amfortas/scattering/'
    datapath = date[0:4]+'/'+date[0:6]+'/'
    pathlib.Path(basepath+datapath).mkdir(parents=True, exist_ok=True)
    filelist = glob.glob(fname)
    np.ma.set_fill_value(dsd.fields[var]['data'], fillvalue)
    data = dsd.fields[var]['data'].filled()
    if not filelist:
        with open(basepath+datapath+fname, 'w', newline='') as csvfile:
            csvfile.write('# Disdrometer timeseries data file\n')
            csvfile.write('# Comment lines are preceded by "#"\n')
            csvfile.write('# Description: \n')
            csvfile.write('# Time series of '+get_fieldname_pyrad(var)+'\n')
            csvfile.write(
                '# Location [lat  lon]: ' +
                dsd.info['Latitude_value'] + '  ' +
                dsd.info['Longitude_value'] + '\n')
            csvfile.write(
                '# Elevation: ' +
                str(dsd.info['Altitude_value'])+'m MSL\n')
            csvfile.write(
                '# Elevation angle: ' +
                '90\n')
            csvfile.write(
                '# Scattering Frequency: ' +
                str(dsd.scattering_freq*10**-9)[0:3]+' GHz\n')
            csvfile.write('# Data: ' + get_fieldname_pyrad(var) + '\n')
            csvfile.write(
                '# Start: ' +
                dsd.time['data'].filled()[0].strftime(
                    '%Y-%m-%d %H:%M:%S UTC') + '\n')
            csvfile.write('#\n')

            fieldnames = ['date', 'Precip Code', get_fieldname_pyrad(var),
                          'Scattering Temp [deg C]']
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            for i in range(len(dsd.time['data'])):
                writer.writerow(
                    {'date': dsd.time['data'][i],
                     'Precip Code': dsd.fields['Precip_Code']['data'][i],
                     get_fieldname_pyrad(var): data[i],
                     'Scattering Temp [deg C]': dsd.scattering_temp})
            csvfile.close()
    else:
        with open(basepath+datapath+fname, 'a', newline='') as csvfile:
            fieldnames = ['date', 'Precip Code', get_fieldname_pyrad(var),
                          'Scattering Temp [deg C]']
            writer = csv.DictWriter(csvfile, fieldnames)
            for i in range(len(dsd.time['data'])):
                writer.writerow(
                    {'date': dsd.time['data'][i],
                     'Precip Code': dsd.fields['Precip_Code']['data'][i],
                     get_fieldname_pyrad(var): data[i],
                     'Scattering Temp [deg C]': dsd.scattering_temp})
            csvfile.close()
