from helpers import Const
import re


class ApplicationBuilderConstants(Const):
    class TagBlurb(Const):
        KEY_BLURBS = 'blurbs'
        KEY_BLURB_TAGS = 'tags'
        KEY_BLURB_LONG_TEXT = 'longText'
        KEY_BLURB_SHORT_TEXT = 'shortText'
        KEY_BLURB_SCORE = 'score'

        TAG_START = 'start_tag'
        TAG_END = 'end_tag'
        TAG_END_ALT = 'end_tag_alt'

    COMPANY_PLACEHOLDER = r'{{COMPANY}}'
    BULLET_POINT = "-"

    # Possible websites
    INDEED = 'Indeed'

    class QuestionNeedle(Const):
        """
        Constants used to determine which question type the question is
        """
        RESUME = 'resume'
        MESSAGE = 'cover letter'
        LIST_LOCATION = ['located', 'are you in']
        EXPERIENCE = 'experience'
        LANGUAGE = 'do you speak'
        CERTIFICATION = 'do you have'
        LIST_EDUCATION = ['education', 'have you completed']
        LIST_CONTACT_INFO = ['name', 'email', 'phone number']

    # TODO: Use custom field in peewee
    class QuestionTypes(Const):
        RESUME = 'resume'
        MESSAGE = 'message'
        LOCATION = 'location'
        EXPERIENCE = 'experience'
        CERTIFICATION = 'certification'
        CONTACT_INFO = 'contact_info'
        LANGUAGE = 'language'
        EDUCATION = 'education'
