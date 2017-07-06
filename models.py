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
    cover_letter = TextField(null=True)
    good_fit = BooleanField(default=True)

"""
These two models are for the application generator
"""
class Blurb(BaseModel):
    id = PrimaryKeyField()
    text = TextField(null=False)
    score = IntegerField(default=1)

    @staticmethod
    def getHeader():
        return "Blurb Header\nid :: Blurb\n\n"

    def __str__(self):
        return "{0} :: {1}".format(self.id, self.text)

class Tag(BaseModel):
    id = PrimaryKeyField()
    text = CharField(null=False)
    blurb = ForeignKeyField(Blurb, related_name='tags')
    type = CharField(null=True) # Example mechanical or software?

    @staticmethod
    def getHeader():
        return "Tag Header\nid :: blurbId :: text\n\n"

    def __str__(self):
        return "{0} :: {1} :: {2}".format(self.id, self.blurb.id, self.text)

