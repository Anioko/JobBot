import os

from Shared.helpers import Const


class UserConfig(Const):
    EMAIL = os.environ['EMAIL']
    PASSWORD = os.environ['PASSWORD']
    INDEED_API_KEY = os.environ['INDEED_API_KEY']
    DEFAULT_RESUME = os.environ['DEFAULT_RESUME']

    class Path(Const):
        JSON_TAG_BLURBS = r'blurbs.json'

    class Settings(Const):
        # Booleans
        USE_ALT_END_TAG = True
        USE_LONG_TEXT = False
        IS_DRY_RUN = False
        WILL_RELOAD_TAGS_AND_BLURBS = True

        MINIMUM_NUMBER_MATCHING_KEYWORDS = 1
        DEFAULT_EXPERIENCE = 2