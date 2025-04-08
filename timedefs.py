from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import namedtuple

def excel_column_to_number(column_string):
    column_number = 0
    for char in column_string:
        column_number = column_number * 26 + (ord(char) - ord('A') + 1)
    return column_number
def excel_number_to_column(column_number):
    column_string = ""
    while column_number > 0:
        remainder = (column_number - 1) % 26  # Get the remainder (0 to 25)
        column_string = chr(ord('A') + remainder) + column_string  # Convert to character and prepend
        column_number = (column_number - 1) // 26  # Integer division to get the next quotient
    return column_string

default_labels = {
    's': 'sleep',
    'e': 'eating and logistics',
    'r': 'RSOs and internship apps',
    'p': 'misc projects',
    't': 'social',
    'u': 'thinking',
    'n': 'procrastinating',
    'w': 'working out',
    'g': 'research',
    'l': 'reading and listening',
    '1': 'class 1',
    '2': 'class 2',
    '3': 'class 3',
    '4': 'class 4',
    '5': 'audit',
    'j': 'email',
    'k': 'high quality social',
    'a': 'applications',
    'c': 'cooking & laundry',
}
dw_eligible = {
    's': False,
    'e': False,
    'r': True,
    'p': True,
    't': False,
    'u': True,
    'n': False,
    'w': False,
    'g': True,
    'l': False,
    '1': True,
    '2': True,
    '3': True,
    '4': True,
    '5': True,
    'j': False,
    'k': False,
    'a': True,
    'c': False,
}

auxiliary_dict = {
    "Sauce": [8,"sauce"],
}

wbreak22_labels = default_labels.copy()
wbreak22_labels['r'] = 'RSOs,internship apps,trek'
wbreak22_dict = {
    'name': "winter break 22-23",
    'dates': ['2022-12-10', '2023-01-02'],
    'defs': wbreak22_labels
}

winter23_labels = default_labels.copy()
winter23_labels['1'] = "Human Being and Citizen 2"
winter23_labels['2'] = "Math 184 Multivariable Calculus"
winter23_labels['3'] = "Physics 142 E&M"
winter23_labels['4'] = "Chemistry 262 Thermodynamics"
winter23_labels['5'] = "Audit: Chemistry 201 Inorganic I"
winter23_dict = {
    'name': "winter quarter 2023",
    'dates': ['2023-01-03', '2023-03-10'],
    'defs': winter23_labels
}

spring23_labels = default_labels.copy()
spring23_labels['1'] = "Human Being and Citizen 3"
spring23_labels['2'] = "Math 185 Differential Equations"
spring23_labels['3'] = "Physics 143 Waves and Optics"
spring23_labels['4'] = "Chemistry 268 Quantum Molecular and Materials Modeling"
spring23_labels['5'] = "Audit: MENG 266 Solid State Physics"
spring23_dict = {
    'name': "spring quarter 2023",
    'dates': ['2023-03-20', '2023-05-26'],
    'defs': spring23_labels
}
week1_dict = {
    'name': "week 1",
    'dates': ['2023-04-10','2023-04-16'],
    'defs': spring23_labels
}
week2_dict = {
    'name': 'week 2',
    'dates':['2023-05-08','2023-05-14'],
    'defs':spring23_labels
}

summerjune_labels = default_labels.copy()
summerjune_labels['1'] = "Shankar Quantum Mechanics"
summerjune_labels['2'] = "Ashcroft Mermin Solid State"
summerjune_labels['3'] = "CS Placement Prep"
summerjune_labels['4'] = "Argonne"
summerjune_labels['5'] = None
summerjune_dict= {
    'name':'summer break pre Argonne 2023',
    'dates':['2023-05-27','2023-07-09'],
    'defs':summerjune_labels
}

argonne_labels = default_labels.copy()
argonne_labels['4'] = "Argonne Work"
argonne_labels['3'] = "CS Placement Prep + Lin Alg."
argonne_labels['2'] = None
argonne_labels['1'] = None
argonne_labels['5'] = None
summerargonne_dict ={
    'name':"Argonne + After",
    'dates':['2023-07-10','2023-09-24'],
    'defs':argonne_labels
}

fall23_labels = default_labels.copy()
fall23_labels['1'] = "Greece"
fall23_labels['2'] = "Math 186"
fall23_labels['3'] = "Quantum Engineering"
fall23_labels['4'] = "MENG 211"
fall23_labels['5'] = None
fall23_dict = {
    'name':"fall quarter 2023",
    'dates':['2023-09-25','2023-12-08'],
    'defs': fall23_labels
}

wbreak23_labels = default_labels.copy()
wbreak23_labels['1'] = None
wbreak23_labels['2'] = None
wbreak23_labels['3'] = None
wbreak23_labels['4'] = None
wbreak23_labels['5'] = None
wbreak23_dict = {
    'name':"winter break 2023",
    'dates':['2023-12-09','2024-01-02'],
    'defs': wbreak23_labels
}

aggregate23_labels = default_labels.copy()
aggregate23_labels['1'] = 'Classwork + Argonne'
aggregate23_labels['2'] = 'Classwork + Argonne'
aggregate23_labels['3'] = 'Classwork + Argonne'
aggregate23_labels['4'] = 'Classwork + Argonne'
aggregate23_labels['5'] = 'Classwork + Argonne'
aggregate23_labels['k'] = 'social' # to autogroup with t
aggregate23_labels['a'] = 'RSOs and internship apps' # to autogroup with r
aggregate23_dict = {
    'name':"2023 wrapped",
    'dates':['2023-01-01','2023-12-31'],
    'defs': aggregate23_labels
}

aggregate23_labels2 = default_labels.copy()
aggregate23_labels2['k'] = 'social' # to autogroup with t
aggregate23_labels2['1'] = 'productive'
aggregate23_labels2['2'] = 'productive'
aggregate23_labels2['3'] = 'productive'
aggregate23_labels2['4'] = 'productive'
aggregate23_labels2['5'] = 'productive'
aggregate23_labels2['a'] = 'productive'
aggregate23_labels2['r'] = 'productive'
aggregate23_labels2['g'] = 'productive'
aggregate23_labels2['j'] = 'productive'
aggregate23_labels2['p'] = 'fun productive'
aggregate23_labels2['l'] = 'fun productive'
aggregate23_dict2 = {
    'name':"2023 wrapped, 2",
    'dates':['2023-01-01','2023-12-31'],
    'defs': aggregate23_labels2
}

winter24_labels = default_labels.copy()
winter24_labels['1'] = "Rome"
winter24_labels['2'] = "Statistics Markov Chains"
winter24_labels['3'] = "Physics 322 Graduate E&M I"
winter24_labels['4'] = "MENG 212"
winter24_labels['5'] = "Audit (none)"
winter24_labels['r'] = "Robotics"
winter24_dict = {
    'name': "winter quarter 2024",
    'dates': ['2024-01-03', '2024-03-07'],
    'defs': winter24_labels
}

spring24_labels = default_labels.copy()
spring24_labels['1'] = "Bayesian Epistemology"
spring24_labels['2'] = "CS 143 Systems Programming I"
spring24_labels['3'] = "Physics 323 Graduate E&M II"
spring24_labels['4'] = "BIOS 20186 Cell Biology"
spring24_labels['5'] = "Audit (PDEs, SDEs + PDEs)"
spring24_labels['r'] = "Robotics"
spring24_dict = {
    'name': "spring quarter 2024",
    'dates': ['2024-03-18', '2024-05-26'],
    'defs': spring24_labels,
}

summer24_labels = default_labels.copy()
summer24_labels['3'] = "Atlantic Quantum"
summer24_dict = {
    'name': "summer 2024",
    'dates': ['2024-05-27', '2024-09-29'],
    'defs': summer24_labels,
}

fall24_labels = default_labels.copy()
fall24_labels['1'] = "Honors Discrete Math"
fall24_labels['2'] = "CS 144 Systems Programming II"
fall24_labels['3'] = "MENG 215 Transport Phenomena"
fall24_labels['4'] = "MENG 314 Advanced Quantum Engineering"
fall24_dict = {
    'name': "fall quarter 2024",
    'dates': ['2024-09-30', '2024-12-12'],
    'defs': fall24_labels
}

wbreak24_labels = default_labels.copy()
wbreak24_labels['1'] = None
wbreak24_labels['2'] = None
wbreak24_labels['3'] = None
wbreak24_labels['4'] = None
wbreak24_labels['5'] = None
wbreak24_dict = {
    'name':"winter break 2024",
    'dates':['2024-12-13','2024-12-22'],
    'defs': wbreak24_labels
}

aggregate24_labels = default_labels.copy()
aggregate24_labels['1'] = 'Classwork + Atlantic'
aggregate24_labels['2'] = 'Classwork + Atlantic'
aggregate24_labels['3'] = 'Classwork + Atlantic'
aggregate24_labels['4'] = 'Classwork + Atlantic'
aggregate24_labels['5'] = 'Classwork + Atlantic'
aggregate24_labels['k'] = 'social' # to autogroup with t
aggregate24_dict = {
    'name':"2024 wrapped",
    'dates':['2024-01-01','2024-12-22'],
    'defs': aggregate24_labels
}

aggregate24_labels2 = default_labels.copy()
aggregate24_labels2['1'] = 'productive'
aggregate24_labels2['2'] = 'productive'
aggregate24_labels2['3'] = 'productive'
aggregate24_labels2['4'] = 'productive'
aggregate24_labels2['5'] = 'productive'
aggregate24_labels2['k'] = 'social' # to autogroup with t
aggregate24_labels2['a'] = 'productive'
aggregate24_labels2['r'] = 'productive'
aggregate24_labels2['g'] = 'productive'
aggregate24_labels2['j'] = 'productive'
aggregate24_labels2['p'] = 'fun productive'
aggregate24_labels2['l'] = 'fun productive'
aggregate24_labels2['e'] = 'life logistics'
aggregate24_labels2['c'] = 'life logistics'
aggregate24_dict2 = {
    'name':"2024 wrapped, 2",
    'dates':['2024-01-01','2024-12-22'],
    'defs': aggregate23_labels2
}

aggregate23_labels3 = default_labels.copy()
for key in aggregate23_labels3:
    if key != 's':
        aggregate23_labels3[key] = "not sleep"
aggregate23_dict3 = {
    'name': "2024 wrapped, 3",
    'dates': ['2024-01-01','2024-12-22'],
    'defs' : aggregate23_labels3
}

start_row = 2
start_col = excel_column_to_number('AJ')
end_col = excel_column_to_number('EA')
start_date = datetime.strptime("2022-12-05",'%Y-%m-%d')
timeframes = [
    wbreak22_dict, # 0
    winter23_dict, # 1
    spring23_dict, # 2
    summerjune_dict,    # 3
    summerargonne_dict, # 4
    fall23_dict,     # 5
    wbreak23_dict,   # 6
    aggregate23_dict, # 7
    aggregate23_dict2, # 8
    winter24_dict, # 9
    spring24_dict, # 10
    summer24_dict, # 11
    fall24_dict, # 12
    wbreak24_dict, # 13
    aggregate24_dict, # 14
    aggregate24_dict2, # 15
    aggregate23_dict3 # 16
]
df = pd.read_csv('Timespent.csv')
days2num = {'mo':0,'tu':1,'we':2,'th':3,'fr':4,'sa':5,'su':6}
num2days = {value: key for key, value in days2num.items()}

def weektime2num(day,time):
    h,t = divmod(time,100)
    return days2num[day]*96+h*4+(t//15)
def num2weektime(num):
    d,t = divmod(num,96)
    d = int(d) % 7
    h,m = divmod(t,4)
    timestr = h*100+15*m
    return num2days[d],timestr
Event = namedtuple("Event",["day","time","length","item","hardConstraint"])