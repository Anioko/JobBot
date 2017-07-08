import time
from urllib.parse import urlencode
import peewee
from bs4 import BeautifulSoup
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Application.ApplicationBuilder import ApplicationBuilder
from helpers import sleepAfterFunction
from constants import HTML
from models import Job, Question
from Bot.constants import BotConstants, IndeedConstants

class IndeedBot(object):
    def __init__(self, user_config, dry_run=False, reload_tags_blurbs=True):
        self.DRY_RUN = dry_run
        self.user_config = user_config
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(BotConstants.WAIT_IMPLICIT)
        self.application_builder = ApplicationBuilder(user_config)

        self._createTables()

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

        while (self.driver.current_url != IndeedConstants.URL_BASE):
            time.sleep(BotConstants.WAIT_DELTA)

    def search_jobs(self):
        # Apparently the difference between %2B and + matters in the search query
        urlArgs = urlencode(IndeedConstants.SEARCH_PARAMETERS).replace('%2B', '+')
        searchURL = IndeedConstants.URL_SEARCH + urlArgs
        self.driver.get(searchURL)

        while True:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            jobResultsSoup = soup.find_all(HTML.TagType.DIV, class_=IndeedConstants.DIV_JOB.CLASSES)

            self.storeJobs(jobResultsSoup)

            nextPageExists = self._nextPage()
            if not nextPageExists:
                break

    @sleepAfterFunction(BotConstants.WAIT_MEDIUM)
    def _nextPage(self):
        try:
            self.driver.find_element_by_xpath(IndeedConstants.XPATH_BUTTON_NEXT_PAGE).click()
            # Right after pressing next a popup alert usually happens
            self._handle_popup()
            return True

        except common.exceptions.NoSuchElementException:
            print('Next button not found.\nNo more search results')
            return False

    def storeJobs(self, jobResultsSoup):
        countNew = 0
        countSeen = 0

        # Iterated through results and save to database
        for jobTag in jobResultsSoup:
            if IndeedConstants.DIV_JOB.EASY_APPLY in jobTag.text:
                if len(jobTag.find_all(HTML.TagType.SPAN, class_=IndeedConstants.DIV_JOB.CLASS_SPONSERED)) != 0:
                    jobTitleSoup = jobTag.find_all(HTML.TagType.ANCHOR, class_=IndeedConstants.DIV_JOB.CLASS_JOB_LINK)[0]
                    jobLink = IndeedConstants.URL_BASE + jobTitleSoup[HTML.Attributes.HREF]
                else:
                    jobTitleSoup = jobTag.find_all(HTML.TagType.H2, class_=IndeedConstants.DIV_JOB.CLASS_JOB_LINK)[0]
                    jobLink = IndeedConstants.URL_BASE + jobTitleSoup.a[HTML.Attributes.HREF]

                jobId = jobTag['id']
                # Format
                jobCompany = jobTag.find(HTML.TagType.SPAN, class_='company').text.strip()
                jobLocation = jobTag.find(HTML.TagType.SPAN, class_='location').text.strip()
                jobTitle = jobTitleSoup.text.strip()

                try:
                    job = Job.create(
                        link_id=jobId, link=jobLink, title=jobTitle, location=jobLocation,
                        company=jobCompany, easy_apply=True
                    )
                    job.save()
                    countNew += 1
                except peewee.IntegrityError:
                    # print("{0} with id: {1}\tAlready in job table ".format(jobTitle, jobId))
                    countSeen += 1

        print("{0} new jobs stored\n{1} jobs already stored".format(countNew, countSeen))

    def applyJobs(self):
        countApplied = 0

        jobs = Job.select().where(Job.applied == False)
        for job in jobs:
            if countApplied > BotConstants.MAX_COUNT_APPLIED_JOBS:
                print('Max job apply limit reached')
                break

            self._applySingleJob(job)
            countApplied += 1

    @sleepAfterFunction(BotConstants.WAIT_MEDIUM)
    def _applySingleJob(self, job):
        job.attempted = True
        if (job.easy_apply == True):
            try:
                self.driver.get(job.link)
                # Fill job information
                job.description = self.driver.find_element_by_id('job_summary').text

                elApply = self.driver.find_element_by_xpath(IndeedConstants.XPATH_APPLY_SPAN)
                elApply.click()

                # TODO: Find better way to do this!
                # Switch to application form IFRAME, notice that it is a nested IFRAME
                self.driver.switch_to.frame(1)
                self.driver.switch_to.frame(0)

                self.fillApplication(job, dryRun=self.DRY_RUN)

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

    def fillApplication(self, job, dryRun = False):
        def addQuestionsToDatabase(qElementLabels, qElements):
            qDict = {}
            for i in range(0, len(qLabels)):
                currentLabel = qLabels[i]
                currentElement = qElements[i]
                qObject = Question(
                    label=currentLabel,
                    website=IndeedConstants.URL_BASE,
                    input_type=currentElement.tag_name,
                    secondary_input_type=currentElement.get_attribute(HTML.Attributes.TYPE)
                )
                self.application_builder.add_question_to_database(qObject)

        def answerQuestions(qDict):
            """
            Returns True if all questions successfully answered and False otherwise
            :param qDict:
            :return:
            """
            removeSet = set()
            while True:
                qNotVisible = False
                for label, question in qDict.items():
                    qAnswer = self.application_builder.answer_question(question)
                    removeSet.add(question.label)

                # TODO: Fill in
                # All questions answered!
                if len(removeSet) == 0 and len(qDict) == 0:
                    break
                # No more questions can be answered
                elif len(removeSet) == 0:
                    # Press continue
                    if qNotVisible:
                        pass
                    # Give up for now...
                    else:
                        break
                # Remove answered questions
                else:
                    removeSet.clear()
            return False

        qElementLabels = self.driver.find_elements_by_xpath(IndeedConstants.XPATH_ALL_QUESTION_LABELS)
        qElementInputs = self.driver.find_elements_by_xpath(IndeedConstants.XPATH_ALL_QUESTION_INPUTS)
        assert(len(qElementLabels) == len(qElementInputs))
        qLabels = [qElementLabel.get_attribute('innerText') for qElementLabel in qElementLabels]


    @staticmethod
    def _createTables():
        # Create table if not exists
        Job.create_table(fail_silently=True)
        Question.create_table(fail_silently=True)

    def shutDown(self):
        self.driver.close()

def doesElementExist(driver, identifer, useXPath = True):
    """
    Function that checks if a element exists on the page
    :param driver: selenium.webdriver
    :param identifer: either a ID attribute or an xPath
    :param useXPath:
    :return:
    """
    try:
        if useXPath:
            driver.find_element_by_xpath(identifer)
        else:
            driver.find_element_by_id(identifer)
        return True

    except common.exceptions.NoSuchElementException:
        return False

if __name__ == "__main__":
    Question.drop_table()