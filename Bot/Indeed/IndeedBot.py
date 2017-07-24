import time

import peewee
from indeed import IndeedClient
from selenium import common
from selenium.webdriver.common.by import By

from Bot.Indeed.IndeedAnswer import IndeedAnswer
from Bot.Indeed.IndeedParser import IndeedParser
from Bot.Indeed.constants import IndeedConstants
from Bot.Robot import Robot, RobotConstants
from Shared.helpers import sleep_after_function
from Shared.selenium_helpers import does_element_exist
from Shared.models import Job


class IndeedRobot(Robot):
    def __init__(self, user_config):
        super().__init__(user_config=user_config, driver=RobotConstants.Driver.CHROME)
        self.indeed_answer = IndeedAnswer(ab_builder=self.application_builder, user_config=user_config)

    def login(self):
        self.driver.get(IndeedConstants.URL_LOGIN)
        el_email = self.driver.find_element(By.ID, IndeedConstants.Id.LOGIN_EMAIL)
        el_email.send_keys(self.user_config.EMAIL)
        self.driver.find_element(By.ID, IndeedConstants.Id.LOGIN_PASSWORD).send_keys(self.user_config.PASSWORD)
        el_email.submit()

    def search_with_api(self, params: dict):
        client = IndeedClient(publisher=self.user_config.INDEED_API_KEY)
        search_response = client.search(**params)

        total_number_hits = search_response['totalResults']
        num_loops = int(total_number_hits / IndeedConstants.API.MAX_NUM_RESULTS_PER_REQUEST)
        counter_start = 0

        print('Total number of hits: {0}'.format(total_number_hits))
        count_jobs_added = 0

        for i in range(0, num_loops):
            # We can get around MAX_NUM_RESULTS_PER_REQUEST by increasing our start location on each loop!
            params['start'] = counter_start

            search_response = client.search(**params)
            list_jobs = IndeedParser.get_jobs_from_response(search_response)
            for job in list_jobs:
                try:
                    # TODO: This sucks, I'm just repeating myself...
                    Job.create(
                        key=job.key,
                        website=job.website,
                        link=job.link,
                        title=job.title,
                        company=job.company,
                        city=job.city,
                        state=job.state,
                        country=job.country,
                        location=job.location,
                        posted_date=job.posted_date,
                        expired=job.expired,
                        easy_apply=job.easy_apply
                    )
                    count_jobs_added += 1

                except peewee.IntegrityError as e:
                    # TODO: Can I write a custom exception that catches UNIQUE Errors but not others?
                    if 'UNIQUE' in str(e):
                        pass
                    else:
                        print(str(e))

            # Increment start
            counter_start += IndeedConstants.API.MAX_NUM_RESULTS_PER_REQUEST

        print('Added {0} new jobs'.format(count_jobs_added))

    def apply_jobs(self):
        count_attempts = 0

        # TODO: Add a parameter to decide between "attemped = false" or "applied = false"
        jobs = Job \
            .select() \
            .where(
            (Job.website == IndeedConstants.WEBSITE_NAME) &
            (Job.applied == False) &
            (Job.good_fit == True)) \
            .order_by(Job.posted_date.desc())

        for job in jobs:
            if count_attempts > RobotConstants.MAX_COUNT_APPLICATION_ATTEMPTS:
                print(RobotConstants.String.MAX_ATTEMPTS_REACHED)
                break

            self._apply_to_single_job(job)
            count_attempts += 1

    @sleep_after_function(RobotConstants.WAIT_MEDIUM)
    def _apply_to_single_job(self, job: Job):
        """
        Assuming you are on a job page, presses the apply button and switches to the application
        IFrame. If everything is working properly it call fill_application.
        Lastly, it saves any changes made to the job table
        :param job:
        :return:
        """
        self.attempt_application(job)
        if job.easy_apply:
            self.driver.get(job.link)

            if does_element_exist(self.driver, By.XPATH, IndeedConstants.XPath.TOS_POPUP):
                self.driver.find_element(By.XPATH, IndeedConstants.XPath.TOS_POPUP).click()

            try:
                # Fill job information
                job.description = self.driver.find_element(By.ID, IndeedConstants.Id.JOB_SUMMARY).text

                self.driver.find_element(By.XPATH, IndeedConstants.XPath.APPLY_SPAN).click()

                # Switch to application form IFRAME, notice that it is a nested IFRAME
                time.sleep(RobotConstants.WAIT_MEDIUM)
                self.driver.switch_to.frame(1)
                self.driver.switch_to.frame(0)

                self.fill_application(job)

            except common.exceptions.NoSuchElementException as e:
                job.error = str(e)
                job.expired = True
                print(e)

        else:
            pass

        job.save()

    def fill_application(self, job: Job):
        if does_element_exist(self.driver, By.XPATH, IndeedConstants.XPath.DIFFERENT_RESUME):
            self.driver.find_element(By.XPATH, IndeedConstants.XPath.DIFFERENT_RESUME).click()
        dict_qle = IndeedParser.get_dict_qle(self.driver)

        for key, qle in dict_qle.items():
            self.application_builder.add_question_to_database(qle.question)

        if self.indeed_answer.answer_all_questions(self.driver, job, dict_qle):
            self.successful_application(job, dry_run=self.user_config.Settings.IS_DRY_RUN)
        else:
            self.failed_application(job)

if __name__ == "__main__":
    pass


