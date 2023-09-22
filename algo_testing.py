from preferences import *
import random
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
IND_SIZE = 96*7
MU = 500 # popsize
NGEN = 500
CXPB = .7
MUTPB = .2
def random_label():
    keys = list(default_labels.keys())
    random_key = random.choice(keys)
    return random_key

def random_schedule(l):
    # TODO generates list of events
    # ansatz that each category fulfills full data allocation at once
    lo =3
    hi = 16
    length = 0
    elist = []
    while length < l:
        d,t = num2weektime(length)
        nl = random.randrange(lo,hi)
        elist.append(Event(d,t,nl,random_label(),True))
        length += nl
        d, t = num2weektime(length)
        nl = random.randrange(1,3)
        elist.append(Event(d,t,nl,'e',True))
        length += nl
    for i in range(int(l/96)):
        d,t = num2weektime(i*96)
        elist.append(Event(d,t,29,'s',True))
    for event in hardList:
        elist.append(event)
    return sched_from_events(elist,l)[0]
def mut_sched(individual):
    if random.random() < .5: # flip one
        individual[random.randrange(IND_SIZE)] = random_label()
    else: # swap two
        i1, i2 = random.randrange(IND_SIZE),random.randrange(IND_SIZE)
        hold = individual[i1]
        individual[i1] = individual[i2]
        individual[i2] = hold
    return individual,

randList = []
for i in range(MU):
    randList.extend(random_schedule(IND_SIZE))
randIndex = -1
def rand_pull():
    global randIndex
    global randList
    randIndex += 1
    return randList[randIndex]

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


toolbox = base.Toolbox()
toolbox.register("attribute", rand_pull)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute,n=IND_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual,n=MU)
# TODO use initIterate or initCycle to build of sample schedule

toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", mut_sched)
toolbox.register("select", tools.selBest)
toolbox.register("evaluate", evaluate)

pop = toolbox.population(n=MU)
hof = tools.ParetoFront() # hall of fame
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register('avg',np.mean,axis=0)
stats.register('std',np.std,axis=0)
stats.register('min',np.min,axis=0)
stats.register('max',np.max,axis=0)
algorithms.eaSimple(pop,toolbox,CXPB,MUTPB,NGEN, stats,halloffame=hof,verbose=True)
# print(pop)
# print(stats)

print(hof[0])
print(evaluate(hof[0],True))
print(nice_schedule(hof[0],defs))