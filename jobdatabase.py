import datetime

from peewee import *

db = SqliteDatabase('jobdatabase.db')

class BaseModel(Model):
    class Meta:
        database = db

class Job(BaseModel):
    link_id = TextField(primary_key=True)
    link = TextField()
    title = TextField()
    easy_apply = BooleanField(default=False)
    applied = BooleanField(default=False)
    date = DateField(default=datetime.datetime.now().date())
    error = TextField(null=True)

def databaseSetup():
    try:
        db.create_table(Job)
    except OperationalError:
        print('Job table already exists')

def databaseTearDown():
    db.drop_table(Job)
    db.close()