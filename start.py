import time
from urllib.parse import urlencode

import peewee
from bs4 import BeautifulSoup
from selenium import webdriver, common

from constants import Const
from jobdatabase import Job, databaseSetup, databaseTearDown
from userconfig import UserConfig


class BotConfig(Const):
    DELTA_RAND = .100
    WAIT_LONG = 5
    WAIT_MEDIUM = 3
    WAIT_SHORT = 1


class IndeedConfig(Const):
    URL_LOGIN = r'https://secure.indeed.com/account/login?service=my&hl=en_CA&co=CA&continue=https%3A%2F%2Fwww.indeed.ca%2F'
    ID_ELEMENT_LOGIN_EMAIL = r'signin_email'
    ID_ELEMENT_LOGIN_PASSWORD = r'signin_password'
    URL_BASE = r'https://www.indeed.ca/'
    URL_SEARCH = URL_BASE + r'jobs?'

    # Advanced search query
    SEARCH_PARAMETERS = {
        'as_any': 'software+developer+engineer+mechanical+mechatronics+computer+program',
        'jt': 'internship',
        'limit': 50,
        'psf': 'advsrch',
        'radius': 100,
        'fromage': 'any'
    }

    class DIV_JOB(Const):
        CLASSES = ['row', 'result']
        CLASS_JOB_LINK = 'jobtitle'
        EASY_APPLY = 'Easily apply'
        CLASS_SPONSERED = 'sponsoredGray'

    XPATH_NEXT_SPAN = r"//div[contains(@class, 'pagination')]//span[contains(text(), 'Next')]"


class IndeedBot(object):
    def __init__(self):
        self.driver = webdriver.Firefox()

    def login(self):
        self.driver.get(IndeedConfig.URL_LOGIN)
        elEmail = self.driver.find_element_by_xpath("//*[@id='{0}']".format(IndeedConfig.ID_ELEMENT_LOGIN_EMAIL))
        elPassword = self.driver.find_element_by_xpath("//*[@id='{0}']".format(IndeedConfig.ID_ELEMENT_LOGIN_PASSWORD))
        elEmail.send_keys(UserConfig.EMAIL)
        elPassword.send_keys(UserConfig.PASSWORD)
        elEmail.submit()

        while (self.driver.current_url != IndeedConfig.URL_BASE):
            time.sleep(BotConfig.DELTA_RAND)

    def searchJobs(self):
        # Apparently the difference between %2B and + matters in the search query
        urlArgs = urlencode(IndeedConfig.SEARCH_PARAMETERS).replace('%2B', '+')
        searchURL = IndeedConfig.URL_SEARCH + urlArgs
        self.driver.get(searchURL)

        while True:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            jobResultsSoup = soup.find_all('div', class_=IndeedConfig.DIV_JOB.CLASSES)

            self.storeJobs(jobResultsSoup)

            try:
                elNext = self.driver.find_element_by_xpath(IndeedConfig.XPATH_NEXT_SPAN)
                elNext.click()

            except common.exceptions.NoSuchElementException:
                print('Next button not found.\nNo more search results')
                break

    def storeJobs(self, jobResultsSoup):
        countNew = 0
        countSeen = 0

        # Iterated through results and save to database
        for jobTag in jobResultsSoup:
            if IndeedConfig.DIV_JOB.EASY_APPLY in jobTag.text:
                if len(jobTag.find_all('span', class_=IndeedConfig.DIV_JOB.CLASS_SPONSERED)) != 0:
                    jobTitleSoup = jobTag.find_all('a', class_=IndeedConfig.DIV_JOB.CLASS_JOB_LINK)[0]
                    jobLink = jobTitleSoup['href']
                else:
                    jobTitleSoup = jobTag.find_all('h2', class_=IndeedConfig.DIV_JOB.CLASS_JOB_LINK)[0]
                    jobLink = jobTitleSoup.a['href']

                jobTitle = jobTitleSoup.text.strip('\n')
                jobId = jobTag['id']
                try:
                    Job.insert(link_id=jobId, link=jobLink, title=jobTitle, easy_apply=True).execute()
                    countNew += 1
                except peewee.IntegrityError:
                    # print("{0} with id: {1}\tAlready in job table ".format(jobTitle, jobId))
                    countSeen += 1

        print("{0} new jobs stored\n{1} jobs already stored")

    def applyJobs(self):
        pass

    def _applySingleJob(selfs):
        pass

    def shutDown(self):
        self.driver.close()


databaseSetup()
bot = IndeedBot()
#bot.login()
bot.searchJobs()
bot.applyJobs()
bot.shutDown()
databaseTearDown()
