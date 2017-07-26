from Shared.helpers import Const
from enum import Enum


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
        NEEDLES_RESUME = ['resume']
        NEEDLES_MESSAGE = ['cover', 'letter']
        NEEDLES_LOCATION = ['located']
        NEEDLES_EXPERIENCE = ['experience']
        NEEDLES_LANGUAGE = ['speak']
        NEEDLES_CERTIFICATION = []
        NEEDLES_EDUCATION = ['education', 'completed']
        NEEDLES_EMAIL = ['email']
        NEEDLES_PERSONAL = ['name', 'phone', 'number']
        NEEDLES_RACE = ['race','ethni']
        NEEDLES_GENDER = ['gender','sex']

        NAME_MULTI_ATTACH = 'attachments'
        LENGTH_THRESHOLD_TOKENS = 20

    # TODO: Use custom field in peewee
    class QuestionTypes(Const):
        RESUME = 'resume'
        MESSAGE = 'message'
        EMAIL = 'email'
        LOCATION = 'location'
        EXPERIENCE = 'experience'
        CERTIFICATION = 'certification'
        PERSONAL = 'personal'
        LANGUAGE = 'language'
        EDUCATION = 'education'
        GENDER = 'gender'
        RACE = 'race'
        ADDITIONAL_ATTACHMENTS = 'attachments'
        LONG = 'long'

    class AnswerTypes(Enum):
        SINGLE = 1
        MULTIPLE = 2