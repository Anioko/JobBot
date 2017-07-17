import datetime
from typing import Optional
from peewee import *

db = SqliteDatabase('job_database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Job(BaseModel):
    # Job fields
    key = CharField()
    website = CharField()
    link = TextField()
    title = CharField()
    description = TextField(null=True)
    company = TextField(null=True)
    city = CharField(null=True)
    state = CharField(null=True) # TODO: Rename this to region
    country = CharField(null=True)
    posted_date = DateField(null=True)
    expired = BooleanField(default=False)
    location = CharField(null=True)

    # Application fields
    easy_apply = BooleanField(default=False)
    applied = BooleanField(default=False)
    attempted = BooleanField(default=False)
    access_date = DateField(null=True)
    error = TextField(null=True)
    message = TextField(null=True)
    good_fit = BooleanField(default=True)

    class Meta:
        primary_key = CompositeKey('key', 'website')


class Question(BaseModel):
    """
    A model for the questions on Indeed easy apply
    """

    hash = CharField(primary_key=True)
    label = TextField()
    tokens = TextField()
    website = CharField()
    input_type = CharField()

    answer = TextField(null=True)
    secondary_input_type = CharField(null=True)
    question_type = CharField(null=True)
    additional_info = TextField(null=True)


class QuestionWrapper(object):
    @staticmethod
    def create_question(
            label:str,
            website:str,
            input_type:str,
            secondary_input_type=None,
            additional_info=None
    ):
        pass

"""
These next two models are for the application builder
"""


class Blurb(BaseModel):
    id = PrimaryKeyField()
    long_text = TextField(null=False)
    short_text = TextField(null=False)
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

