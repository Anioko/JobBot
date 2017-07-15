import peewee
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium import webdriver, common
from helpers import sleep_after_function
from constants import HTML
from models import Job, Question
from Bot.Robot import Robot
from Bot.constants import IndeedConstants, RobotConstants
from collections import namedtuple
from typing import List, Optional
from indeed import IndeedClient
from datetime import datetime

QuestionLabelElement = namedtuple('QuestionLabelElement', 'label element')


class IndeedRobot(Robot):
    def __init__(self, user_config, dry_run=False, reload_tags_blurbs=True):
        super().__init__(user_config, dry_run=dry_run, reload_tags_blurbs=reload_tags_blurbs)

    def search_with_api(self, params: dict):
        client = IndeedClient(publisher=self.user_config.INDEED_API_KEY)
        search_response = client.search(**params)

        total_number_hits = search_response['totalResults']
        num_loops = int(total_number_hits / IndeedConstants.MAX_NUM_RESULTS_PER_REQUEST)
        start = 0
        print('Total number of hits: {0}'.format(total_number_hits))
        count_jobs_added = 0
        for i in range(0, num_loops):
            # We can get around MAX_NUM_RESULTS_PER_REQUEST by increasing our start location on each loop!
            params['start'] = start
            search_response = client.search(**params)
            job_results = search_response['results']
            for job_result in job_results:
                if job_result['indeedApply']:
                    try:
                        parsed_date = datetime.strptime(job_result['date'], '%a, %d %b %Y %H:%M:%S %Z')
                        Job.create(
                            job_key=job_result['jobkey'],
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
                        count_jobs_added += 1
                    except peewee.IntegrityError as e:
                        pass
            start += IndeedConstants.MAX_NUM_RESULTS_PER_REQUEST
        print('Added {0} new jobs'.format(count_jobs_added))

    def apply_jobs(self):
        count_applied = 0

        jobs = Job\
            .select()\
            .where((Job.applied == False) & (Job.good_fit == True) & (Job.access_date >> None))\
            .order_by(Job.posted_date.desc())
        for job in jobs:
            if count_applied > RobotConstants.MAX_COUNT_APPLIED_JOBS:
                print('Max job apply limit reached')
                break

            self._apply_to_single_job(job)
            count_applied += 1

    @sleep_after_function(RobotConstants.WAIT_MEDIUM)
    def _apply_to_single_job(self, job: Job):
        """
        Assuming you are on a job page, presses the apply button and switches to the application
        IFrame. If everything is working properly it call fill_application.
        Lastly, it saves any changes made to the job table
        :param job:
        :return:
        """
        # TODO: Add assert to ensure you are on job page
        self.attempt_application(job)
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

                self.fill_application(job)

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

    def fill_application(self, job: Job):
        def remove_multiple_attachments(q_el_inputs: List[FirefoxWebElement]):
            new_el_inputs = []
            for i in range(0, len(q_el_inputs)):
                current_id = q_el_inputs[i].get_attribute('id')
                if 'multattach' not in current_id:
                    new_el_inputs.append(q_el_inputs[i])
            return new_el_inputs

        def add_questions_to_database(list_qle: List[QuestionLabelElement]):
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

        def answer_questions(list_qle: List[QuestionLabelElement]):
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
                            if qle.element.get_attribute(HTML.Attributes.TYPE) == HTML.InputTypes.RADIO:
                                radio_name = qle.element.get_attribute(HTML.Attributes.NAME)
                                radio_button_xpath = IndeedConstants.compute_xpath_radio_button(q_answer, radio_name)
                                self.driver.find_element_by_xpath(radio_button_xpath).click()
                            else:
                                try:
                                    qle.element.send_keys(q_answer)
                                except Exception as e:
                                    job.error = e
                                    return False

                            remove_labels.add(qle.label)
                        except common.exceptions.ElementNotInteractableException:
                            q_not_visible = True

                # All questions answered!
                if len(list_qle) == 0:
                    return True
                # Stuck on a question with no answer
                elif unable_to_answer:
                    if job.message is None:
                        job.error = RobotConstants.String.NOT_ENOUGH_KEYWORD_MATCHES
                        job.good_fit = False
                    else:
                        job.error = RobotConstants.String.UNABLE_TO_ANSWER
                    break
                # Remove answered questions
                else:
                    list_qle = [qle for qle in list_qle if qle.label not in remove_labels]
                    remove_labels.clear()
                    if q_not_visible:
                        cont_elements = self.driver.find_elements_by_xpath(IndeedConstants.XPATH_BUTTON_CONT)
                        for j in range(0, len(cont_elements)):
                            try:
                                cont_elements[j].click()
                                break
                            except common.exceptions.ElementNotInteractableException as e:
                                pass
            return False

        q_element_labels = self.driver.find_elements_by_xpath(IndeedConstants.XPATH_ALL_QUESTION_LABELS)
        q_element_inputs = self.driver.find_elements_by_xpath(IndeedConstants.XPATH_ALL_QUESTION_INPUTS)
        # Make grouped radio buttons into only one element, using the name attribute
        q_element_inputs = remove_grouped_elements_by_attribute(q_element_inputs, 'name')
        # TODO: Eventually add labels for multi-attach and attach transcripts
        q_element_inputs = remove_multiple_attachments(q_element_inputs)
        app_success = False
        if len(q_element_labels) == len(q_element_inputs):
            list_question_label_element = []
            for i in range(0, len(q_element_labels)):
                formatted_label = q_element_labels[i].get_attribute(HTML.Attributes.INNER_TEXT).lower().strip()
                list_question_label_element.append(
                    QuestionLabelElement(
                        label=formatted_label,
                        element=q_element_inputs[i]
                    )
                )
            add_questions_to_database(list_question_label_element)

            if answer_questions(list_question_label_element):
                if not self.DRY_RUN:
                    self.driver.find_element_by_xpath(IndeedConstants.XPATH_BUTTON_APPLY).click()
                self.successful_application(job, dry_run=self.DRY_RUN)
                app_success = True
        else:
            job.error = RobotConstants.String.QUESTION_LABELS_AND_INPUTS_MISMATCH

        if not app_success:
            self.failed_application(job)

        return


def remove_grouped_elements_by_attribute(html_elements, attribute):
    copy_elements = list(html_elements)
    previous_attribute = ''
    for i in range(len(copy_elements) - 1, -1, -1):
        current_element = copy_elements[i]
        current_attribute = current_element.get_attribute(attribute)
        if previous_attribute == current_attribute:
            copy_elements.pop(i + 1)
        previous_attribute = current_attribute

    return copy_elements


if __name__ == "__main__":
    Question.drop_table()
