import time
from urllib.parse import urlencode

import peewee
from bs4 import BeautifulSoup
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from ApplicationBuilder import ApplicationBuilder
import helpers
from models import Job

# TODO: Once project is ready to release move configs!
class BotConfig(helpers.Const):
    WAIT_IMPLICIT = 3
    WAIT_DELTA = .100
    WAIT_LONG = 10
    WAIT_MEDIUM = 3
    WAIT_SHORT = 1
    MAX_COUNT_APPLIED_JOBS = 30


class IndeedConfig(helpers.Const):
    URL_LOGIN = r'https://secure.indeed.com/account/login?service=my&hl=en_CA&co=CA&continue=https%3A%2F%2Fwww.indeed.ca%2F'
    ID_INPUT_LOGIN_EMAIL = r'signin_email'
    ID_INPUT_LOGIN_PASSWORD = r'signin_password'
    URL_BASE = r'https://www.indeed.ca/'
    URL_SEARCH = URL_BASE + r'jobs?'

    # SEARCH STAGE

    # Advanced search query
    SEARCH_PARAMETERS = {
        'as_any': 'software+developer+engineer+mechanical+mechatronics+programming+android+ios+web+technical',
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


class IndeedBot(object):
    def __init__(self, userConfig, dryRun=False):
        self.DRY_RUN = dryRun
        self.userConfig = userConfig
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(BotConfig.WAIT_IMPLICIT)
        self.AB = ApplicationBuilder(userConfig)
        self.AB.resetAllTables()
        print('Initializing Tags and Blurbs from {0}'.format(userConfig.PATH_TAG_BLURBS))
        self.AB.readTagBlurbs(userConfig.PATH_TAG_BLURBS)

        # Create table if not exists
        Job.create_table(True)

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
        nextPageExists = False
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
            if (countApplied > BotConfig.MAX_COUNT_APPLIED_JOBS):
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
                self.fillApplication(job)
            except common.exceptions.NoSuchFrameException as e:
                job.error = str(e)
            # This second exception shouldn't really happen if the job is easy apply as described...
            except common.exceptions.NoSuchElementException as e:
                job.error = str(3)
        else:
            pass

        job.save()

    def fillApplication(self, job):
        job.attempted = True

        self.driver.find_element_by_id(IndeedConfig.ID_INPUT_APPLICANT_NAME).send_keys(self.userConfig.NAME)
        self.driver.find_element_by_id(IndeedConfig.ID_INPUT_APPLICANT_EMAIL).send_keys(self.userConfig.EMAIL)
        self.driver.find_element_by_id(IndeedConfig.ID_INPUT_APPLICANT_PHONE).send_keys(self.userConfig.PHONE)
        self.driver.find_element_by_id(IndeedConfig.ID_BUTTON_RESUME).send_keys(self.userConfig.PATH_SOFTWARE_RESUME)

        coverLetter = self.AB.generateMessage(job.description, job.company, containMinBlurbs=True)
        if coverLetter == None:
            print('Not a good fit for {0} with {1} at {2}'.format(job.title, job.company, job.location))
            job.good_fit = False

        else:
            self.driver.find_element_by_id(IndeedConfig.ID_INPUT_COVER_LETTER).send_keys(coverLetter)
            job.cover_letter = coverLetter
            if(self.DRY_RUN):
                print(coverLetter)

            # TODO: Handle case where there is additional information to fill out
            elif doesElementExist(self.driver, IndeedConfig.XPATH_BUTTON_CONT):
                job.error = "Additional information required (Cont Button)"
            else:
                try:
                    elApplyButton = self.driver.find_element_by_xpath(IndeedConfig.XPATH_BUTTON_APPLY)
                    if (not self.DRY_RUN):
                        elApplyButton.click()

                    job.applied = True
                    print('Applied to {0} with {1} at {2}'.format(job.title, job.company, job.location))

                except common.exceptions.NoSuchElementException as e:
                    job.error = str(e)

        job.save()
        return


    def resetTables(self):
        Job.drop_table()
        Job.create_table()

    def shutDown(self):
        self.driver.close()

def doesElementExist(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
        return True

    except common.exceptions.NoSuchElementException:
        return False