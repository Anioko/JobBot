from Shared.helpers import Const


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
        TOS_POPUP = r"//button[text()='I agree']"
        APPLY_SPAN = r"//span[contains(@class, 'indeed-apply-button-label')]"
        DIFFERENT_RESUME = r"//a[contains(text(),'Apply with a different resume?')]"

        BUTTON_CONT = r"//a[@href='#next']"
        BUTTON_APPLY = r"//div[contains(@id,'apply-div')]//div//input"

        ALL_QUESTION_LABELS = r"//div[contains(@class, 'input-container')]//label"
        ALL_QUESTION_INPUTS = r"//div[contains(@class, 'input-container')]//input | " \
                                    r"//div[contains(@class, 'input-container')]//select | " \
                                    r"//div[contains(@class, 'input-container')]//textarea"

        PREFILLED_INPUTS = r"//div[contains(@class, 'input-container')]//input[@type='hidden']"

        # Not really constants anymore, perhaps renaming is necessary...
        @staticmethod
        def compute_xpath_check_button(radio_name:str, answer:str) -> str:
            """
            :param radio_name:
            :param value:
            :return:
            """
            xpath = r"//div[@class='input']//span[text()='{1}']/preceding-sibling::input[1][@name='{0}']"
            return xpath.format(radio_name, answer)

        @staticmethod
        def compute_xpath_input_name_of_label(label_for:str) -> str:
            """
            The label is above a div with class input and inside this div are the input elements
            ignoring the hidden input types
            :param label_for:
            :return:
            """
            xpath = "//label[@for='{0}']/following-sibling::div[contains(@class,'input')]//input[@type!='hidden'] | " \
                    "//label[@for='{0}']/following-sibling::div[contains(@class,'input')]//textarea | " \
                    "//label[@for='{0}']/following-sibling::div[contains(@class,'input')]//select"
            return xpath.format(label_for)

        @staticmethod
        def compute_xpath_radio_span(radio_name:str) -> str:
            """
            xpath to find the span right beside the radio option input, basically the choice that the radio button represents
            :param radio_name:
            :return:
            """
            xpath = "//input[@name='{0}']/following-sibling::span"
            return xpath.format(radio_name)

        @staticmethod
        def compute_xpath_select_options(select_name: str) -> str:
            xpath = "//select[@name='{0}']//option"
            return xpath.format(select_name)

    class Id(Const):
        LOGIN_EMAIL = 'signin_email'
        LOGIN_PASSWORD = 'signin_password'
        JOB_SUMMARY = 'job_summary'
        INPUT_APPLICANT_NAME = 'applicant.name'
        INPUT_APPLICANT_EMAIL = 'applicant.email'
        INPUT_APPLICANT_PHONE = 'applicant.phoneNumber'
        BUTTON_RESUME = 'resume'
        INPUT_COVER_LETTER = 'applicant.applicationMessage'

    class Class(Const):
        HELP_BLOCK = 'help-block'
