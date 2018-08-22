#!/usr/bin/env python
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import numpy as np
import pydsd as pyd
#np.set_printoptions(threshold=1000)

# for basepath 1 in filename, only the given date works
# for testing on other dates, choose basepath 2 in filename
# basepath 2 is the location where the Parsivel2 data are located on
# zueub242.
date = '20180315'
basepath1 = '../testdata/'
basepath2 = '/data/disdrometer/mals_parsivel/amfortas/data_netCDF/'


# Read in the Parsivel File
filename = basepath1+date[:4]+'/'+date+'_amfortas.nc'
dsd = pyd.read_parsivel2_netCDF(filename)
dsd.calculate_radar_parameters()
dsd.calculate_dsd_parameterization()
######################################################################
############################# DSD plot ###############################
start = datetime.strptime(date, '%Y%m%d')
end = datetime.strptime(date+'235959', '%Y%m%d%H%M%S')

plt.figure(1)
fig, ax = plt.subplots(figsize=(15, 6), dpi=80)
ticks = ax.set_yticks(dsd.bin_edges['data'], minor=False)
nd = pyd.plot.plot_dsd(dsd, tighten=False, vmin=1, ylims=(0, 5.5),
                       xlims=(start, end), date_format='%H:%M:%S',
                       x_min_tick_format='hour')
ttl = plt.title('24h DSD-timeseries '+date[:4]+'-'+date[4:6]+
                '-'+date[6:8], fontsize=14, fontweight='bold')
ax.yaxis.grid(True, which='major')
ttl.set_position([.5, 1.05])

######################################################################
######################## General timeseries ##########################

plt.figure(2)
fig, ax = plt.subplots(figsize=(10, 4), dpi=80)
ts1 = pyd.plot.plot_ts(dsd, 'Zdr', date_format='%H:%M:%S',
                       x_min_tick_format='hour',
                       title='24h ZDR timeseries '+date[:4]+'-'+
                       date[4:6]+'-'+date[6:8], fmt="r-")
xlabel = plt.xlabel('Time')
ylabel = plt.ylabel('ZDR [dB]')
ax.yaxis.grid(True, which='major')
ax.set_xlim(start, end)
#ax.set_ylim(0, 1.8)
ttl = ax.title
ttl.set_position([.5, 1.05])

######################################################################
##################### Compare scatterplot ############################

plt.figure(3)
fig, ax = plt.subplots(figsize=(7, 7), dpi=80)
#plt.xscale('log')
pyd.plot.scatter(dsd.fields['Zh']['data'], dsd.fields['Zdr']['data'],
                 col='k', msize=20, edgecolors='none',
                 title='24h Zh-ZDR '+date[:4]+'-'+date[4:6]+'-'+
                 date[6:8], ax=ax, fig=fig)
xlabel = plt.xlabel(r'Zh [dBZ]')
ylabel = plt.ylabel(r'ZDR [dB]')
ax.yaxis.grid(True, which='major')
ax.set_xlim(0, 43)
ax.set_ylim(0, 1.9)
ttl = ax.title
ttl.set_position([.5, 1.05])

######################################################################
#################### Compare DSD with median D #######################

plt.figure(4)
fig, ax = plt.subplots(figsize=(20, 8), dpi=80)
ticks = ax.set_yticks(dsd.bin_edges['data'], minor=False)
pyd.plot.plot_dsd(dsd, tighten=False, vmin=1, ylims=(0, 6),
                  xlims=(start, end))
ttl = plt.title('24h DSD-timeseries '+date[:4]+'-'+date[4:6]+'-'+
                date[6:8], fontsize=14, fontweight='bold')
ax.yaxis.grid(True, which='major')
ttl.set_position([.5, 1.05])
ts1 = pyd.plot.plot_ts(dsd, 'D0', date_format='%H:%M:%S',
                       x_min_tick_format='hour', fmt="black")

######################################################################
######################  RR with Precip code  #########################

tsdata = dsd.fields['RR']['data']
p = np.full(dsd.numt, True, dtype=bool)
l = dsd.fields['Precip_Code']['data']
t = dsd.time['data'].filled()
tt = mdates.date2num(t)
for i in range(dsd.numt):
    if ('G' in l[i]) or ('S' in l[i]):
        p[i] = False

c = ['r' if a else 'b' for a in p]
lines = [((x0, y0), (x1, y1)) for x0, y0, x1, y1
         in zip(tt[:-1], tsdata[:-1], tt[1:], tsdata[1:])]
colored_lines = LineCollection(lines, colors=c, linewidths=(2, ))
# plot data

plt.figure(5)
fig, ax = plt.subplots(figsize=(20, 8), dpi=80)
coll = ax.add_collection(colored_lines)
ax.autoscale_view()
date_format = mdates.DateFormatter('%H:%M:%S')
ax.xaxis.set_major_formatter(date_format)
ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
ylabel = plt.ylabel('RR [mm/h]')
xlabel = plt.xlabel('Time')
ax.yaxis.grid(True, which='major')
#ax.set_ylim(0, 3)
ax.set_xlim(tt[0], tt[-1])
ttl = plt.title('24h RR timeseries '+date[:4]+'-'+date[4:6]+'-'+
                date[7:8], fontsize=14, fontweight='bold')
ttl.set_position([.5, 1.05])
red_patch = mpatches.Patch(color='red', label='all liquid')
blue_patch = mpatches.Patch(color='blue', label='solid phase present')
plt.legend(handles=[red_patch, blue_patch])
plt.show()

######################################################################
#####################    Write csv-files    ##########################

pyd.io.csv_writer.write_csv_file(dsd, date, 'Zh', '../testdata/')
