from typing import Dict
from enum import Enum

from selenium.webdriver.common.by import By
from selenium import common
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium import webdriver

from models import Job, Question
from constants import HTMLConstants
from Bot.Robot import RobotConstants
from Bot.Indeed.constants import IndeedConstants
from Bot.Indeed.IndeedParser import QuestionLabelElements
from Application.constants import ApplicationBuilderConstants as ABCs
from Application.ApplicationBuilder import ApplicationBuilder
from userconfig import UserConfig
from helpers import does_element_exist


class IndeedAnswer(object):
    class AnswerState(Enum):
        CONTINUE = 1
        CANNOT_INTERACT = 2
        CANNOT_ANSWER = 3

    def __init__(self, ab_builder:ApplicationBuilder, user_config: UserConfig):
        self.ab_builder = ab_builder
        self.user_config = user_config

    def answer_all_questions(self,driver: webdriver.Chrome,job: Job, dict_qle:Dict[str, QuestionLabelElements]):
        # Initialize
        names = list(dict_qle.keys())
        i = 0
        name = names[i]
        state = self.AnswerState.CONTINUE

        while state != self.AnswerState.CANNOT_ANSWER:
            qle = dict_qle[name]
            state = self._answer_question(driver, job, qle)

            if state == self.AnswerState.CANNOT_INTERACT:
                # TODO: Press continue
                raise NotImplementedError

            else:
                if i == len(names) - 1:
                    try:
                        driver.find_element(By.XPATH, IndeedConstants.XPath.BUTTON_APPLY).click()
                        return True
                    except common.exceptions.NoSuchElementException as e:
                        job.error(str(e))
                        return False
                i += 1
                name = names[i]

        return False

    def _answer_question(self, driver: webdriver.Chrome,  job:Job, qle: QuestionLabelElements):
        # Question should already be in database at this point
        q: Question = Question.get(Question.name == qle.question.name)

        if q.question_type == ABCs.QuestionTypes.MESSAGE:
            message = self.ab_builder.generate_message(job.description, job.company)
            if message is not None:
                driver.find_element(By.NAME, q.name).send_keys(message)
                job.message = message
                return self.AnswerState.CONTINUE
            else:
                job.error = RobotConstants.String.NOT_ENOUGH_KEYWORD_MATCHES

        elif q.secondary_input_type == HTMLConstants.InputTypes.RADIO:
            return self.answer_radio(driver, job, qle)

        elif q.input_type == HTMLConstants.TagType.SELECT:
            raise NotImplementedError

        else:
            if q.answer is None:
                if q.question_type == ABCs.QuestionTypes.ADDITONAL_ATTACHMENTS:
                    return self.AnswerState.CONTINUE
                else:
                    job.error = RobotConstants.String.UNABLE_TO_ANSWER
            else:
                element = driver.find_element(By.NAME, q.name)
                element.clear()
                element.send_keys(q.answer)
                return self.AnswerState.CONTINUE

        return self.AnswerState.CANNOT_ANSWER

    def answer_radio(self, driver: webdriver.Chrome, job:Job, qle:QuestionLabelElements):
        if does_element_exist(driver, By.XPATH, IndeedConstants.XPath.PREFILLED_INPUTS):
            return self.AnswerState.CONTINUE
        else:
            question_answer = qle.question.answer
            input_radio_name = qle.element_list[0].get_attribute(HTMLConstants.Attributes.NAME)
            if question_answer is not None:
                try:
                    xpath_radio = IndeedConstants.XPath.compute_xpath_radio_button(question_answer, input_radio_name)
                    driver.find_element(By.XPATH, xpath_radio).click()
                    return self.AnswerState.CONTINUE

                except common.exceptions.NoSuchElementException as e:
                    job.error = str(e)
                    return self.AnswerState.CANNOT_ANSWER