from helpers import Const


class BotConstants(Const):
    WAIT_IMPLICIT = 2
    WAIT_DELTA = .100
    WAIT_LONG = 15
    WAIT_MEDIUM = 7
    WAIT_SHORT = 2
    MAX_COUNT_APPLIED_JOBS = 100


class IndeedConstants(Const):
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

    class DIV_JOB(Const):
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
