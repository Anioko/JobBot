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
        KEYWORDS_RESUME = ['resume']
        KEYWORDS_MESSAGE = ['cover', 'letter']
        KEYWORDS_LOCATION = ['located']
        KEYWORDS_EXPERIENCE = ['experience']
        KEYWORDS_LANGUAGE = ['speak']
        KEYWORDS_CERTIFICATION = []
        KEYWORDS_EDUCATION = ['education', 'completed']
        KEYWORDS_EMAIL = ['email']
        KEYWORDS_PERSONAL = ['name', 'phone', 'number']
        KEYWORDS_RACE = ['race', 'ethni']
        KEYWORDS_GENDER = ['gender', 'sex']

        KEYWORDS_OPTIONAL = ['optional']

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