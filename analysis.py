from timedefs import *
from sched_funcs import *

timeperiod = 5
#timeframes = [wbreak22_dict,winter23_dict,spring23_dict,summerjune_dict,summerargonne_dict,week1_dict,week2_dict]
defs = timeframes[timeperiod]['defs']
dates = timeframes[timeperiod]['dates']
print("Time Period:",timeframes[timeperiod]['name'])

data_list,flist = pull_schedule(dates,df,show=True)
continuities, terminators, totals, dws = schedule_analyze(flist,defs)
verbose_analyze(flist,defs,continuities,terminators,totals,dws)
