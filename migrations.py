from playhouse.migrate import *

my_db = SqliteDatabase('job_database.db')
migrator = SqliteMigrator(my_db)
