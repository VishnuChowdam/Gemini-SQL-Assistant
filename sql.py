# pip install db-sqlite3
# pip install sqlite3
import sqlite3

#Connectt to SQlite
connection=sqlite3.connect("my_db.db")

# Create a cursor object to insert record,create table

cursor=connection.cursor()

#create the table
#Our table name student
#Columns names are: name, course
table_info="""
Create table employees(employee_name varchar(30),
                    employee_role varchar(30),
                    employee_salary FLOAT);
"""
cursor.execute(table_info)

#Insert the records

cursor.execute('''Insert Into employees values('Raju','Data Science',75000)''')
cursor.execute('''Insert Into employees values('Naresh','Data Science',90000)''')
cursor.execute('''Insert Into employees values('Phani','Developer',88000)''')
cursor.execute('''Insert Into employees values('Naga babu','Data Engineer',50000)''')
cursor.execute('''Insert Into employees values('Ajay','Data Engineer',35000)''')
cursor.execute('''Insert Into employees values('Pawan','Analyst',60000)''')

#Display ALl the records

print("The inserted records are")
data=cursor.execute('''Select * from employees''')
for row in data:
    print(row)

#Commit your changes int he databse
connection.commit()
connection.close()