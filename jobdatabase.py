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