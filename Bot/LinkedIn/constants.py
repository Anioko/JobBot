import re

from Shared.helpers import Const
from Shared.models import Person


class LinkedInConstant(Const):
    WEBSITE_NAME = 'LinkedIn'

    class URL(Const):
        HOST = r'http://www.linkedin.com'
        LOGIN = r'https://www.linkedin.com/uas/login'
        SEARCH_PATH = r'/search/results/people/'

    class Name(Const):
        LOGIN_EMAIL = 'session_key'
        LOGIN_PASSWORD = 'session_password'

    class XPath(Const):
        NEWS_FEED = "//div[@class='feed-s-update__scroll']"
        SEARCH_RESULTS_LIST = "//ul[contains(@class,'results-list')]"
        NEXT_BUTTON = "//button[@class='next']"

        @staticmethod
        def find_link(link) -> str:
            return "//a[@href='{0}']".format(link)

    class Class(Const):
        SEARCH_RESULT = 'search-result'

        ACTOR_NAME = 'actor-name'
        ACTOR_TITLE = 'subline-level-1'
        ACTOR_POSITION = 'search-result__snippets'
        ACTOR_LINK = 'search-result__result-link'
        ACTOR_LOCATION = 'subline-level-2'

    class Regex(Const):
        position_string = re.compile(r"(.*)\sat\s(.*)")

    class String(Const):
        @staticmethod
        def person_visited(person: Person):
            print('Visited {0} : {1}'.format(person.name, person.title))

    class Constraint(Const):
        MAX_VISITS = 50

    class WaitTime(Const):
        LOGIN = 10
        SEARCH = 10
        VISIT = 15
        VIEW = 10
