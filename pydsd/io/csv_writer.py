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
    elif datatype == 'Zh':
        field_name = 'dBZ'
    elif datatype == 'Zv':
        field_name = 'dBZv'
    elif datatype == 'Zdr':
        field_name = 'ZDR'
    elif datatype == 'cross_correlation_ratio_hv':
        field_name = 'RhoHV'
    elif datatype == 'Ai':
        field_name = 'Ah'
    elif datatype == 'Adr':
        field_name = 'Adp'
    elif datatype == 'Kdp':
        field_name = 'KDP'
    else:
        raise ValueError('ERROR: Unknown data type '+datatype)

    return field_name


def write_csv_file(dsd, date, var):
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
             str(dsd.scattering_freq*10**-9)[0:3]+'_' +
             get_fieldname_pyrad(var)+'_el090.0.csv')
    basepath = '/data/disdrometer/mals_parsivel/amfortas/scattering/'
    datapath = date[0:4]+'/'+date[0:6]+'/'
    pathlib.Path(basepath+datapath).mkdir(parents=True, exist_ok=True)
    dsd.calculate_radar_parameters()
    filelist = glob.glob(fname)
    if not filelist:
        with open(basepath+datapath+fname, 'w', newline='') as csvfile:
            csvfile.write('# Disdrometer timeseries data file\n')
            csvfile.write('# Comment lines are preceded by "#"\n')
            csvfile.write('# Description: \n')
            csvfile.write('# Time series of '+get_fieldname_pyrad(var)+'\n')
            csvfile.write(
                '# Location [lon, lat, alt]: ' +
                dsd.info['Longitude_value'] + '  ' +
                dsd.info['Latitude_value'] + '  ' +
                dsd.info['Altitude_value'] + '\n')
            csvfile.write(
                '# Elevation: ' +
                str(dsd.info['Altitude_value'])+'m\n')
            csvfile.write(
                '# Scattering Frequency: ' +
                str(dsd.scattering_freq*10**-9)[0:3]+'MHz\n')
            csvfile.write('# Data: ' + get_fieldname_pyrad(var) + '\n')
            # csvfile.write('# Fill Value: ' +
            #              str(dsd.fields[var]['_FillValue']) + '\n')
            csvfile.write(
                '# Start: ' +
                dsd.time['data'].filled()[0].strftime(
                    '%Y-%m-%d %H:%M:%S UTC') + '\n')
            csvfile.write('#\n')

            fieldnames = ['date', 'Precip_Code', get_fieldname_pyrad(var),
                          'Scattering_Temp. [°C]']
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            for i in range(len(dsd.time['data'])):
                writer.writerow(
                    {'date': dsd.time['data'][i],
                     'Precip_Code': dsd.fields['Precip_Code']['data'][i],
                     get_fieldname_pyrad(var): dsd.fields[var]['data'][i],
                     'Scattering_Temp. [°C]': dsd.scattering_temp})
            csvfile.close()
    else:
        with open(basepath+datapath+fname, 'a', newline='') as csvfile:
            fieldnames = ['date', 'Precip_Code', get_fieldname_pyrad(var),
                          'Scattering_Temp. [°C]']
            writer = csv.DictWriter(csvfile, fieldnames)
            for i in range(len(dsd.time['data'])):
                writer.writerow(
                    {'date': dsd.time['data'][i],
                     'Precip_Code': dsd.fields['Precip_Code']['data'][i],
                     get_fieldname_pyrad(var): dsd.fields[var]['data'][i],
                     'Scattering_Temp. [°C]': dsd.scattering_temp})
            csvfile.close()
