import pandas as pd
import numpy as np
from timedefs import *
from collections import Counter

df = pd.read_csv('Timespent.csv')
timeperiod = 4
timeframes = [wbreak22_dict,winter23_dict,spring23_dict,summerjune_dict,summerargonne_dict]
defs = timeframes[timeperiod]['defs']
dates = timeframes[timeperiod]['dates']
d1 = datetime.strptime(dates[0],'%Y-%m-%d')
d2 = datetime.strptime(dates[1],'%Y-%m-%d')
print("Time Period:",timeframes[timeperiod]['name'])
totalDays = (d2-d1).days+1
print("Timespan:",totalDays,'days')
d11 = start_row+(d1-start_date).days
d22 = d11 + (d2-d1).days+1
print("From",d1,"to",d2)
data_range = df.iloc[d11:d22,start_col-1:end_col]
data_list = data_range.values.tolist()
flist = [item for sublist in data_list for item in sublist]

for i,row in enumerate(data_list):
    print(d1+timedelta(days=i),row)



continuities = defs.copy()
terminators = defs.copy()
totals = defs.copy()
dws = defs.copy()
for key in continuities:
    continuities[key] = []
    terminators[key] = []
    totals[key] = 0
    dws[key] = []
curr = None
currLen = 0
dw = False
dwLen = 0
for i,fifteen in enumerate(flist):
    fif = fifteen.strip("d")
    totals[fif] = totals[fif] + .25
    if curr == None: # assumes not starting in DW
        curr = fifteen
        currLen = .25
    else:
        currkey = curr.strip("d")
        isdw = "d" in fifteen
        if fif == currkey:
            currLen += .25
            if isdw:
                dwLen += .25
            else:
                if dwLen > 0:
                    dws[currkey].append(dwLen)
                    dwLen = 0
        else:
            terminators[currkey].append(fif)
            continuities[currkey].append(currLen)
            if dwLen > 0:
                dws[currkey].append(dwLen)
            currLen = .25
            dwLen = int(isdw)
            curr = fifteen
        if i == len(flist)-1:
            terminators[currkey].append(fif)
            continuities[currkey].append(currLen)
            if dwLen > 0:
                dws[currkey].append(dwLen)

tsum = 0
for key in continuities:
    print("")
    print("Code",key,defs[key])
    print("Average Session:",np.round(np.mean(continuities[key]),3),"Std. Dev of session:",np.round(np.std(continuities[key]),3))
    print("Total Hours",totals[key],"Weekly Hours",np.round(totals[key]/totalDays*7,2))
    tsum += totals[key]
    print("Deep Work Sessions:",dws[key])
    print("Average, Std. Dev Deep Work Session:",np.round(np.mean(dws[key]),3),np.round(np.std(dws[key]),3))
    print("Most commonly followed by:",Counter(terminators[key]).most_common(3))
# print("Checksum:",tsum)



# TODO next typical task
# TODO average length of each task

