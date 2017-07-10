import datetime

from peewee import *

db = SqliteDatabase('job_database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Job(BaseModel):
    # Job fields
    job_key = TextField(primary_key=True)
    link = TextField()
    title = CharField()
    description = TextField(null=True)
    company = TextField()
    city = CharField()
    state = CharField()
    country = CharField()
    posted_date = DateField()
    expired = BooleanField(default=False)
    location = CharField()

    # Application fields
    easy_apply = BooleanField(default=False)
    applied = BooleanField(default=False)
    access_date = DateField(null=True)
    error = TextField(null=True)
    message = TextField(null=True)
    good_fit = BooleanField(default=True)


class Question(BaseModel):
    """
    A model for the questions on Indeed easy apply
    """
    label = TextField(primary_key=True)
    answer = TextField(null=True)
    website = CharField(null=False)
    input_type = CharField(null=False)
    secondary_input_type = CharField(null=True)
    question_type = CharField(null=True)
"""
These next two models are for the application builder
"""


class Blurb(BaseModel):
    id = PrimaryKeyField()
    text = TextField(null=False)
    score = IntegerField(default=1)

    @staticmethod
    def get_header():
        return "Blurb Header\nid :: Blurb\n\n"

    def __str__(self):
        return "{0} :: {1}".format(self.id, self.text)


class Tag(BaseModel):
    id = PrimaryKeyField()
    text = CharField(null=False)
    blurb = ForeignKeyField(Blurb, related_name='tags')
    type = CharField(null=True) # Example mechanical or software?

    @staticmethod
    def get_header():
        return "Tag Header\nid :: blurbId :: text\n\n"

    def __str__(self):
        return "{0} :: {1} :: {2}".format(self.id, self.blurb.id, self.text)

