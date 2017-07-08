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
