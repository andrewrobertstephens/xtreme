#!/usr/bin/env python

import datetime
import sqlite3

class Database:

	'''All the database stuff for the application'''

	def __init__(self):
		'''Initialize Database class'''
		self.connection = sqlite3.connect('xtreme3.db')
		self.cursor = self.connection.cursor()

	def clear(self):
		'''Clear the contents of the database'''
		sql = 'delete from Customers'
		self.cursor.execute(sql)
		sql = 'delete from Transactions'
		self.cursor.execute(sql)
		self.connection.commit()

	def commit(self):
		'''Commit transaction'''
		self.connection.commit()

	def rollback(self):
		'''Rollback transaction'''
		self.connection.rollback()

	def last_row_id(self):
		'''Return last inserted id'''
		return self.cursor.lastrowid

	def load_csv(self, filename):
		'''Load CSV into database'''
		file = open(filename,'r')
		for line in file.readlines():
			(name,phone,comments) = line.split(',')
			if name != 'Name':
				(firstname,lastname) = name.split(' ')
				self.new_customer(firstname.capitalize(),lastname.capitalize(),phone,'','',1,45.00,comments.capitalize())
		file.close()

	def payday_execute(self, reverse=False):
		'''Execute the payday algorithm'''
		for customer in self.get_customers():
			customer_id = int(customer[0])
			if reverse:
				monthly = -float(customer[7])
			else:
				monthly = float(customer[7])
			owing = float(customer[8]) + monthly
			date = datetime.date.today().strftime('%Y-%m-%d')
			sql = '''insert into Transactions (CustomerID,Date,Description,Amount) values (?,?,?,?)'''
			self.cursor.execute( sql, (customer_id,date,'Monthly Fee',monthly) )
			sql = '''update Customers set Owing=? where CustomerID=?'''
			self.cursor.execute( sql, (owing,customer_id) )
		self.connection.commit()

	def transaction(self,customerid,description,amount):
		'''New transaction for customer'''
		date =  datetime.date.today().strftime('%Y-%m-%d')
		sql = 'insert into Transactions (CustomerID, Date, Description, Amount) values (?,?,?,?)'
		self.cursor.execute( sql, (customerid,date,description,amount) )
		sql = 'select Owing from Customers where CustomerID=%d' % customerid	# would be better to use sql parameters (but doesn't work)
		self.cursor.execute( sql )
		owing = float(self.cursor.fetchone()[0]) + float(amount)
		sql = 'update Customers set Owing=? where CustomerID=?'
		self.cursor.execute( sql, (owing,customerid) )
		self.connection.commit()

	def new_customer(self,firstname,lastname,phone,email,address,membership,monthly,comments):
		'''Create a new customer'''
		sql = '''insert into Customers (FirstName,LastName,Phone,Email,Address,Membership,Monthly,Owing,Comments,Active) values (?,?,?,?,?,?,?,?,?,?)'''
		self.cursor.execute( sql, (firstname,lastname,phone,email,address,membership,monthly,0.00,comments,"true") )
		self.connection.commit()
		return self.cursor.lastrowid

	def get_customers(self,owing=False,membership=None,active=True):
		'''Get a list of customers using criteria provided'''
		if owing==True:
			sql = '''select * from Customers where Owing > 0 and Active="true"'''
		elif membership != None:
			sql = '''select * from Customers where Membership="%d" and Active="true"''' % (membership)
		elif active==False:
			sql = '''select * from Customers where Active="false"'''
		else:
			sql = '''select * from Customers where Active="true"'''
		sql += ''' order by LastName, FirstName'''
		self.cursor.execute(sql)	# would be better to use sql parameters
		return self.cursor.fetchall()

	def get_customer(self, id):
		'''Get all info for one customer based on id'''
		sql = 'select * from Customers where CustomerID=%d' % int(id)	# would be better to use sql paramaters
		self.cursor.execute(sql)
		return self.cursor.fetchone()

	def get_transactions(self, customer_id):
		'''Get payment history for customer'''
		sql = 'select Date, Description, Amount from Transactions where CustomerID=%d order by Date desc, TransactionID desc' % customer_id
		self.cursor.execute(sql)
		return self.cursor.fetchall()

	def save_customer(self,id,firstname,lastname,phone,email,address,membership,monthly,comments):
		'''Update row in Customer table'''
		sql = '''update Customers set FirstName=?,LastName=?,Phone=?,Email=?,Address=?,Membership=?,Monthly=?,Comments=? where CustomerID=?'''
		self.cursor.execute( sql, (firstname,lastname,phone,email,address,membership,monthly,comments,id) )
		self.connection.commit()

	def save_customer_active(self, customer_id, active='true'):
		'''Deactivate customer'''
		sql = 'update Customers set Active="%s" where CustomerID="%d"' % ( active, int(customer_id) )
		self.cursor.execute(sql)
		self.connection.commit()

if __name__ == '__main__':
	database = Database()
	database.clear()
	database.load_csv('xtreme.csv')
	
