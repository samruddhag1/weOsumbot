# -*- coding: utf-8 -*-

class database():
    def __init__(self, name):
        #t --> transaction
        self.name  = name
        self.t_index = 0
        self.t_list = []
        self.balance = 0
        
        t0 = {'amount':0 , 'tag':'Account Creation'}
        self.t_list.append(t0)
    
    def addTransaction(self,transaction):
        #transaction is a dic with atleast an amount. date, tag optional
        self.t_index+=1
        self.t_list.append(transaction)
        self.balance+= transaction['amount']
        
    
    def getBalance(self):
        return self.balance
        
    def getStatement(self,no_of_transactions=10):
        if no_of_transactions == -1 or (no_of_transactions > self.t_index) :
            #show all transactions
            no_of_transactions = self.t_index
        
        s = 'Last {} transactions. (Newer First) \n'.format(no_of_transactions)
        for i in range(no_of_transactions):
            t_index = self.t_index - i 
            transaction = self.t_list[t_index]
            
            amount  = transaction.get('amount','--')
            date = transaction.get('date','--')
            tag = transaction.get('tag','--')
            
            s+= "{} Amount: {}    Date: {}    Reason: {} \n" .format(t_index,amount,date,tag)
            
        return s
    
    def __str__(self):
        s = ''
        s+= "---{} account--- \n\n".format(self.name)
        s+= "Transactions: {} \n".format(self.t_index)
        s+= "Balance: {} \n".format(self.balance)
        
        return s

#def makeTransansaction():