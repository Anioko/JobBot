import time
from urllib.parse import urlencode

import peewee
from bs4 import BeautifulSoup
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ApplicationBuilder import ApplicationBuilder
import helpers
from models import Job, Question

# TODO: Once project is ready to release move configs!
class BotConfig(helpers.Const):
    WAIT_IMPLICIT = 2
    WAIT_DELTA = .100
    WAIT_LONG = 15
    WAIT_MEDIUM = 7
    WAIT_SHORT = 2
    MAX_COUNT_APPLIED_JOBS = 100


class IndeedConfig(helpers.Const):
    URL_LOGIN = r'https://secure.indeed.com/account/login?service=my&hl=en_CA&co=CA&continue=https%3A%2F%2Fwww.indeed.ca%2F'
    ID_INPUT_LOGIN_EMAIL = r'signin_email'
    ID_INPUT_LOGIN_PASSWORD = r'signin_password'
    URL_BASE = r'https://www.indeed.ca/'
    URL_SEARCH = URL_BASE + r'jobs?'

    # SEARCH STAGE

    # Advanced search query
    SEARCH_PARAMETERS = {
        'as_any': 'software+develop+engineer+mechanical+mechatronics+programming+android+ios+technical+qa',
        'as_not': 'market',
        'jt': 'internship',
        'limit': 50,
        'psf': 'advsrch',
        'radius': 100,
        'fromage': 'any'
    }

    class DIV_JOB(helpers.Const):
        CLASSES = ['row', 'result']
        CLASS_JOB_LINK = 'jobtitle'
        EASY_APPLY = 'Easily apply'
        CLASS_SPONSERED = 'sponsoredGray'
        XPATH_COMPANY_NAME = r"//"

    XPATH_BUTTON_NEXT_PAGE = r"//div[contains(@class, 'pagination')]//span[contains(text(), 'Next')]"
    ID_POPUP = 'popover-foreground'

    # APPLICATION STAGE
    XPATH_APPLY_SPAN = r"//span[contains(@class, 'indeed-apply-button-label')]"
    ID_INPUT_APPLICANT_NAME = 'applicant.name'
    ID_INPUT_APPLICANT_EMAIL = 'applicant.email'
    ID_INPUT_APPLICANT_PHONE = 'applicant.phoneNumber'
    ID_BUTTON_RESUME = 'resume'
    ID_INPUT_COVER_LETTER = 'applicant.applicationMessage'
    XPATH_BUTTON_CONT = r"//div[contains(@id,'continue-div')]//div//a"
    XPATH_BUTTON_APPLY = r"//div[contains(@id,'apply-div')]//div//input"

    # If the continue button is present
    # TODO: How do we use 'or' here?
    XPATH_ALL_QUESTION_LABELS = r"//div[contains(@class, 'input-container')]//label"
    XPATH_ALL_QUESTION_INPUTS = r"//div[contains(@class, 'input-container')]//input | " \
                          r"//div[contains(@class, 'input-container')]//select | " \
                          r"//div[contains(@class, 'input-container')]//textarea"


class IndeedBot(object):
    def __init__(self, userConfig, dryRun=False, reloadTagsBlurbs=True):
        self.DRY_RUN = dryRun
        self.userConfig = userConfig
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(BotConfig.WAIT_IMPLICIT)
        self.AB = ApplicationBuilder(userConfig)

        self._createTables()

        if reloadTagsBlurbs:
            self.AB.resetAllTables()
            print('Initializing Tags and Blurbs from {0}'.format(userConfig.PATH_TAG_BLURBS))
            self.AB.readTagBlurbs(userConfig.PATH_TAG_BLURBS)

    def _handlePopup(self):
        try:
            # Just to ensure that there is a popup
            self.driver.find_element_by_id(IndeedConfig.ID_POPUP)
            webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except common.exceptions.NoSuchElementException:
            pass

    def login(self):
        self.driver.get(IndeedConfig.URL_LOGIN)
        elEmail = self.driver.find_element_by_id(IndeedConfig.ID_INPUT_LOGIN_EMAIL)
        elEmail.send_keys(self.userConfig.EMAIL)
        self.driver.find_element_by_id(IndeedConfig.ID_INPUT_LOGIN_PASSWORD).send_keys(self.userConfig.PASSWORD)
        elEmail.submit()

        while (self.driver.current_url != IndeedConfig.URL_BASE):
            time.sleep(BotConfig.WAIT_DELTA)

    def searchJobs(self):
        # Apparently the difference between %2B and + matters in the search query
        urlArgs = urlencode(IndeedConfig.SEARCH_PARAMETERS).replace('%2B', '+')
        searchURL = IndeedConfig.URL_SEARCH + urlArgs
        self.driver.get(searchURL)

        while True:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            jobResultsSoup = soup.find_all('div', class_=IndeedConfig.DIV_JOB.CLASSES)

            self.storeJobs(jobResultsSoup)

            nextPageExists = self._nextPage()
            if not nextPageExists:
                break

    @helpers.sleepAfterFunction(BotConfig.WAIT_MEDIUM)
    def _nextPage(self):
        try:
            self.driver.find_element_by_xpath(IndeedConfig.XPATH_BUTTON_NEXT_PAGE).click()
            # Right after pressing next a popup alert usually happens
            self._handlePopup()
            return True

        except common.exceptions.NoSuchElementException:
            print('Next button not found.\nNo more search results')
            return False

    def storeJobs(self, jobResultsSoup):
        countNew = 0
        countSeen = 0

        # Iterated through results and save to database
        for jobTag in jobResultsSoup:
            if IndeedConfig.DIV_JOB.EASY_APPLY in jobTag.text:
                if len(jobTag.find_all('span', class_=IndeedConfig.DIV_JOB.CLASS_SPONSERED)) != 0:
                    jobTitleSoup = jobTag.find_all('a', class_=IndeedConfig.DIV_JOB.CLASS_JOB_LINK)[0]
                    jobLink = IndeedConfig.URL_BASE + jobTitleSoup['href']
                else:
                    jobTitleSoup = jobTag.find_all('h2', class_=IndeedConfig.DIV_JOB.CLASS_JOB_LINK)[0]
                    jobLink = IndeedConfig.URL_BASE + jobTitleSoup.a['href']

                jobId = jobTag['id']
                # Format
                jobCompany = jobTag.find('span', class_='company').text.strip()
                jobLocation = jobTag.find('span', class_='location').text.strip()
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
            if countApplied > BotConfig.MAX_COUNT_APPLIED_JOBS:
                print('Max job apply limit reached')
                break

            self._applySingleJob(job)
            countApplied += 1

    @helpers.sleepAfterFunction(BotConfig.WAIT_MEDIUM)
    def _applySingleJob(self, job):
        job.attempted = True
        if (job.easy_apply == True):
            try:
                self.driver.get(job.link)
                # Fill job information
                job.description = self.driver.find_element_by_id('job_summary').text

                elApply = self.driver.find_element_by_xpath(IndeedConfig.XPATH_APPLY_SPAN)
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
        def attachResume(logError = False):
            try:
                # TODO: Eventually get resume from application builder
                self.driver.find_element_by_id(IndeedConfig.ID_BUTTON_RESUME).send_keys(self.userConfig.PATH_SOFTWARE_RESUME)
                return True
            except common.exceptions.NoSuchElementException as e:
                if logError:
                    job.error = str(e)
                return False

        def finalizeApplication(logError = False, dryRun = False):
            try:
                elApplyButton = self.driver.find_element_by_xpath(IndeedConfig.XPATH_BUTTON_APPLY)
                if not dryRun:
                    job.applied = True
                    elApplyButton.click()
                print('Successfully applied!')
                return True
            except common.exceptions.NoSuchElementException as e:
                if logError:
                    print(e)
                    job.error = str(e)
                return False

        print('Attempting application for {0} with {1} at {2}'.format(job.title, job.company, job.location))
        job.attempted = True

        # Wait for applicant name field to load, if it's not there somethings wrong
        if not doesElementExist(self.driver, IndeedConfig.ID_INPUT_APPLICANT_NAME, useXPath=False):
            job.error = "Applicant name field not found"
            return
        self.driver.find_element_by_id(IndeedConfig.ID_INPUT_APPLICANT_NAME).send_keys(self.userConfig.NAME)
        self.driver.find_element_by_id(IndeedConfig.ID_INPUT_APPLICANT_EMAIL).send_keys(self.userConfig.EMAIL)
        self.driver.find_element_by_id(IndeedConfig.ID_INPUT_APPLICANT_PHONE).send_keys(self.userConfig.PHONE)

        # FIRST CASE: No continue button - Easy Application
        # Attach resume and cover letter (if possible), click apply
        if not doesElementExist(self.driver, IndeedConfig.XPATH_BUTTON_CONT):
            # If you can't attach a resume someting is seriously wrong!
            if not attachResume(logError=True):
                return

            # Add cover letter
            if doesElementExist(self.driver, IndeedConfig.ID_INPUT_COVER_LETTER, useXPath=False):
                coverLetter = self.AB.generateMessage(job.description, job.company, containMinBlurbs=True)
                if coverLetter is None:
                    print('Not enough keyword matches')
                    job.good_fit = False
                else:
                    self.driver.find_element_by_id(IndeedConfig.ID_INPUT_COVER_LETTER).send_keys(coverLetter)
                    job.cover_letter = coverLetter
                    if dryRun:
                        print(coverLetter)
                    finalizeApplication(logError=True)

        # SECOND CASE: Continue button exists - We have to fill out additional information
        # Also resume can either be on the first page or not?
        else:
            # TODO: Fill this out
            # Get all question elements
            elementsQuestionLabels = self.driver.find_elements_by_xpath(IndeedConfig.XPATH_ALL_QUESTION_LABELS)
            elementsQuestionInputs = self.driver.find_elements_by_xpath(IndeedConfig.XPATH_ALL_QUESTION_INPUTS)
            assert(len(elementsQuestionLabels) == len(elementsQuestionInputs))
            allQuestionsAnswered = True
            for i in range(0, len(elementsQuestionLabels)):
                label = elementsQuestionLabels[i].get_attribute('innerText')
                questionElement = elementsQuestionInputs[i]
                try:
                    question = Question.create(label=label, website=IndeedConfig.URL_BASE, type='experience')
                    question.save()
                # The question is already in the database
                except peewee.IntegrityError as e:
                    question = Question.get(Question.label == label)
                    if len(question.answer) != 0:
                        questionElement.send_keys(question.answer)
                    else:
                        pass

            while not doesElementExist(self.driver, IndeedConfig.XPATH_BUTTON_APPLY):
                # Attempt to attach a resume
                break

        return

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