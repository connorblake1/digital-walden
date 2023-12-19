from sched_funcs import *
from timedefs import *
import time


# START INPUTS
# define how many hours each will be per week
timeFrame = week1_dict
targetSum = 168
target_dict = dict()

# Schedule standing meetings/nonnegotiable events here
# event   day, time, #15 min blocks, category, hard constraint?

# FALL 2023
target_dict['s'] = 50  # overhead + productivity multiplier
target_dict['r'] = 13  # practical experience + career dev + network + fun + friends + meaning + knowledge
target_dict['g'] = 16  # practical experience + career dev + network + knowledge
target_dict['e'] = 15  # overhead
target_dict['t'] = 10  # fun + friends
target_dict['k'] = 5  # meaning + friends + expand possibilities
target_dict['1'] = 8  # requirement + meaning + expand possibilities
target_dict['2'] = 11  # requirement + knowledge + network
target_dict['3'] = 12  # requirement + practical experience + career dev + network + knowledge
target_dict['4'] = 12  # requirement + practical experience + career dev + network + knowledge
target_dict['5'] = 0  # NA
target_dict['j'] = 1  # overhead
target_dict['l'] = 2  # expand possibilities
target_dict['w'] = 5  # health + productivity multiplier
target_dict['p'] = 2  # fun + practical experience
target_dict['u'] = 6  # expand possibilities + productivity multiplier
target_dict['n'] = 0  # none (all negative)


hardList = [
            Event("mo", 830, 4, '2', True), # math
            Event("we", 830, 4, '2', True),
            Event("fr", 830, 4, '2', True),
            Event("mo", 930, 4, '4', True), # chem
            Event("we", 930, 4, '4', True),
            Event("fr", 930, 4, '4', True),
            Event("mo", 1030, 4, '3', True), # physics
            Event("we", 1030, 4, '3', True),
            Event("fr", 1030, 4, '3', True),
            Event("tu", 930, 6, '1', True), # civ
            Event("th", 930, 6, '1', True),
            Event("fr", 1330, 4, 'g', True),  # yang lab
            Event("mo", 1830, 8, 'r', True)  # robotics
            ]


# spring quarter 2023
# target_dict['s'] = 50  # overhead + productivity multiplier
# target_dict['r'] = 9  # practical experience + career dev + network + fun + friends + meaning + knowledge
# target_dict['g'] = 15  # practical experience + career dev + network + knowledge
# target_dict['e'] = 15  # overhead
# target_dict['t'] = 12  # fun + friends
# target_dict['k'] = 0  # meaning + friends + expand possibilities
# target_dict['1'] = 9.5  # requirement + meaning + expand possibilities
# target_dict['2'] = 8.5  # requirement + knowledge + network
# target_dict['3'] = 13  # requirement + practical experience + career dev + network + knowledge
# target_dict['4'] = 13  # requirement + practical experience + career dev + network + knowledge
# target_dict['5'] = 1  # NA
# target_dict['j'] = 3  # overhead
# target_dict['l'] = 3  # expand possibilities
# target_dict['w'] = 5  # health + productivity multiplier
# target_dict['p'] = 5  # fun + practical experience
# target_dict['u'] = 6  # expand possibilities + productivity multiplier
# target_dict['n'] = 0  # none (all negative)
# hardList = [
#             # Event("mo", 830, 4, '2', True), # math
#             # Event("we", 830, 4, '2', True),
#             # Event("fr", 830, 4, '2', True),
#             Event("tu", 1230, 6, '1', True), # chem
#             Event("th", 1230, 6, '1', True),
#             Event("tu", 1100, 6, '4', True), # physics
#             Event("th", 1100, 6, '4', True),
#             Event("tu", 930, 6, '3', True), # civ
#             Event("th", 930, 6, '3', True),
#             Event("fr", 1330, 4, 'g', True),  # yang lab
#             # Event("mo", 1830, 8, 'r', True)  # robotics
#             ]


goodsink = ['r','g'] # encourage to overrun allocation (given efficiency boosts from dw)
workcats = ['1','2','3','4','5','r','g','j'] # need to hit minimum allocations for schedule in some way, take priority
workCurve = { # how bad it is to undershoot (ie hum not important to miss but physics yes)
    '1':0,
    '2':1,
    '3':1,
    '4':1,
    '5':0,
    'r':1,
    'g':1,
    'j':0
}
defs = fall2023_labels
# how much work (in hours) 15 minutes of deep work is equivalent to (ie after 4 hours, each 15 minutes is worth 30 minutes)
dw_bonus_curve = [.25,.25,.25,.3,     .37,.37,.37,.37,     .4,.4,.4,.4,   .45,.45,.45,.45,     .5,.5,.5,.5,   .5,.5,.5,.5,    .5,.5,.5,.5,   .5,.5,.5,.5,    .5,.5,.5,.5,      .5,.5,.5,.5,     .5,.5,.5,.5,    .5,.5,.5,.5,     .5,.5,.5,.5,     .5,.5,.5,.5] # breaks after 9 hours
nonworkCurve = { # ie how bad it is if i am off target on my non work obligations
    'e':.5,
    't':1,
    'k':0, # TODO
    'l':0, # can spend time on, not too important if don't
    'w':1.5,
    'u':0, # highly variable week to week, hard to optimize
    'n':2, # penalizes procrastinating a lot
    'p':0
}

# END INPUTS


# print out category goals
verboseSchedule = False
if verboseSchedule:
    tsum = 0
    print("Category Goals (h):")
    for key in target_dict:
        print(target_dict[key],key,defs[key])
        tsum += target_dict[key]
    print("")
    print("Schedule Sum:",tsum,"Target:",targetSum)
# process events by expanding to all times and then printing out hard constraints
# hardsets = [None]*targetSum*4
# for event in hardList:
#     if event[4]:
#         start = weektime2num(event[0],event[1])
#         for i in range(start,start+event[2]):
#             hardsets[i] = event[3]
hardsets, nones = sched_from_events(hardList,targetSum*4)
if verboseSchedule:
    print("Commitments","None",nones)
    nice_schedule(hardsets,defs)
_,schedule = pull_schedule(timeFrame['dates'],df,verboseSchedule)
dw_bonus_cumulative = []
cumulative_sum = 0
for number in dw_bonus_curve:
    cumulative_sum += number
    dw_bonus_cumulative.append(cumulative_sum)

def evaluate(scheduleIn,verbosity=False):
    return lossFunction(target_dict,defs,scheduleIn,hardsets,goodsink,workcats,dw_bonus_cumulative,workCurve,nonworkCurve,verbose=verbosity)

# print("Function to Maximize: ",evaluate(schedule,True))