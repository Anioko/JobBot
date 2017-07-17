from datetime import datetime
from typing import Optional, List

from selenium import webdriver
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium import common
from selenium.webdriver.common.by import By

from Bot.Indeed.constants import IndeedConstants
from Bot.Indeed.IndeedBot import QuestionElementPair
from models import Job

class IndeedParser(object):
    def __init__(self):
        pass

    @staticmethod
    def get_jobs_from_response(response: dict) -> List[Job]:
        list_jobs = []
        job_results = response['results']
        for job_result in job_results:
            j = IndeedParser._get_job_from_result(job_result)
            if j is not None:
                list_jobs.append(j)
        return list_jobs

    @staticmethod
    def _get_job_from_result(job_result: dict) -> Optional[Job]:
        if job_result['indeedApply']:
            parsed_date = datetime.strptime(job_result['date'], IndeedConstants.API.DATE_FORMAT)
            job = Job(
                key=job_result['jobkey'],
                website=IndeedConstants.WEBSITE_NAME,
                link=job_result['url'],
                title=job_result['jobtitle'],
                company=job_result['company'],
                city=job_result['city'],
                state=job_result['state'],
                country=job_result['country'],
                location=job_result['formattedLocation'],
                posted_date=parsed_date.date(),
                expired=job_result['expired'],
                easy_apply=job_result['indeedApply']
            )
            return job
        return None

    @staticmethod
    def get_questions(driver: webdriver):
        q_element_labels = driver.find_elements(By.XPATH, IndeedConstants.XPath.ALL_QUESTION_LABELS)
        q_element_inputs = driver.find_elements(By.XPATH, IndeedConstants.XPath.ALL_QUESTION_INPUTS)

        list_questions = []
        for i, element_input in enumerate(q_element_inputs):



def group_radio_buttons_by_attribute(html_elements: List[FirefoxWebElement], attribute:str) -> List[FirefoxWebElement]:
    copy_elements = list(html_elements)
    previous_attribute = ''

    for i, current_element in enumerate(copy_elements):
        current_attribute = current_element.get_attribute(attribute)
        if previous_attribute == current_attribute:
            copy_elements.pop(i + 1)
        previous_attribute = current_attribute

    return copy_elements