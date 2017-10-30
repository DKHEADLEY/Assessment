import csv
import json
import pprint as pp
import numpy as np

#Open all the data files
reader = csv.reader(open('labresults.csv'))
results = list(reader)
codereader = csv.reader(open('labresults-codes.csv'))
codes = list(codereader)
with open('patients.json') as json_data:
    spreadsheet = json.load(json_data)


def codefinder(string):
    '''Takes a code and returns the name of the test'''
    ind = np.array(codes)[:,0].tolist().index(string)
    return codes[ind][1]
def description(string):
    '''Takes a code and returns the name of the test'''
    ind = np.array(codes)[:,0].tolist().index(string)
    return codes[ind][2]
def date(string):
    """Takes a date written dd/mm/yyyy and recasts in ISO at midnight"""
    return string[6:10] +'-' + string[3:5] +'-'+string[0:2] + 'T00:00:00.000Z'
def stripvalue(string):
    '''strips text from fron to values'''
    return string[string.index('~')+1:]
def offset(n):
    '''Tells you where the result value is'''
    targ = results[n][5:30]
    for i in enumerate(targ):
        if i[1] != '':
            if i[1][:i[1].index('~')] == results[n][30]:
                return i[0]

#Initialise array
answer = []

#create profiles and initialise lab_results section
for person in spreadsheet:
    answer.append({'id':person['id']})    
    answer[-1]['firstName'] = person['firstName']
    answer[-1]['lastName'] = person['lastName']    
    answer[-1]['dob'] = person['dateOfBirth']
    answer[-1]['lab_results'] = [{}]
    answer[-1]['identifiers'] = person['identifiers']

#pp.pprint(answer)
info = []

#produce all of the panels
for n in range(1,len(results)):
    record = results[n] #Select a panel
    ID = results[n][0]
    panel = {}
    panel['code'] = codefinder(record[30])
    panel['label'] = description(record[30])
    panel['value'] = stripvalue(record[5+offset(n)])
    panel['unit'] = record[31]
    #Deal with exception if upper and lower are empty
    if record[32] != '':
        panel['lower'] = float(record[32]) 
        panel['upper'] = float(record[33])
    else: 
        panel['lower'] = 'n/a'
        panel['upper'] = 'n/a'
    info.append([ID, date(record[2]), record[4], record[3], panel])

#slot in the panels

#Select a panel and determine who it belongs to
for example in info:
    #find who panel belongs to
    for i,subject in enumerate(answer):
        if subject['identifiers'][0] == example[0]:
            personind = i
    #focus on lab reports of that one person
    focus = answer[personind]['lab_results']
        #If the person has no lab records, add the information and panel
    if focus[-1] == {}:
        #print 'Focus is empty, apply first entry'
        focus[-1]['timestamp'] = example[1]
        focus[-1]['profile'] = {}
        focus[-1]['profile']['code'] = example[2]        
        focus[-1]['profile']['name'] = example[3]
        focus[-1]['panel'] = []
        #Add panel
        focus[-1]['panel'].append(example[4])
    else:
        # Lab reports are nonempty, determine if existing lab report exists matching this panel
        counter = 0  #counts if a panel has been added
        #print 'Focus is length ',len(focus)
        for j in range(0,len(focus)):
            if focus[j]['timestamp'] == example[1] and focus[j]['profile']['code'] == example[2]:
                #The current panel matches a previous lab report and will be added to that
                focus[j]['panel'].append(example[4])  #add panel
                counter = 1  #indicate panel has been added
        if counter == 0:
            #no lab report exists for this sample, add a new one and slot in the panel
            focus.append({})
            focus[-1]['timestamp'] = example[1]
            focus[-1]['profile'] = {}
            focus[-1]['profile']['code'] = example[2]        
            focus[-1]['profile']['name'] = example[3]
            focus[-1]['panel'] = []
            focus[-1]['panel'].append(example[4])
            counter = 1

#Delete an identifier section I used to match panels to people
for element in answer:
    del element['identifiers']

#Add the top level structure required
answer = {'patients' : answer}

#save to a json file
with open('output.json', 'w') as outfile:
     json.dump(answer, outfile, sort_keys = True, indent = 4,
               ensure_ascii = False)
               

