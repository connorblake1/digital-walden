from collections import Counter
from timedefs import *
import numpy as np
import matplotlib.pyplot as plt
from statistics import mode
import os

def schedule_analyze(flat_list,def_dict):
    continuities = def_dict.copy()
    terminators = def_dict.copy()
    sum_totals = def_dict.copy()
    dw_sessions = def_dict.copy()
    for key in continuities:
        continuities[key] = []
        terminators[key] = []
        sum_totals[key] = 0
        dw_sessions[key] = []
    current_key = None
    session_length = 0
    dw_len = 0
    for i, full_key in enumerate(flat_list):
        base_key = full_key.strip("d")
        sum_totals[base_key] = sum_totals[base_key] + .25
        if current_key == None:  # assumes not starting in DW
            current_key = full_key
            session_length = .25
        else:
            current_key = current_key.strip("d")
            isdw = "d" in full_key
            if base_key == current_key:
                session_length += .25
                if isdw:
                    dw_len += .25
                else:
                    if dw_len > 0:
                        dw_sessions[current_key].append(dw_len)
                    dw_len = 0
            else:
                terminators[current_key].append(base_key)
                continuities[current_key].append(session_length)
                if dw_len > 0:
                    dw_sessions[current_key].append(dw_len)
                session_length = .25
                dw_len = int(isdw) * .25
                current_key = full_key
            if i == len(flat_list) - 1:
                terminators[current_key].append(base_key)
                continuities[current_key].append(session_length)
                if dw_len > 0:
                    dw_sessions[current_key].append(dw_len)
    return continuities, terminators, sum_totals, dw_sessions


def deepwork_analyze(flat_list, def_dict, folder_name):
    days = int(len(flat_list)/96)
    time_start_buckets = [ [] for i in range(96)]
    long_time_start_buckets = [ [] for i in range(96)]
    indw_bucket = [0]*96
    long_indw_bucket = [0]*96
    long_cutoff = 12
    for i, full_key in enumerate(flat_list):
        if i == 0:
            continue
        if "d" in full_key:
            indw_bucket[i%96] += 1
        if "d" in full_key and flat_list[i-1] != full_key:
            
            j = i+1
            while flat_list[j] == full_key:
                j+= 1
            time_start_buckets[i%96].append((j-i)*.25)
            if j-i >= long_cutoff:
                long_time_start_buckets[i%96].append((j-i)*.25)
                for k in range(i,j):
                    long_indw_bucket[k%96] += 1

    indw_bucket = np.array(indw_bucket)/days
    long_indw_bucket = np.array(long_indw_bucket)/days
    

    hour_ticks = np.arange(0, 96, 4)
    hour_labels = [f"{h}:00" for h in range(24)]

    
    # plot by hour of day
    fig, ax = plt.subplots()
    ax.bar(range(96), indw_bucket, width=1)
    ax.set_xticks(hour_ticks)
    ax.set_xticklabels(hour_labels, rotation=90)
    ax.set_xlabel("Time of Day")
    ax.set_title("Proportion of Days in Deep Work by Time of Day")
    plt.tight_layout()
    plt.savefig(os.path.join(folder_name,"dw_tod_histogram.png"), dpi=300)
    plt.clf()
    plt.cla()
    # long by hour
    fig, ax = plt.subplots()
    ax.bar(range(96), long_indw_bucket, width=1)
    ax.set_xticks(hour_ticks)
    ax.set_xticklabels(hour_labels, rotation=90)
    ax.set_xlabel("Time of Day")
    ax.set_title("Proportion of Days in Deep Work by Time of Day (Long)")
    plt.tight_layout()
    plt.savefig(os.path.join(folder_name,"dw_ltod_histogram.png"), dpi=300)
    plt.clf()
    plt.cla()

    # total hours started at a certain time
    dw_start_times = [sum(arr) for arr in time_start_buckets]
    fig, ax = plt.subplots()
    ax.bar(range(96), dw_start_times, width=1)
    ax.set_xticks(hour_ticks)
    ax.set_xticklabels(hour_labels, rotation=90)
    ax.set_xlabel("Time of Day")
    ax.set_ylabel("Hours")

    ax.set_title("Deep Work Hours by Time of Day When Started")
    plt.tight_layout()
    plt.savefig(os.path.join(folder_name,"dw_start_histogram.png"), dpi=300)
    plt.clf()
    plt.cla()
    # long starts
    long_dw_start_times = [sum(arr) for arr in long_time_start_buckets]
    fig, ax = plt.subplots()
    ax.bar(range(96), long_dw_start_times, width=1)
    ax.set_xticks(hour_ticks)
    ax.set_xticklabels(hour_labels, rotation=90)
    ax.set_xlabel("Time of Day")
    ax.set_ylabel("Hours")
    ax.set_title("Deep Work Hours by Time of Day When Started (Long)")
    plt.tight_layout()
    plt.savefig(os.path.join(folder_name,"dw_longstart_histogram.png"), dpi=300)
    plt.clf()
    plt.cla()


def reassignDW(flat_list):
    # when randomly generating schedules, assign blocks longer than 1.5h to be deep work, does not apply to analysis
    for i,block in enumerate(flat_list):
        flat_list[i] = block.strip("d")
    curr = None
    currLen = 0
    currStart = -1
    for i, fifteen in enumerate(flat_list):
        fifteen = fifteen.strip("d")
        if curr == None:  # assumes not starting in DW
            curr = fifteen
            currLen = .25
            currStart = i
        else:
            curr = curr.strip("d")
            if fifteen == curr:
                currLen += .25
            else:
                if currLen > 1.5 and dw_eligible[curr]:
                    flat_list[currStart:currStart+int(currLen/.25)] = [curr + "d"]*int(currLen/.25)
                currLen = .25
                currStart = i
                curr = fifteen
            if i == len(flat_list) - 1:
                pass
    return flat_list
def verbose_analyze(flat_list, def_dict,conts,terms,tots,dwss,regrouping=False,ultraVerbose=False,graphing=False):
    totalDays = int(len(flat_list)/96)
    print("")
    tsum = 0
    dw_tot = 0
    # regrouping (ie if 1 and 2 are mapped to "Class", they get analyzed together)
    if regrouping:
        r_conts = dict()
        r_terms = dict()
        r_tots = dict()
        r_dwss = dict()
        for key in def_dict:
            rkey = def_dict[key]
            h = r_conts.get(rkey,[])
            h.extend(conts[key])
            r_conts[rkey] = h
            h = r_terms.get(rkey,[])
            t2 = []
            for terminator in terms[key]:
                t2.append(def_dict[terminator])
            h.extend(t2)
            r_terms[rkey] = h
            r_tots[rkey] = r_tots.get(rkey,0)+tots[key]
            h = r_dwss.get(rkey,[])
            h.extend(dwss[key])
            r_dwss[rkey] = h
        conts = r_conts
        terms = r_terms
        tots = r_tots
        dwss = r_dwss
        for nkey in conts:
            if len(conts[nkey]) != 0:
                print("")
                print(nkey)
                if ultraVerbose:
                    print(conts[nkey])
                if graphing is not None:
                    activity = nkey.replace(" ", "")
                    file_name = activity+"_SessionHistogram.png"
                    full_path = os.path.join(graphing, file_name)
                    plt.clf()
                    msesh = max(conts[nkey])
                    plt.hist(conts[nkey], bins=[i * 0.5 for i in range(int(msesh * 2) + 2)], edgecolor='black')
                    plt.xlabel('Session Length (h)', labelpad=-2)
                    plt.ylabel('Frequency')
                    plt.xticks([i * 0.5 for i in range(int(msesh * 2) + 2)], rotation=60)
                    plt.title("Sessions Lengths of " + nkey)
                    plt.savefig(full_path, dpi=300)

                print("Average Per Day (h):",np.round(np.sum(conts[nkey])/totalDays,3))
                print("Average Session (h):", np.round(np.mean(conts[nkey]), 3))
                print("Std. Dev of session:",np.round(np.std(conts[nkey]), 3))
                print("Total (h)", tots[nkey], "Weekly Hours", np.round(tots[nkey] / totalDays * 7, 2))
                print("Most commonly followed by:", Counter(terms[nkey]).most_common(3))
                tsum += tots[nkey]
                if len(dwss[nkey]) > 0:
                    if graphing is not None:
                        activity = nkey.replace(" ","")
                        file_name = activity+"_DW_SessionHistogram.png"
                        full_path = os.path.join(graphing,file_name)
                        plt.clf()
                        msesh = max(dwss[nkey])
                        plt.hist(dwss[nkey],bins=[i *.5 for i in range(int(msesh*2)+2)])
                        plt.xlabel("Deep Work Session Length (h)",labelpad=-2)
                        plt.ylabel("Frequency")
                        plt.xticks([i * 0.5 for i in range(int(msesh * 2) + 2)], rotation=60)
                        plt.title("Deep Work Sessions Lengths of " + nkey)
                        plt.savefig(full_path, dpi=300)

                    # TODO
                    # count = 0
                    # for item in flat_list:
                    #     if key + "d" in item:
                    #         count += 1
                    # print(.25 * count)
                    print("Percent in Deep Work:", np.round(100 * np.sum(dwss[nkey]) / tots[nkey], 1), "%", "\tTotal:",
                          np.round(np.sum(dwss[nkey]), 2))
                    dw_tot += np.sum(dwss[nkey])
                    print("Deep Work Session Average:", np.round(np.mean(dwss[nkey]), 3), "Std. Dev ",
                          np.round(np.std(dwss[nkey]), 3))
    else:
        for key in def_dict:
            if def_dict[key] is not None and len(conts[key]) != 0:
                print("")
                print("Code", key, def_dict[key])
                print(conts[key])
                print("Average Per Day (h):",np.round(np.sum(conts[key])/totalDays,3))
                print("Average Session (h):", np.round(np.mean(conts[key]), 3))
                print("Std. Dev of session:",np.round(np.std(conts[key]), 3))
                print("Total (h)", tots[key], "Weekly Hours", np.round(tots[key] / totalDays * 7, 2))
                print("Most commonly followed by:", Counter(terms[key]).most_common(3))
                tsum += tots[key]
                if (len(dwss[key]) > 0):
                    # count = 0
                    # for item in flat_list:
                    #     if key + "d" in item:
                    #         count += 1
                    # print(.25 * count)
                    print("Percent in Deep Work:", np.round(100 * np.sum(dwss[key]) / tots[key], 1), "%", "\tTotal:",
                          np.round(np.sum(dwss[key]), 2))
                    print("Deep Work Session Average:", np.round(np.mean(dwss[key]), 3), "Std. Dev ",
                          np.round(np.std(dwss[key]), 3))

    print("Checksum:",tsum,"=?",totalDays*24)
    print("Total Deep Work: ",np.round(dw_tot))
def overtimeplots(flat_list,def_dict,fname,dates):
    # over time plots
    splitter = 96*7 # 1 week
    weeks = int(len(flat_list)/splitter+1)
    full_data = dict()
    dw_data = dict()
    for key in def_dict:
        full_data[def_dict[key]] = [0]*weeks
        if dw_eligible[key]:
            dw_data[def_dict[key]] = [0]*weeks
    for i,fifteen in enumerate(flat_list):
        fif = fifteen.strip("d")
        full_data[def_dict[fif]][int(i/splitter)] += .25
        if "d" in fifteen and dw_eligible[fif]:
            dw_data[def_dict[fif]][int(i/splitter)] += .25
    for j in range(weeks):
        wsum = 0
        dwsum = 0
        for key in full_data.keys():
            wsum += full_data[key][j]
        for key in dw_data.keys():
            dwsum += dw_data[key][j]
        for key in full_data.keys():
            if wsum != 0:
                full_data[key][weeks-1] *= 168/wsum
            else:
                full_data[key][weeks-1] = 0
        for key in dw_data.keys():
            if dwsum != 0:
                dw_data[key][weeks-1] *= 168/dwsum
            else:
                dw_data[key][weeks-1] = 0
    full_data = {key: value for key, value in full_data.items() if sum(value) != 0}
    dw_data = {key: value for key, value in dw_data.items() if sum(value) != 0}

    start_date = datetime.strptime(dates[0], '%Y-%m-%d')
    days_from_start = (start_date - datetime(start_date.year, 1, 1)).days
    week_starts = [start_date + timedelta(days=(7 * i)) for i in range((365 - days_from_start) // 7 + 1)]
    def OtimePlot(doSleep,d,dname):
        plt.figure(figsize=(12, 8))
        setL=-1
        for category, values in d.items():
            if category == 'sleep' and not doSleep:
                continue
            setL = len(values)
            plt.plot(week_starts[0:setL], values, label=category)
        plt.xlabel('Date')
        plt.xticks(week_starts[0:setL],rotation=60)
        plt.ylabel('Hours per week')
        plt.legend(fontsize='small')
        full_path = os.path.join(fname, dname)
        plt.title("Activities ("+dates[0]+" --> "+dates[1]+')')
        plt.savefig(full_path, dpi=300)
        plt.clf()
    OtimePlot(True,full_data,"OverTime.png")
    OtimePlot(False,full_data,"OverTimeNoSleep.png")
    OtimePlot(False,dw_data,"DWTime.png")
    # correlations
    correlation_matrix = np.corrcoef([full_data[key] for key in full_data])
    plt.imshow(correlation_matrix, cmap='RdYlGn', vmin=-1, vmax=1)
    plt.colorbar(label='Correlation', ticks=np.arange(-1, 1.1, 0.5))
    plt.xticks(ticks=np.arange(len(full_data)), labels=full_data.keys(), rotation=20,ha='right')
    plt.yticks(ticks=np.arange(len(full_data)), labels=full_data.keys())
    plt.title("Week-to-Week Time Correlations ("+dates[0]+" --> "+dates[1]+')')
    full_path2 = os.path.join(fname, "WeeklyCorrelation.png")
    plt.savefig(full_path2, dpi=300)
    plt.clf()




    # most frequent at each time of day


    num_weeks = len(flat_list) // (7 * 96)
    activities = flat_list[:num_weeks * 7 * 96]
    for i in range(len(activities)):
        activities[i] = activities[i].strip("d")
    mode_weekly_data = []
    for i in range(7 * 96):
        weekly_activities = activities[i::7 * 96]
        imode = mode(weekly_activities)
        mode_weekly_data.append(imode)

    weekly_data = [mode_weekly_data[i:i + 96] for i in range(0, len(mode_weekly_data), 96)]
    plt.figure(figsize=(12, 8))
    for i in range(7):
        for j in range(96):
            time = j % 4  # Get the time interval index (0, 1, 2, 3)
            stagger = time * 0.2 -.4  # Stagger each letter based on the time interval
            plt.text(i + stagger, 95 - j, weekly_data[i][j], ha='center', va='center', color='black')
        plt.axhline(y=24, color='black', linestyle='-', linewidth=0.5)
        plt.axhline(y=48, color='black', linestyle='-', linewidth=0.5)
        plt.axhline(y=72, color='black', linestyle='-', linewidth=0.5)
    plt.xticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    plt.yticks(range(0, 96, 4), [f"{hour:02d}:00" for hour in reversed(range(0, 24))])
    plt.xlabel('Days')
    plt.ylabel('Time')
    plt.title("Most Common Activities By Time ("+dates[0]+" --> "+dates[1]+')')
    plt.xlim(-0.5, 6.5)
    plt.ylim(-0.5, 95.5)
    plt.grid(visible=False)
    plt.tight_layout()
    full_path2 = os.path.join(fname, "MostCommonActivityByTime.png")
    plt.savefig(full_path2, dpi=300)
def extra_analysis(dates,df,aux_dict,fname):
    d1 = datetime.strptime(dates[0], '%Y-%m-%d')
    d2 = datetime.strptime(dates[1], '%Y-%m-%d')
    day_starts = [d1 + timedelta(days=i) for i in range((d2-d1).days + 1)]
    d11 = start_row + (d1 - start_date).days
    d22 = d11 + (d2-d1).days+1
    for key,val in aux_dict.items():
        values = df.iloc[d11:d22,val[0]].values.astype('float')
        plt.figure(figsize=(8, 4))
        plt.plot(day_starts, values, marker='o')
        plt.title(f"{key} Consumption from {d1.date()} to {d2.date()}")
        plt.ylabel(val[1])
        plt.xlabel('Date')
        plt.tight_layout()
        file_name = key + "_consumption.png"
        full_path = os.path.join(fname, file_name)
        plt.savefig(full_path, dpi=300)
        plt.clf()

def pull_schedule(dates,dataframe,show=False):
    d1 = datetime.strptime(dates[0], '%Y-%m-%d')
    d2 = datetime.strptime(dates[1], '%Y-%m-%d')
    totalDays = (d2 - d1).days + 1
    d11 = start_row + (d1 - start_date).days
    d22 = d11 + (d2 - d1).days + 1
    if show:
        print("Timespan:", totalDays, 'days')
        print("From", d1, "to", d2)
    data_range = dataframe.iloc[d11:d22, start_col - 1:end_col]
    data_list = data_range.values.tolist()
    flist = [item for sublist in data_list for item in sublist]
    if show:
        for i, row in enumerate(data_list):
            print(d1 + timedelta(days=i), row)
    return data_list,flist

# def lossFunction(tdict,def_dict,sched,hardsched,gsink,wdict,dw_bonus,wcurve,nwcurve,verbose=False):
#     newsched = reassignDW(sched)
#     conts, terms, tots, dwss = schedule_analyze(newsched,def_dict)

#     totalDays = int(len(newsched)/96)
#     if verbose:
#         if totalDays != sum(list(tdict.values()))/24:
#             print("ERROR: BAD TARGET DICTIONARY")
#             return -1
#         else:
#             print("Scheduling...")

#     totalWork = 0
#     #  hard schedule matching
#     hardPenalty = 3 # hours per 15 min missed
#     penSum = 0
#     for i,block in enumerate(newsched):
#         if hardsched[i] is not None:
#             if hardsched[i] != block.strip("d"):
#                 penSum += hardPenalty
#                 if verbose:
#                     print("Sched",hardsched[i],"Sub",block,num2weektime(i))
#     totalWork -= penSum
#     # WORK TIME
#     # time allocations and deep work
#     actualHours = 0
#     dwHours = 0
#     ndwHours = 0
#     gsinkReward =.5
#     allocPenalty = 3 # hours per hour missed off allocation
#     if verbose:
#         print("Hard Constraints","\t\tpenalty:",hardPenalty)
#         print("Penalty From Skipped Sessions:",penSum)
#         print("Bonus Categories",gsink,"\t\tBonus Multiplier",gsinkReward)
#         print("Allocation default penalty",allocPenalty,"(h/h)")
#     penAllocSum = 0.0
#     contextSwitches = 0
#     for key in tdict:
#         contextSwitches += len(conts[key])
#         if key in wdict:
#             nonDW = tots[key] - np.sum(dwss[key])
#             ndwHours += nonDW
#             actualHours += tots[key] # for accounting
#             dwbonus = 0
#             for dw in dwss[key]: # adding time multiplier
#                 dwbonus += dw_bonus[int(dw/.25)-1]
#             dwHours += dwbonus
#             if dwbonus+nonDW < tdict[key]: # penalty for missing allocation, allowing for efficiency gains
#                 misallocated = (dwbonus+nonDW - tdict[key])*allocPenalty*wcurve[key]
#                 if verbose:
#                     print("Misallocated (work):",def_dict[key],misallocated)
#                 penAllocSum += misallocated
#             if key in gsink:
#                 if verbose:
#                     print("bonus",def_dict[key],max(0,dwbonus+nonDW-tdict[key])*gsinkReward)
#                 totalWork += max(0,dwbonus+nonDW-tdict[key])*gsinkReward
#     cswitchCost = .2
#     totalWork -= contextSwitches*cswitchCost
#     totalWork += penAllocSum
#     totalWork += dwHours
#     totalWork += ndwHours

#     if verbose:
#         print("Context Switching cost rate:",cswitchCost,"hours","Costs:",-contextSwitches*cswitchCost)
#         print("actual hours",actualHours,"\t\tnon-DW",ndwHours,"\t\tactualDW",actualHours-ndwHours,"\t\teffective work from DW",dwHours,"\t\tallocation penalty",penAllocSum)

#     # loss from sleep (sd, multiplying all productivity)
#     sleep_factor = 1 + .3/25*relu(50-tots['s']) # implies need 50h to function at 100%, 25 at 70 % productivity
#     napCutoff = 5
#     zombiePenalty = .1
#     night_sleeps = [item for item in conts['s'] if item > napCutoff]
#     sleepstd = np.std(night_sleeps)
#     baseVariability = 1.5
#     scaleVariability = 10
#     sleep_factor += (baseVariability - sleepstd)/scaleVariability
#     sleep_factor -= zombiePenalty*(totalDays-len(night_sleeps))
#     sleep_factor = min(sleep_factor,1)
#     if np.isnan(sleep_factor):
#         sleep_factor = .5
#     if verbose:
#         print("")
#         print("Sleep factor",sleep_factor,"\t\tStd. Dev",sleepstd,"\t\tBase Variability and Scale Variability",baseVariability,scaleVariability,"Nap Cutoff, All-nighter penalty",napCutoff,zombiePenalty)
#         print("Night Sleeps",night_sleeps)
#         print("")
#     totalWork *= sleep_factor

#     # NON WORK TIME
#     lifeVal = 0 # always negative because measures deviation from optimal
#     notwork = [key for key in tdict if key not in wdict]
#     notwork.remove('s')
#     for key in notwork:
#         modder = abs(tots[key]-tdict[key])*nwcurve[key]
#         if verbose:
#             print("Misallocation (nonwork):",def_dict[key],-modder)
#         lifeVal -= modder
#     worklifeBalance = .5
#     if verbose:
#         print("Life Optimality:",lifeVal, "'Life/Work' Balance",worklifeBalance)
#     overallScore = totalWork + worklifeBalance*lifeVal
#     return (overallScore,)

"""
	constraints/factors on schedule maker ONCE i have defined target allocation (adding to 168)
		constraints
			classes (hard)
			meals (soft)
			work out at least every other day (soft)
		factors
			deep work multiplier (1.5 - 2.5 ish) - google it - define at 2h minimum now
			time of day productivity factor
			meta - will try to minimize slippage/friction in schedule bc there is a minimum e in between each deep work session?
			minimize sleep SD
			only some subjects have deep work eligibility
			extra time goes into "sink" categories (linear extra points), otherwise try to hit targets by minimizing gap - NO, cause goodharting because penalizes efficiency
		reward points
			effective hours
			maybe bonuses for # for % in deep work per category?
			how to blend wanting to hit targets and deep work? not at odds just different metrics
                just subtract from loss for getting more deep work in?
                each target in work category (1-5, g, r) needs to hit allocation minimum in some way, otherwise ok
	algo design
	    set hard limits into array
"""
# def sched_from_events(eventList,size):
#     schedule = [None]*size
#     for event in eventList:
#         if event[4]:
#             start = weektime2num(event[0], event[1])
#             for i in range(start, start + event[2]):
#                 if i < size:
#                     schedule[i] = event[3]
#     return schedule, schedule.count(None)
# def nice_schedule(flat_list,ddict):
#     for i,set in enumerate(flat_list):
#         if set is not None:
#             d,t = num2weektime(i)
#             if "d" in set:
#                 adder= " (DW)"
#             else:
#                 adder=""
#             print(i,d,t,ddict[set.strip('d')]+ adder)
# TODO evolution algo
# TODO midweek reallocation
# TODO get free times