import matplotlib as plt
from timedefs import *
from sched_funcs import *
import os
import sys
# from preferences import *
timeperiod = int(sys.argv[1])
"""
    0   wbreak22_dict
    1   winter23_dict
    2   spring23_dict
    3   summerjune_dict
    4   summerargonne_dict
    5   fall23_dict
    6   wbreak23_dict
    7   aggregrate23_dict
    8   aggregrate23_dict2
    9   winter24_dict
    10  spring24_dict
    11  summer24_dict
    12  fall24_dict
    13  wbreak24_dict
    14  aggregate24_dict
    15  aggregate24_dict2
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

data_list, flat_list = pull_schedule(dates,df,show=False)
continuities, terminators, totals, dws = schedule_analyze(flat_list,defs)
if doGraphs:
    print("OVERTIME PLOTS")
    overtimeplots(flat_list, defs, folder_name,dates)
    print("OVERTIME PLOTS /")
verbose_analyze(flat_list,defs,continuities,terminators,totals,dws,regrouping=True,ultraVerbose=False,graphing=folder_name)
extra_analysis(dates,df,auxiliary_dict,folder_name)
# not sleeping
flat_list2 = []
for chunk in flat_list:
    if chunk == 's':
        flat_list2.append(chunk)
    else:
        flat_list2.append('p')
continuities2, terminators2, totals2, dws2 = schedule_analyze(flat_list2,defs)
verbose_analyze(flat_list2,defs,continuities2,terminators2,totals2,dws2, regrouping=True, ultraVerbose=False,graphing=folder_name)
