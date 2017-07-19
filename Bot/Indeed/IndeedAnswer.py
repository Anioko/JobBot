from typing import Dict, List
from enum import Enum

from selenium.webdriver.common.by import By
from selenium import common
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.support.ui import Select
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
        NOT_VISIBLE = 2
        CANNOT_ANSWER = 3

    def __init__(self, ab_builder: ApplicationBuilder, user_config: UserConfig):
        self.ab_builder = ab_builder
        self.user_config = user_config

    def answer_all_questions(self, driver: webdriver.Chrome, job: Job, dict_qle: Dict[str, QuestionLabelElements]):
        # Initialize
        names = list(dict_qle.keys())
        i = 0
        name = names[i]
        state = self.AnswerState.CONTINUE
        list_continues: List[FirefoxWebElement] = driver.find_elements(By.XPATH, IndeedConstants.XPath.BUTTON_CONT)

        while True:
            qle = dict_qle[name]
            state = self._answer_question(driver, job, qle)
            if state == self.AnswerState.CANNOT_ANSWER:
                job.error = RobotConstants.String.UNABLE_TO_ANSWER
                return False

            if state == self.AnswerState.NOT_VISIBLE:
                for element_continue in list_continues:
                    try:
                        element_continue.click()
                        break
                    except common.exceptions.ElementNotVisibleException as e:
                        pass
                    except common.exceptions.NoSuchElementException as e:
                        job.error = str(e)
                        return False

            else:
                if i == len(names) - 1:
                    try:
                        driver.find_element(By.XPATH, IndeedConstants.XPath.BUTTON_APPLY).click()
                        return True
                    except common.exceptions.NoSuchElementException as e:
                        job.error = str(e)
                        return False
                    except common.exceptions.ElementNotVisibleException as e:
                        # TODO: Figure out why this happens
                        driver.find_element(By.XPATH, IndeedConstants.XPath.BUTTON_CONT).click()

                i += 1
                name = names[i]

        return False

    def _answer_question(self, driver: webdriver.Chrome, job: Job, qle: QuestionLabelElements):
        # Question should already be in database at this point with updated answer hopefully
        qle.question = Question.get(Question.name == qle.question.name)

        if qle.question.question_type == ABCs.QuestionTypes.MESSAGE:
            return self._answer_message(driver, job, qle)

        elif qle.question.secondary_input_type == HTMLConstants.InputTypes.RADIO:
            return self._answer_radio_or_checkbox(driver, job, qle, is_checkbox=False)

        elif qle.question.secondary_input_type == HTMLConstants.InputTypes.CHECK_BOX:
            return self._answer_radio_or_checkbox(driver, job, qle, is_checkbox=True)

        elif qle.question.input_type == HTMLConstants.TagType.SELECT:
            return self._answer_select(driver, job, qle)

        else:
            if qle.question.answer is None:
                if qle.question.question_type == ABCs.QuestionTypes.ADDITONAL_ATTACHMENTS:
                    return self.AnswerState.CONTINUE
                else:
                    job.error = RobotConstants.String.UNABLE_TO_ANSWER
            else:
                return self._answer_text(driver, job, qle)

        return self.AnswerState.CANNOT_ANSWER

    def _answer_message(self, driver: webdriver.Chrome, job: Job, qle: QuestionLabelElements) -> Enum:
        message = self.ab_builder.generate_message(job.description, job.company)
        if message is not None:
            try:
                driver.find_element(By.NAME, qle.question.name).send_keys(message)
                job.message = message
                return self.AnswerState.CONTINUE

            except common.exceptions.ElementNotVisibleException as e:
                return self.AnswerState.NOT_VISIBLE

            except common.exceptions.NoSuchElementException as e:
                job.error = str(e)
            return self.AnswerState.CANNOT_ANSWER

        else:
            job.error = RobotConstants.String.NOT_ENOUGH_KEYWORD_MATCHES
            return self.AnswerState.CANNOT_ANSWER

    def _answer_text(self, driver: webdriver.Chrome, job: Job, qle: QuestionLabelElements) -> Enum:
        try:
            element = driver.find_element(By.NAME, qle.question.name)
            element.clear()
            element.send_keys(qle.question.answer)
            return self.AnswerState.CONTINUE

        except common.exceptions.ElementNotVisibleException as e:
            return self.AnswerState.NOT_VISIBLE

        except common.exceptions.NoSuchElementException as e:
            job.error = str(e)

        except common.exceptions.InvalidElementStateException as e:
            return self.AnswerState.NOT_VISIBLE

        return self.AnswerState.CANNOT_ANSWER

    def _answer_radio_or_checkbox(self, driver: webdriver.Chrome, job: Job, qle: QuestionLabelElements,
                                  is_checkbox: bool) -> Enum:
        if is_checkbox:
            if qle.question.answer is not None:
                answers = qle.question.answer.split(',')
                values = [answer.strip() for answer in answers]
                checkbox_name = qle.element_list[0].get_attribute(HTMLConstants.Attributes.NAME)
                for value in values:
                    try:
                        xpath_checkbox_button = IndeedConstants.XPath.compute_xpath_radio_checkbox_button(
                            checkbox_name, value
                        )
                        driver.find_element(By.XPATH, xpath_checkbox_button).click()

                    except common.exceptions.ElementNotVisibleException as e:
                        return self.AnswerState.NOT_VISIBLE

                    except common.exceptions.NoSuchElementException as e:
                        job.error = str(e)
                        return self.AnswerState.CANNOT_ANSWER

                return self.AnswerState.CONTINUE

        else:
            question_answer = qle.question.answer
            radio_name = qle.element_list[0].get_attribute(HTMLConstants.Attributes.NAME)
            if question_answer is not None:
                try:
                    xpath_radio_button = IndeedConstants.XPath.compute_xpath_radio_checkbox_button(
                        radio_name, question_answer
                    )
                    driver.find_element(By.XPATH, xpath_radio_button).click()
                    return self.AnswerState.CONTINUE

                except common.exceptions.ElementNotVisibleException as e:
                    return self.AnswerState.NOT_VISIBLE

                except common.exceptions.NoSuchElementException as e:
                    job.error = str(e)

        return self.AnswerState.CANNOT_ANSWER

    def _answer_select(self, driver: webdriver.Chrome, job: Job, qle: QuestionLabelElements) -> Enum:
        select_name = qle.element_list[0].get_attribute(HTMLConstants.Attributes.NAME)
        try:
            select = Select(driver.find_element(By.NAME, select_name))
            if qle.question.secondary_input_type == HTMLConstants.InputTypes.SELECT_ONE:
                select.select_by_value(qle.question.answer)
            else:
                raise NotImplementedError
            return self.AnswerState.CONTINUE

        except common.exceptions.ElementNotVisibleException as e:
            return self.AnswerState.NOT_VISIBLE

        except common.exceptions.NoSuchElementException as e:
            job.error = str(e)

        return self.AnswerState.CANNOT_ANSWER


#TODO: This pattern is very common, perhaps reduce with method that takes function and parameters as argument
'''
try:
    xpath_radio_button = IndeedConstants.XPath.compute_xpath_radio_button(
        radio_name, question_answer
    )
    driver.find_element(By.XPATH, xpath_radio_button).click()
    return self.AnswerState.CONTINUE

except common.exceptions.ElementNotInteractableException as e:
    return self.AnswerState.CANNOT_INTERACT

except common.exceptions.ElementNotVisibleException as e:
    job.error = str(e)
'''