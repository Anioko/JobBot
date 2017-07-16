import os

from Bot.IndeedBot import IndeedRobot
from Bot.AngelBot import AngelBot
from helpers import Const


class UserConfig(Const):
    EMAIL = os.environ['EMAIL']
    PASSWORD = os.environ['PASSWORD']
    INDEED_API_KEY = os.environ['INDEED_API_KEY']

    class Path(Const):
        TAG_BLURBS = r'blurbs.txt'

    class Settings(Const):
        # Booleans
        USE_ALT_END_TAG = True
        IS_DRY_RUN = True
        WILL_RELOAD_TAGS_AND_BLURBS = True

        MINIMUM_NUMBER_MATCHING_KEYWORDS = 3
        DEFAULT_EXPERIENCE = None


if __name__ == "__main__":
    INDEED = False
    if INDEED:
        bot = IndeedRobot(UserConfig(), dry_run=False)

        q1 = '((intern OR co-op) AND ' \
             '(software OR develop OR engineer OR mechanical OR mechatronics ' \
             'OR programming OR android OR ios OR technical OR qa OR testing OR automation)) ' \
             '-"marketing" -"human resources" -"hr" -unpaid -volunteer -"labor" -"labour" -secretary ' \
             '-receptionist -"assistant" -clerk -instructor -coordinator -tutor -cook -operator -manager -accountant' \
             '-senior -director -film -"social worker" -teacher -designer -psychologist'
        params = {
            'q': q1,
            'limit': '25',
            # 'jt':'internship',
            'fromage': '20',
            'language': 'en',
            'co': 'ca',
            'userip': "1.2.3.4",
            'useragent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        bot.search_with_api(params=params)
        bot.apply_jobs()
        bot.shut_down()
    else:
        bot = AngelBot(UserConfig(), dry_run=False)
        bot.login()
        query_parameters = {"types": "internship",
                            "roles": [
                                "Software Engineer"
                                ],
                            "last_active" : "30",
                            "excluded_keywords": ["unpaid"]
                            }
        #bot.gather(query_parameters)
        bot.apply()
        bot.shut_down()
