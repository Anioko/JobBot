from abc import ABC
from datetime import datetime

from selenium import webdriver

from Application.ApplicationBuilder import ApplicationBuilder
from Shared.helpers import Const
from Shared.models import Job, Question, Person
from userconfig import UserConfig


class RobotConstants(Const):
    WAIT_IMPLICIT = 5
    WAIT_DELTA = .100
    WAIT_ULTRA_LONG = 30
    WAIT_LONG = 15
    WAIT_MEDIUM = 7
    WAIT_SHORT = 2
    MAX_COUNT_APPLICATION_ATTEMPTS = 100

    class Driver(Const):
        FIREFOX = 'firefox'
        CHROME = 'chrome'

    class String(Const):
        UNABLE_TO_ANSWER = 'Unable to answer all questions'
        NOT_ENOUGH_KEYWORD_MATCHES = 'Not enough keyword matches in the description'
        QUESTION_LABELS_AND_INPUTS_MISMATCH = 'The number of labels and question input elements do not match'
        UNPAID = 'Unpaid internship'
        MAX_ATTEMPTS_REACHED = 'The maximum number of job application attempts has been reached'


class Robot(ABC):
    def __init__(
            self,
            user_config: UserConfig,
            driver=RobotConstants.Driver.FIREFOX
    ):
        self.user_config = user_config
        if driver == RobotConstants.Driver.CHROME:
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(RobotConstants.WAIT_IMPLICIT)
        self.application_builder = ApplicationBuilder(user_config)

        self._create_tables()

        if self.user_config.Settings.WILL_RELOAD_TAGS_AND_BLURBS:
            self.application_builder.reset_all_tables()
            print('Initializing Tags and Blurbs from {0}'.format(self.user_config.Path.JSON_TAG_BLURBS))
            self.application_builder.read_tag_blurbs(self.user_config.Path.JSON_TAG_BLURBS)

    @staticmethod
    def attempt_application(job: Job) -> str:
        job.attempted = True
        job.access_date = datetime.now().date()
        string = 'Attempting application for {0} with {1} at {2}'.format(job.title, job.company, job.location)
        print(string)
        return string

    @staticmethod
    def successful_application(job: Job, dry_run=False) -> str:
        if not dry_run:
            job.applied = True
        string = 'Successfully applied to {0} with {1} at {2}'.format(job.title, job.company, job.location)
        print(string)
        return string

    @staticmethod
    def failed_application(job: Job) -> str:
        string = 'Failed to apply to {0} with {1} at {2} because: {3}'.format(job.title, job.company, job.location, job.error)
        print(string)
        return string

    @staticmethod
    def _create_tables():
        # Create table if not exists
        Job.create_table(fail_silently=True)
        Question.create_table(fail_silently=True)
        Person.create_table(fail_silently=True)

    def shut_down(self):
        self.driver.close()

