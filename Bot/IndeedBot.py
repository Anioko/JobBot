import time
from urllib.parse import urlencode
import peewee
from bs4 import BeautifulSoup
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from Application.ApplicationBuilder import ApplicationBuilder
from helpers import sleep_after_function
from constants import HTML
from models import Job, Question
from Bot.constants import BotConstants, IndeedConstants
from collections import namedtuple

QuestionLabelElement = namedtuple('QuestionLabelElement','label element')


class IndeedBot(object):
    def __init__(self, user_config, dry_run=False, reload_tags_blurbs=True):
        self.DRY_RUN = dry_run
        self.user_config = user_config
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(BotConstants.WAIT_IMPLICIT)
        self.application_builder = ApplicationBuilder(user_config)

        self._create_tables()

        if reload_tags_blurbs:
            self.application_builder.resetAllTables()
            print('Initializing Tags and Blurbs from {0}'.format(user_config.PATH_TAG_BLURBS))
            self.application_builder.read_tag_blurbs(user_config.PATH_TAG_BLURBS)

    def _handle_popup(self):
        try:
            # Just to ensure that there is a popup
            self.driver.find_element_by_id(IndeedConstants.ID_POPUP)
            webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except common.exceptions.NoSuchElementException:
            pass

    def login(self):
        self.driver.get(IndeedConstants.URL_LOGIN)
        elEmail = self.driver.find_element_by_id(IndeedConstants.ID_INPUT_LOGIN_EMAIL)
        elEmail.send_keys(self.user_config.EMAIL)
        self.driver.find_element_by_id(IndeedConstants.ID_INPUT_LOGIN_PASSWORD).send_keys(self.user_config.PASSWORD)
        elEmail.submit()

        while self.driver.current_url != IndeedConstants.URL_BASE:
            time.sleep(BotConstants.WAIT_DELTA)

    def search_jobs(self):
        # Apparently the difference between %2B and + matters in the search query
        url_args = urlencode(IndeedConstants.SEARCH_PARAMETERS).replace('%2B', '+')
        search_url = IndeedConstants.URL_SEARCH + url_args
        self.driver.get(search_url)

        while True:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            job_results_soup = soup.find_all(HTML.TagType.DIV, class_=IndeedConstants.DIV_JOB.CLASSES)

            self.store_jobs(job_results_soup)

            next_page_exists = self._next_page()
            if not next_page_exists:
                break

    @sleep_after_function(BotConstants.WAIT_MEDIUM)
    def _next_page(self):
        try:
            self.driver.find_element_by_xpath(IndeedConstants.XPATH_BUTTON_NEXT_PAGE).click()
            # Right after pressing next a popup alert usually happens
            self._handle_popup()
            return True

        except common.exceptions.NoSuchElementException:
            print('Next button not found.\nNo more search results')
            return False

    def store_jobs(self, job_results_soup):
        count_new = 0
        count_seen = 0

        # Iterated through results and save to database
        for job_tag in job_results_soup:
            if IndeedConstants.DIV_JOB.EASY_APPLY in job_tag.text:
                if len(job_tag.find_all(HTML.TagType.SPAN, class_=IndeedConstants.DIV_JOB.CLASS_SPONSORED)) != 0:
                    job_title_soup = job_tag.find_all(HTML.TagType.ANCHOR, class_=IndeedConstants.DIV_JOB.CLASS_JOB_LINK)[0]
                    job_link = IndeedConstants.URL_BASE + job_title_soup[HTML.Attributes.HREF]
                else:
                    job_title_soup = job_tag.find_all(HTML.TagType.H2, class_=IndeedConstants.DIV_JOB.CLASS_JOB_LINK)[0]
                    job_link = IndeedConstants.URL_BASE + job_title_soup.a[HTML.Attributes.HREF]

                job_id = job_tag[HTML.Attributes.ID]
                # Format
                job_company = job_tag.find(HTML.TagType.SPAN, class_=IndeedConstants.DIV_JOB.CLASS_JOB_COMPANY).text.strip()
                job_location = job_tag.find(HTML.TagType.SPAN, class_=IndeedConstants.DIV_JOB.CLASS_JOB_LOCATION).text.strip()
                job_title = job_title_soup.text.strip()

                try:
                    job = Job.create(
                        link_id=job_id, link=job_link, title=job_title, location=job_location,
                        company=job_company, easy_apply=True
                    )
                    job.save()
                    count_new += 1
                except peewee.IntegrityError:
                    # print("{0} with id: {1}\tAlready in job table ".format(jobTitle, jobId))
                    count_seen += 1

        print("{0} new jobs stored\n{1} jobs already stored".format(count_new, count_seen))

    def apply_jobs(self):
        count_applied = 0

        jobs = Job.select().where(Job.applied == False)
        for job in jobs:
            if count_applied > BotConstants.MAX_COUNT_APPLIED_JOBS:
                print('Max job apply limit reached')
                break

            self._apply_to_single_job(job)
            count_applied += 1

    @sleep_after_function(BotConstants.WAIT_MEDIUM)
    def _apply_to_single_job(self, job):
        """
        Assuming you are on a job page, presses the apply button and switches to the application
        IFrame. If everything is working properly it call fill_application.
        Lastly, it saves any changes made to the job table
        :param job:
        :return:
        """
        # TODO: Add assert to ensure you are on job page
        print('Attempting application for {0} with {1} at {2}'.format(job.title, job.company, job.location))
        job.attempted = True
        if job.easy_apply:
            try:
                self.driver.get(job.link)
                # Fill job information
                job.description = self.driver.find_element_by_id('job_summary').text

                self.driver.find_element_by_xpath(IndeedConstants.XPATH_APPLY_SPAN).click()

                # TODO: Find better way to do this!
                # Switch to application form IFRAME, notice that it is a nested IFRAME
                self.driver.switch_to.frame(1)
                self.driver.switch_to.frame(0)

                self.fill_application(job, dry_run=self.DRY_RUN)

            except common.exceptions.NoSuchFrameException as e:
                job.error = str(e)
                print(e)

            # This second exception shouldn't really happen if the job is easy apply as described...
            except common.exceptions.NoSuchElementException as e:
                job.error = str(e)
                print(e)
        else:
            pass

        job.save()

    def fill_application(self, job, dry_run=False):
        def add_questions_to_database(list_qle):
            """
            Passes a question model object to application builder to add to database
            :param list_qle: List of QuestionLabelElement namedtupled objects
            :return:
            """
            for qle in list_qle:
                q_object = Question(
                    label=qle.label,
                    website=IndeedConstants.WEBSITE_NAME,
                    input_type=qle.element.tag_name,
                    secondary_input_type=qle.element.get_attribute(HTML.Attributes.TYPE)
                )
                self.application_builder.add_question_to_database(q_object)

        def answer_questions(list_qle):
            """
            Returns True if all questions successfully answered and False otherwise
            :param list_qle:
            :return:
            """
            remove_labels = set()
            while True:
                q_not_visible = False
                unable_to_answer = False
                for i in range(0, len(list_qle)):
                    qle = list_qle[i]
                    q_answer = self.application_builder.answer_question(job=job, question_label=qle.label)

                    if q_answer is None:
                        unable_to_answer = True
                    else:
                        try:
                            qle.element.send_keys(q_answer)
                            remove_labels.add(qle.label)
                        except common.exceptions.ElementNotInteractableException:
                            q_not_visible = True

                # All questions answered!
                if len(list_qle) == 0:
                    return True
                # Stuck on a question with no answer
                elif unable_to_answer:
                    break
                # Remove answered questions
                else:
                    list_qle = [qle for qle in list_qle if qle.label not in remove_labels]
                    remove_labels.clear()
                    if q_not_visible:
                        self.driver.find_element_by_xpath(IndeedConstants.XPATH_BUTTON_CONT).click()
            return False

        q_element_labels = self.driver.find_elements_by_xpath(IndeedConstants.XPATH_ALL_QUESTION_LABELS)
        q_element_inputs = self.driver.find_elements_by_xpath(IndeedConstants.XPATH_ALL_QUESTION_INPUTS)
        assert(len(q_element_labels) == len(q_element_inputs))
        list_question_label_element = []
        for i in range(0, len(q_element_labels)):
            formatted_label = q_element_labels[i].get_attribute(HTML.Attributes.INNER_TEXT).lower().strip()
            list_question_label_element.append(
                QuestionLabelElement(
                    label= formatted_label,
                    element=q_element_inputs[i]
                )
            )
        add_questions_to_database(list_question_label_element)
        if answer_questions(list_question_label_element):
            self.driver.find_element_by_xpath(IndeedConstants.XPATH_BUTTON_APPLY).click()
            job.applied = True
            print('Successfully applied to {0} with {1} at {2}'.format(job.title, job.company, job.location))

        return

    @staticmethod
    def _create_tables():
        # Create table if not exists
        Job.create_table(fail_silently=True)
        Question.create_table(fail_silently=True)

    def shut_down(self):
        self.driver.close()


def does_element_exist(driver, identifier, useXPath = True):
    """
    Function that checks if a element exists on the page
    :param driver: selenium.webdriver
    :param identifier: either a ID attribute or an xPath
    :param useXPath:
    :return:
    """
    try:
        if useXPath:
            driver.find_element_by_xpath(identifier)
        else:
            driver.find_element_by_id(identifier)
        return True

    except common.exceptions.NoSuchElementException:
        return False

if __name__ == "__main__":
    Question.drop_table()