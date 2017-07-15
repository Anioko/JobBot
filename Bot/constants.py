from helpers import Const


class RobotConstants(Const):
    WAIT_IMPLICIT = 2
    WAIT_DELTA = .100
    WAIT_LONG = 15
    WAIT_MEDIUM = 7
    WAIT_SHORT = 2
    MAX_COUNT_APPLIED_JOBS = 100

    class String(Const):
        UNABLE_TO_ANSWER = 'Unable to answer all questions'
        NOT_ENOUGH_KEYWORD_MATCHES = 'Not enough keyword matches in the description'
        QUESTION_LABELS_AND_INPUTS_MISMATCH = 'The number of labels and question input elements do not match'


class IndeedConstants(Const):
    WEBSITE_NAME = 'Indeed'

    # SEARCH STAGE
    MAX_NUM_RESULTS_PER_REQUEST = 25

    # APPLICATION STAGE
    XPATH_APPLY_SPAN = r"//span[contains(@class, 'indeed-apply-button-label')]"
    ID_INPUT_APPLICANT_NAME = 'applicant.name'
    ID_INPUT_APPLICANT_EMAIL = 'applicant.email'
    ID_INPUT_APPLICANT_PHONE = 'applicant.phoneNumber'
    ID_BUTTON_RESUME = 'resume'
    ID_INPUT_COVER_LETTER = 'applicant.applicationMessage'
    XPATH_BUTTON_CONT = r"//div[contains(@id,'continue-div')]//div//a"
    XPATH_BUTTON_APPLY = r"//div[contains(@id,'apply-div')]//div//input"

    @staticmethod
    def compute_xpath_radio_button(answer, radio_name):
        unformatted_xpath_radio_button = "//span[text()='{0}']/preceding-sibling::input[@name='{1}']"
        return unformatted_xpath_radio_button.format(answer, radio_name)

    # If the continue button is present
    # TODO: How do we use 'or' here?
    XPATH_ALL_QUESTION_LABELS = r"//div[contains(@class, 'input-container')]//label"
    XPATH_ALL_QUESTION_INPUTS = r"//div[contains(@class, 'input-container')]//input | " \
                          r"//div[contains(@class, 'input-container')]//select | " \
                          r"//div[contains(@class, 'input-container')]//textarea"


class AngelConstants(Const):
    WEBSITE_NAME = 'Angel'

    class URL(Const):
        BASE = r'https://angel.co/'
        LOGIN = r'https://angel.co/login'
        JOBS = r'https://angel.co/jobs#find/f!'

    class Id(Const):
        LOGIN_EMAIL = 'user_email'
        LOGIN_PASSWORD = 'user_password'

    class XPath(Const):
        LOGGED_IN = r"//div[string(@data-user_id)]"
