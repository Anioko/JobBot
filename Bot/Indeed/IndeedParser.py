from collections import namedtuple, OrderedDict
from datetime import datetime
from typing import Optional, List, Dict

import nltk

from selenium import webdriver
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium import common
from selenium.webdriver.common.by import By

from constants import HTMLConstants
from Bot.Indeed.constants import IndeedConstants
from models import Job, Question, ModelConstants
from helpers import tokenize_text

class QuestionLabelElements(object):
    def __init__(self):
        self.question = Question()
        self.label = ''
        self.element_list = []

    def add_element(self, element):
        self.element_list.append(element)

    def compute_question(self):
        first_element:FirefoxWebElement = self.element_list[0]

        # TODO: Add additional infomation using list elements
        self.question = Question(
            name=first_element.get_attribute(HTMLConstants.Attributes.NAME),
            label=self.label,
            tokens=ModelConstants.DELIMITER.join(tokenize_text(self.label)),
            website=IndeedConstants.WEBSITE_NAME,
            input_type=first_element.tag_name,
            secondary_input_type=first_element.get_attribute(HTMLConstants.Attributes.TYPE)
        )
        if self.question.secondary_input_type == HTMLConstants.InputTypes.RADIO:
            raise NotImplementedError

        if self.question.input_type == HTMLConstants.TagType.SELECT:
            raise NotImplementedError

        return self.question


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
    def get_dict_qle(driver: webdriver) -> Dict[str, QuestionLabelElements]:
        q_element_labels: List[FirefoxWebElement] = driver.find_elements(By.XPATH, IndeedConstants.XPath.ALL_QUESTION_LABELS)
        q_element_inputs: List[FirefoxWebElement] = driver.find_elements(By.XPATH, IndeedConstants.XPath.ALL_QUESTION_INPUTS)

        dict_qle: Dict[str, QuestionLabelElements] = OrderedDict()
        for element_input in q_element_inputs:
            element_name = element_input.get_attribute(HTMLConstants.Attributes.NAME)

            if element_input.get_attribute('type') == HTMLConstants.InputTypes.HIDDEN:
                pass
            else:
                if dict_qle.get(element_name, None) is None:
                    qle = QuestionLabelElements()
                    qle.add_element(element_input)
                    qle.question.name = element_name
                    dict_qle[element_name] = qle
                else:
                    dict_qle[element_name].add_element(element_input)

        # Match Labels to Inputs
        for element_label in q_element_labels:
            label_for = element_label.get_attribute(HTMLConstants.Attributes.FOR)
            xpath_element_name = IndeedConstants.XPath.compute_xpath_input_name_of_label(label_for)
            element_name = driver.find_element(By.XPATH, xpath_element_name).get_attribute(HTMLConstants.Attributes.NAME)
            label_text = element_label.get_attribute(HTMLConstants.Attributes.INNER_TEXT)
            if dict_qle.get(element_name, None) is None:
                print('No input for label ' + label_text)
            else:
                dict_qle[element_name].label = label_text

        for key, qle in dict_qle.items():
            qle.compute_question()

        return dict_qle
