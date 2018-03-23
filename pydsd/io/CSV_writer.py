from __future__ import print_function
import numpy as np
import numpy as np
import glob
import csv
import os

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

    if datatype == 'Zh':
        field_name = 'dBZ'
    elif datatype == 'Zv':
        field_name = 'dBZv'
    elif datatype == 'Zdr':
        field_name = 'ZDR'
    elif datatype == 'cross_correlation_ratio_hv':
        field_name = 'RhoHV'
    elif datatype == 'PhiDP':
        field_name = 'differential_phase'
    else:
        raise ValueError('ERROR: Unknown data type '+datatype)

    return field_name


def write_csv_file(dsd, fname, var):
    """
    writes time series of data

    Parameters
    ----------
    dataset : dict
        dictionary containing the time series parameters

    fname : str
        file name where to store the data

    Returns
    -------
    fname : str
        the name of the file where data has written

    """

    filelist = glob.glob(fname)
    if len(filelist) == 0:
        with open(fname, 'w', newline='') as csvfile:
            csvfile.write('# Disdrometer timeseries data file\n')
            csvfile.write('# Comment lines are preceded by "#"\n')
            csvfile.write('# Description: \n')
            csvfile.write('# Time series of ' + var + '\n')
            csvfile.write(
                '# Location [lon, lat, alt]: ' +
                dsd.info['Longitude_value'] + '  ' +
                dsd.info['Latitude_value'] + '  ' +
                dsd.info['Altitude_value'] + '\n')
            csvfile.write('# Data: ' + get_fieldname_pyrad(var) + '\n')
            csvfile.write('# Fill Value: ' +
                          str(dsd.fields[var]['_FillValue']) + '\n')
            csvfile.write(
                '# Start: ' +
                dsd.time['data'].filled()[0].strftime(
                    '%Y-%m-%d %H:%M:%S UTC') + '\n')
            csvfile.write('#\n')

            fieldnames = ['date', 'Precip_Code', get_fieldname_pyrad(var)]
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            for i in range(len(dsd.time['data'])):
                writer.writerow(
                    {'date': dsd.time['data'][i],
                     'Precip_Code': dsd.fields['Precip_Code']['data'][i],
                     get_fieldname_pyrad(var): dsd.fields[var]['data'][i]})
            csvfile.close()
    else:
        with open(fname, 'a', newline='') as csvfile:
            fieldnames = ['date', 'Precip_Code', get_fieldname_pyrad(var)]
            writer = csv.DictWriter(csvfile, fieldnames)
            for i in range(len(dsd.time['data'])):
                writer.writerow(
                    {'date': dsd.time['data'][i],
                     'Precip_Code': dsd.fields['Precip_Code']['data'][i],
                     get_fieldname_pyrad(var):
                         [dsd.fields[var]['data'][i, j] for j
                          in range(len(dsd.fields[var]['data'][i]))]})
            csvfile.close()
