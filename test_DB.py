import sqlite3

db = sqlite3.connect('files.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXIST docs (

)""")
