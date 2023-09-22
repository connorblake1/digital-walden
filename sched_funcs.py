from collections import Counter
from timedefs import *

def schedule_analyze(flat_list,def_dict):
    conts = def_dict.copy()
    terms = def_dict.copy()
    tots = def_dict.copy()
    dwss = def_dict.copy()
    for key in conts:
        conts[key] = []
        terms[key] = []
        tots[key] = 0
        dwss[key] = []
    curr = None
    currLen = 0
    dw = False
    dwLen = 0
    for i, fifteen in enumerate(flat_list):
        fif = fifteen.strip("d")
        tots[fif] = tots[fif] + .25
        if curr == None:  # assumes not starting in DW
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
                        dwss[currkey].append(dwLen)
                    dwLen = 0
            else:
                terms[currkey].append(fif)
                conts[currkey].append(currLen)
                if dwLen > 0:
                    dwss[currkey].append(dwLen)
                currLen = .25
                dwLen = int(isdw) * .25
                curr = fifteen
            if i == len(flat_list) - 1:
                terms[currkey].append(fif)
                conts[currkey].append(currLen)
                if dwLen > 0:
                    dwss[currkey].append(dwLen)
    return conts, terms, tots, dwss
def reassignDW(flat_list):
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
def verbose_analyze(flat_list, def_dict,conts,terms,tots,dwss):
    totalDays = int(len(flat_list)/96)
    print("")
    tsum = 0
    for key in def_dict:
        if def_dict[key] is not None and len(conts[key]) != 0:
            print("")
            print("Code", key, def_dict[key])
            print(conts[key])
            print("Average Per Day (h):",np.round(np.sum(conts[key])/totalDays,3),"Average Session (h):", np.round(np.mean(conts[key]), 3) ,"Std. Dev of session:",
                  np.round(np.std(conts[key]), 3))
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
    print("Checksum:",tsum)
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
def lossFunction(tdict,def_dict,sched,hardsched,gsink,wdict,dw_bonus,wcurve,nwcurve,verbose=False):
    newsched = reassignDW(sched)
    conts, terms, tots, dwss = schedule_analyze(newsched,def_dict)

    totalDays = int(len(newsched)/96)
    if verbose:
        if totalDays != sum(list(tdict.values()))/24:
            print("ERROR: BAD TARGET DICTIONARY")
            return -1
        else:
            print("Scheduling...")

    totalWork = 0
    #  hard schedule matching
    hardPenalty = 3 # hours per 15 min missed
    penSum = 0
    for i,block in enumerate(newsched):
        if hardsched[i] is not None:
            if hardsched[i] != block.strip("d"):
                penSum += hardPenalty
                if verbose:
                    print("Sched",hardsched[i],"Sub",block,num2weektime(i))
    totalWork -= penSum
    # WORK TIME
    # time allocations and deep work
    actualHours = 0
    dwHours = 0
    ndwHours = 0
    gsinkReward =.5
    allocPenalty = 3 # hours per hour missed off allocation
    if verbose:
        print("Hard Constraints","\t\tpenalty:",hardPenalty)
        print("Penalty From Skipped Sessions:",penSum)
        print("Bonus Categories",gsink,"\t\tBonus Multiplier",gsinkReward)
        print("Allocation default penalty",allocPenalty,"(h/h)")
    penAllocSum = 0.0
    contextSwitches = 0
    for key in tdict:
        contextSwitches += len(conts[key])
        if key in wdict:
            nonDW = tots[key] - np.sum(dwss[key])
            ndwHours += nonDW
            actualHours += tots[key] # for accounting
            dwbonus = 0
            for dw in dwss[key]: # adding time multiplier
                dwbonus += dw_bonus[int(dw/.25)-1]
            dwHours += dwbonus
            if dwbonus+nonDW < tdict[key]: # penalty for missing allocation, allowing for efficiency gains
                misallocated = (dwbonus+nonDW - tdict[key])*allocPenalty*wcurve[key]
                if verbose:
                    print("Misallocated (work):",def_dict[key],misallocated)
                penAllocSum += misallocated
            if key in gsink:
                if verbose:
                    print("bonus",def_dict[key],max(0,dwbonus+nonDW-tdict[key])*gsinkReward)
                totalWork += max(0,dwbonus+nonDW-tdict[key])*gsinkReward
    cswitchCost = .2
    totalWork -= contextSwitches*cswitchCost
    totalWork += penAllocSum
    totalWork += dwHours
    totalWork += ndwHours

    if verbose:
        print("Context Switching cost rate:",cswitchCost,"hours","Costs:",-contextSwitches*cswitchCost)
        print("actual hours",actualHours,"\t\tnon-DW",ndwHours,"\t\tactualDW",actualHours-ndwHours,"\t\teffective work from DW",dwHours,"\t\tallocation penalty",penAllocSum)

    # loss from sleep (sd, multiplying all productivity)
    sleep_factor = 1 + .3/25*relu(50-tots['s']) # implies need 50h to function at 100%, 25 at 70 % productivity
    napCutoff = 5
    zombiePenalty = .1
    night_sleeps = [item for item in conts['s'] if item > napCutoff]
    sleepstd = np.std(night_sleeps)
    baseVariability = 1.5
    scaleVariability = 10
    sleep_factor += (baseVariability - sleepstd)/scaleVariability
    sleep_factor -= zombiePenalty*(totalDays-len(night_sleeps))
    sleep_factor = min(sleep_factor,1)
    if np.isnan(sleep_factor):
        sleep_factor = .5
    if verbose:
        print("")
        print("Sleep factor",sleep_factor,"\t\tStd. Dev",sleepstd,"\t\tBase Variability and Scale Variability",baseVariability,scaleVariability,"Nap Cutoff, All-nighter penalty",napCutoff,zombiePenalty)
        print("Night Sleeps",night_sleeps)
        print("")
    totalWork *= sleep_factor

    # NON WORK TIME
    lifeVal = 0 # always negative because measures deviation from optimal
    notwork = [key for key in tdict if key not in wdict]
    notwork.remove('s')
    for key in notwork:
        modder = abs(tots[key]-tdict[key])*nwcurve[key]
        if verbose:
            print("Misallocation (nonwork):",def_dict[key],-modder)
        lifeVal -= modder
    worklifeBalance = .5
    if verbose:
        print("Life Optimality:",lifeVal, "'Life/Work' Balance",worklifeBalance)
    overallScore = totalWork + worklifeBalance*lifeVal
    return (overallScore,)

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
def sched_from_events(eventList,size):
    schedule = [None]*size
    for event in eventList:
        if event[4]:
            start = weektime2num(event[0], event[1])
            for i in range(start, start + event[2]):
                if i < size:
                    schedule[i] = event[3]
    return schedule, schedule.count(None)
def nice_schedule(flat_list,ddict):
    for i,set in enumerate(flat_list):
        if set is not None:
            d,t = num2weektime(i)
            if "d" in set:
                adder= " (DW)"
            else:
                adder=""
            print(i,d,t,ddict[set.strip('d')]+ adder)
# TODO evolution algo
# TODO midweek reallocation
# TODO get free times