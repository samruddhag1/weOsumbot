# -*- coding: utf-8 -*-
"""
Learning to use simple database tools with the dataset module.
https://dataset.readthedocs.io/en/latest/quickstart.html
"""

import dataset
import itertools

# connecting to a SQLite database
db = dataset.connect('sqlite:///exportdata/transactions.db')

# get a reference to the table 'transactions'
table = db['usertransactions']

# Insert a new record.
current_trans = dict(transid=12345, ower='user0', amount='200')
table.insert(current_trans)
current_trans = dict(transid=67890, ower='user2', amount='150')
table.insert(current_trans)

table.insert(dict(transid=23456, ower='user0', amount='150'))
table.insert(dict(transid=78901, ower='user2', amount='300'))

#Updating/editing a record
table.update(dict(transid=67890, owee='user0'), ['transid'])

#Printing out the table
def showlist(table,sublist):
    for item in table.columns:
        print (item,end='\t')   #Printing headers
    print('\n')
    
    for row in sublist:
        for item in table.columns:
            print (row[item],end='\t')  #Printing values
        print(end='\n')

#Finding

#All user0_owes
user0_owes = table.find(ower='user0')
#All user0_isowed
user0_isowed = table.find(owee='user0')

#Merge the finds
user0_all=itertools.chain(user0_owes,user0_isowed)

# Get a specific transaction
trans23456 = table.find_one(transid=23456)

#All large trabsactions
largetrans = table.find(table.table.columns.amount >= 200)


#Export
dataset.freeze(largetrans, format='json', filename='/largetrans.json')