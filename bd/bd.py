import sqlite3

connection = sqlite3.connect("hh_bd.db")

cursor = connection.cursor()

sql = "CREATE TABLE vacancies (id TEXT, title TEXT," \
      " url TEXT, company_name TEXT, area TEXT, salary TEXT, valute TEXT)"
cursor.execute(sql)

connection.close()
