from helpers import Const
import os


class UserConfig(Const):
    EMAIL = os.environ['EMAIL']
    PASSWORD = os.environ['PASSWORD']
    INDEED_API_KEY = os.environ['INDEED_API_KEY']

    PATH_TAG_BLURBS = r'blurbs.txt'

    MIN_BLURBS = 3
    DEFAULT_YEARS_EXPERIENCE = 1
