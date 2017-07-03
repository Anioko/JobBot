from selenium import webdriver
from constants import Const
from userconfig import UserConfig
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import peewee
import time
from jobdatabase import Job, databaseSetup

class BotConfig(Const):
    DELTA_RAND = .100

class IndeedConfig(Const):
    URL_LOGIN = r'https://secure.indeed.com/account/login?service=my&hl=en_CA&co=CA&continue=https%3A%2F%2Fwww.indeed.ca%2F'
    ID_ELEMENT_LOGIN_EMAIL = r'signin_email'
    ID_ELEMENT_LOGIN_PASSWORD = r'signin_password'
    URL_BASE = r'https://www.indeed.ca/'
    URL_SEARCH = URL_BASE + r'jobs?'
    # Advanced search query
    SEARCH_PARAMETERS = {
        'as_any' : 'software+developer+engineer',
        'jt' : 'internship',
        'limit' : 50,
        'psf' : 'advsrch',
        'radius' : 100,
        'fromage' : 'any'
    }

    class DIV_JOB(Const):
        CLASSES = ['row', 'result']
        CLASS_JOB_LINK = 'jobtitle'
        EASY_APPLY = 'Easily apply'
        CLASS_SPONSERED = 'sponsoredGray'


class IndeedBot(object):
    def __init__(self):
        self.driver = webdriver.Firefox()

    def login(self):
        self.driver.get(IndeedConfig.URL_LOGIN)
        el_email = self.driver.find_element_by_xpath("//*[@id='{0}']".format(IndeedConfig.ID_ELEMENT_LOGIN_EMAIL))
        el_password = self.driver.find_element_by_xpath("//*[@id='{0}']".format(IndeedConfig.ID_ELEMENT_LOGIN_PASSWORD))
        el_email.send_keys(UserConfig.EMAIL)
        el_password.send_keys(UserConfig.PASSWORD)
        el_email.submit()

        while(self.driver.current_url != IndeedConfig.URL_BASE):
            time.sleep(BotConfig.DELTA_RAND)

    def search_jobs(self):
        # Apparently the difference between %2B and + matters in the search query
        urlArgs = urlencode(IndeedConfig.SEARCH_PARAMETERS).replace('%2B','+')
        searchURL = IndeedConfig.URL_SEARCH + urlArgs
        self.driver.get(searchURL)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        jobResultsSoup = soup.find_all('div', class_=IndeedConfig.DIV_JOB.CLASSES)

        for jobTag in jobResultsSoup:
            if IndeedConfig.DIV_JOB.EASY_APPLY in jobTag.text:
                if len(jobTag.find_all('span', class_=IndeedConfig.DIV_JOB.CLASS_SPONSERED)) != 0:
                    jobTitleSoup = jobTag.find_all('a', class_=IndeedConfig.DIV_JOB.CLASS_JOB_LINK)[0]
                    jobLink = jobTitleSoup['href']
                else:
                    jobTitleSoup = jobTag.find_all('h2', class_=IndeedConfig.DIV_JOB.CLASS_JOB_LINK)[0]
                    jobLink = jobTitleSoup.a['href']

                # TODO: Store these values
                jobTitle = jobTitleSoup.text.strip('\n')
                jobId = jobTag['id']
                try:
                    j = Job.create(link_id = jobId, link = jobLink, title = jobTitle, easy_apply = True)
                    j.save
                except peewee.IntegrityError:
                    print("{0} with id: {1}\tAlready in job table ".format(jobTitle, jobId))

    def shutDown(self):
        self.driver.close()

databaseSetup()
bot = IndeedBot()
#bot.login()
bot.search_jobs()
bot.shutDown()
