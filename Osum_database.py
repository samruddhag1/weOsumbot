# -*- coding: utf-8 -*-
"""
database related functions for transaction table analysis.
"""

import dataset
import itertools

# connecting to a SQLite database
db = dataset.connect('sqlite:///exportdata/transactions.db')

# get a reference to the table 'transactions'
table = db['usertransactions']

#Printing out the table
#'id','token','sender','reciever','amount','reason'
def showlist(table,sublist):

    #Printing headers
    print (('{:^10} '*6).format('id','token','sender','reciever','amount','reason'))
    print('\n')
    
    #Printing values
    for row in sublist:
        row['reciever'] = str(row['reciever'])
        print(  '{id:^10} {token:^10} {sender:^10} {reciever:^10} {amount:^10} {reason:.<10.10}'.format(**row))




if __name__ == '__main__':
    
    showlist(table,table)