from helpers import Const


class IndeedConstants(Const):
    WEBSITE_NAME = 'Indeed'

    # LOGIN
    URL_LOGIN = r'https://secure.indeed.com/account/login'

    # SEARCH STAGE
    class API(Const):
        DATE_FORMAT =  '%a, %d %b %Y %H:%M:%S %Z'
        MAX_NUM_RESULTS_PER_REQUEST = 25

    # APPLICATION STAGE
    class XPath(Const):
        APPLY_SPAN = r"//span[contains(@class, 'indeed-apply-button-label')]"
        DIFFERENT_RESUME = r"//a[contains(text(),'Apply with a different resume?')]"

        BUTTON_CONT = r"//div[contains(@id,'continue-div')]//div//a"
        BUTTON_APPLY = r"//div[contains(@id,'apply-div')]//div//input"

        ALL_QUESTION_LABELS = r"//div[contains(@class, 'input-container')]//label"
        ALL_QUESTION_INPUTS = r"//div[contains(@class, 'input-container')]//input | " \
                                    r"//div[contains(@class, 'input-container')]//select | " \
                                    r"//div[contains(@class, 'input-container')]//textarea"

        PREFILLED_INPUTS = r"//div[contains(@class, 'input-container')]//input[@type='hidden']"

        @staticmethod
        def compute_xpath_radio_button(answer, radio_name):
            """
            The span right before the input element is it's label
            :param answer:
            :param radio_name:
            :return:
            """
            xpath = "//span[text()='{0}']/preceding-sibling::input[@name='{1}']"
            return xpath.format(answer, radio_name)

        @staticmethod
        def compute_xpath_input_name_of_label(label_for:str):
            """
            The label is above a div with class input and inside this div are the input elements
            ignoring the hidden input types
            :param label_for:
            :return:
            """
            xpath = "//label[@for='{0}']/following-sibling::div[contains(@class,'input')]//input[@type!='hidden'] |" \
                    "//label[@for='{0}']/following-sibling::div[contains(@class,'input')]//textarea"
            return xpath.format(label_for)

    class Id(Const):
        LOGIN_EMAIL = 'signin_email'
        LOGIN_PASSWORD = 'signin_password'
        JOB_SUMMARY = 'job_summary'
        INPUT_APPLICANT_NAME = 'applicant.name'
        INPUT_APPLICANT_EMAIL = 'applicant.email'
        INPUT_APPLICANT_PHONE = 'applicant.phoneNumber'
        BUTTON_RESUME = 'resume'
        INPUT_COVER_LETTER = 'applicant.applicationMessage'
