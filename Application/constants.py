from helpers import Const
import re


class ApplicationBuilderConstants(Const):
    """
    The two regex captures in this class determine how you should
    format your file that contains tags and blurbs
    """
    REGEX_TAGS_CAPTURE = re.compile(r"'''(.*?)'''", re.DOTALL)
    REGEX_BLURB_CAPTURE = re.compile(r'"""(.*?)"""', re.DOTALL)
    START_TAG = 'start_tag'
    END_TAG = 'end_tag'
    REPLACE_COMPANY_STRING = r'{COMPANY}'
    BULLET_POINT = "-"

    # Possible websites
    INDEED = 'Indeed'

    class QuestionNeedle(Const):
        """
        Constants used to determine which question type the question is
        """
        RESUME = 'resume'
        MESSAGE = 'cover letter'
        LOCATION = 'located'
        EXPERIENCE = 'experience'
        EDUCATION = 'education'
        LIST_CONTACT_INFO = ['name', 'email', 'phone number']

    # TODO: Use custom field in peewee
    class QuestionTypes(Const):
        RESUME = 'resume'
        MESSAGE = 'message'
        LOCATION = 'location'
        EXPERIENCE = 'experience'
        CONTACT_INFO = 'contact_info'
        EDUCATION = 'education'
