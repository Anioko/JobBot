import datetime

from peewee import *

db = SqliteDatabase('job_database.db')

class BaseModel(Model):
    class Meta:
        database = db

class Job(BaseModel):
    # Link Information
    link_id = TextField(primary_key=True)
    link = TextField()

    # Job fields
    title = TextField()
    description = TextField(null=True)
    company = TextField()
    location = TextField()

    # Application fields
    easy_apply = BooleanField(default=False)
    applied = BooleanField(default=False)
    attempted = BooleanField(default=False)
    date = DateField(default=datetime.datetime.now().date())
    error = TextField(null=True)

"""
These two models are for the application generator
"""
class Blurb(BaseModel):
    id = IntegerField(primary_key=True)
    text = TextField(null=False)

class Tag(BaseModel):
    id = IntegerField(primary_key=True)
    keyword = CharField()
    blurb = ForeignKeyField(Blurb, related_name='tags')




