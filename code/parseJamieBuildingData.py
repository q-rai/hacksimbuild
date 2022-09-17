import json
import pandas as pd

# load in building file
df = pd.read_csv('Downloads/Building3147_Aug2019.csv')

# separate time and date
cols = df.apply(lambda row: row.Time.split(), axis=1, result_type='expand')
df['Date'] = cols[0]
df['Time'] = cols[1]

# make a list of rooms
rooms = []
for column in df.columns:
    if 'IHL' in column:
        rooms.append(column.split('_')[1])

# make an empty dictionary for the data, organized by date/time/room
dataDict = {}
for date in df.Date.unique():
    dataDict[date] = {}
    for time in df.Time.unique():
        dataDict[date][time] = {}
        for room in rooms:
            dataDict[date][time][room] = {}

# go over the data row by row and fill in the dictionary
for index, row in df.iterrows():
    # general variables for the entire building
    dataDict[row['Date']][row['Time']]['Temp'] = row['Temp']
    dataDict[row['Date']][row['Time']]['WindS'] = row['WindS']
    dataDict[row['Date']][row['Time']]['Hconvec'] = row['Hconvec']
    
    # room-specific variables
    for room in rooms:
        # separate Tsol/Qsolar from IHL and surround with try/except since not all rooms have all variables
        try:
            dataDict[row['Date']][row['Time']][room]['Tsol_Cal'] = row['Tsol_{}_Cal'.format(room)]
            dataDict[row['Date']][row['Time']][room]['Qsolar_Cal'] = row['Qsolar_{}_Cal'.format(room)]
        except:
            pass
        try:
            dataDict[row['Date']][row['Time']][room]['IHL'] = row['IHL_{}'.format(room)]
        except:
            pass
        
# write dictionary to file
with open('Downloads/Building3147_Aug2019.json', 'w') as outfile:
    json.dump(dataDict, outfile, indent=2)




