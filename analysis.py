import matplotlib as plt
from timedefs import *
from sched_funcs import *
import os
from preferences import *
timeperiod = 5
"""
    0   wbreak22_dict
    1   winter23_dict
    2   spring23_dict
    3   summerjune_dict
    4   summerargonne_dict
    5   fall23_dict
    6   wbreak23_dict
    7   aggregrate_dict
    8   aggregrate_dict2

"""
defs = timeframes[timeperiod]['defs']
dates = timeframes[timeperiod]['dates']
print("Time Period:",timeframes[timeperiod]['name'])
d1 = datetime.strptime(dates[0], '%Y-%m-%d')
d2 = datetime.strptime(dates[1], '%Y-%m-%d')
totalDays = (d2 - d1).days + 1
print("Timespan:", totalDays, 'days')
print("From", d1, "to", d2)

doGraphs = True
folder_name = timeframes[timeperiod]['name']
if doGraphs:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

data_list,flist = pull_schedule(dates,df,show=False)
continuities, terminators, totals, dws = schedule_analyze(flist,defs)
if doGraphs:
    overtimeplots(flist,defs,folder_name,dates)
verbose_analyze(flist,defs,continuities,terminators,totals,dws,regrouping=True,ultraVerbose=False,graphing=folder_name)

