from helpers import Const


class IndeedConstants(Const):
    WEBSITE_NAME = 'Indeed'

    # SEARCH STAGE
    class API(Const):
        DATE_FORMAT =  '%a, %d %b %Y %H:%M:%S %Z'
        MAX_NUM_RESULTS_PER_REQUEST = 25

    # APPLICATION STAGE
    class XPath(Const):
        APPLY_SPAN = r"//span[contains(@class, 'indeed-apply-button-label')]"
        BUTTON_CONT = r"//div[contains(@id,'continue-div')]//div//a"
        BUTTON_APPLY = r"//div[contains(@id,'apply-div')]//div//input"

        ALL_QUESTION_LABELS = r"//div[contains(@class, 'input-container')]//label"
        ALL_QUESTION_INPUTS = r"//div[contains(@class, 'input-container')]//input | " \
                                    r"//div[contains(@class, 'input-container')]//select | " \
                                    r"//div[contains(@class, 'input-container')]//textarea"

        @staticmethod
        def compute_xpath_radio_button(answer, radio_name):
            unformatted_xpath_radio_button = "//span[text()='{0}']/preceding-sibling::input[@name='{1}']"
            return unformatted_xpath_radio_button.format(answer, radio_name)

    class Id(Const):
        JOB_SUMMARY = 'job_summary'
        INPUT_APPLICANT_NAME = 'applicant.name'
        INPUT_APPLICANT_EMAIL = 'applicant.email'
        INPUT_APPLICANT_PHONE = 'applicant.phoneNumber'
        BUTTON_RESUME = 'resume'
        INPUT_COVER_LETTER = 'applicant.applicationMessage'
