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

    def getHeader():
        return "Blurb Header\nid :: Blurb\n\n"

    def __str__(self):
        return "{0} :: {1}".format(self.id, self.text)

class Tag(BaseModel):
    id = IntegerField(primary_key=True)
    text = CharField(null=False)
    blurb = ForeignKeyField(Blurb, related_name='tags')

    def getHeader():
        return "Tag Header\nid :: blurbId :: text\n\n"

    def __str__(self):
        return "{0} :: {1} :: {2}".format(self.id, self.blurb.id, self.text)




