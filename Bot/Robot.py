from abc import ABC
from models import Job, Question
from selenium import webdriver
from Application.ApplicationBuilder import ApplicationBuilder
from Bot.constants import RobotConstants
from datetime import datetime
from userconfig import UserConfig


class Robot(ABC):
    def __init__(self, user_config: UserConfig, dry_run=False, reload_tags_blurbs=True):
        self.DRY_RUN = dry_run
        self.user_config = user_config
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(RobotConstants.WAIT_IMPLICIT)
        self.application_builder = ApplicationBuilder(user_config)

        self._create_tables()

        if reload_tags_blurbs:
            self.application_builder.reset_all_tables()
            print('Initializing Tags and Blurbs from {0}'.format(user_config.PATH_TAG_BLURBS))
            self.application_builder.read_tag_blurbs(user_config.PATH_TAG_BLURBS)

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

    def shut_down(self):
        self.driver.close()
