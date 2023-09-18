from datetime import datetime, timedelta

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
    'e': 'eating/logistics',
    'r': 'RSOs/internship apps',
    'p': 'programming projects / math problems',
    't': 'social',
    'u': 'planning/thinking',
    'n': 'procrastinating',
    'w': 'working out',
    'g': 'Yang lab',
    'l': 'reading/listening',
    '1': 'class 1',
    '2': 'class 2',
    '3': 'class 3',
    '4': 'class 4',
    '5': 'audit',
    'j': 'email'
}

wbreak22_labels = default_labels.copy()
wbreak22_labels['r'] = 'RSOs/internship apps/trek'
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
    'dates': ['2023-01-03', '2023-03-19'],
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

summerjune_labels = default_labels.copy()
summerjune_labels['1'] = "Shankar Quantum Mechanics"
summerjune_labels['2'] = "Ashcroft/Mermin Solid State"
summerjune_labels['3'] = "CS Placement Prep"
summerjune_labels['4'] = "Argonne"
summerjune_labels['5'] = None
summerjune_dict= {
    'name':'summer break pre Argonne 2023',
    'dates':['2023-05-27','2023-07-09'],
    'defs':summerjune_labels
}

argonne_labels = default_labels.copy()
argonne_labels['4'] = "Argonne"
argonne_labels['3'] = "CS Placment Prep / Lin Alg."
argonne_labels['2'] = None
argonne_labels['1'] = None
argonne_labels['5'] = None
summerargonne_dict ={
    'name':"Argonne",
    'dates':['2023-07-10','2023-09-15'],
    'defs':argonne_labels
}

start_row = 2
start_col = excel_column_to_number('AB')
end_col = excel_column_to_number('DS')
start_date = datetime.strptime("2022-12-05",'%Y-%m-%d')