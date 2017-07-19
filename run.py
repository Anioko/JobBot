import argparse
from enum import Enum

from Bot.AngelBot import AngelBot
from Bot.Indeed.IndeedBot import IndeedRobot
from userconfig import UserConfig

class JobBot(Enum):
    IndeedBot = 1
    AngelBot = 2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run JobBot')
    parser.add_argument('option', type=int, help="Pick JobBot, by typing it's option number")

    unformatted_display_query = "Bot being initialized with this query:\n\n {0}"

    args = parser.parse_args()
    if args.option == JobBot.IndeedBot.value:
        q1 = '((intern OR co-op) AND ' \
             '(software OR develop OR engineer OR mechanical OR mechatronics ' \
             'OR programming OR android OR ios OR technical OR qa OR testing OR automation)) ' \
             '-"marketing" -"human resources" -"hr" -unpaid -volunteer -"labor" -"labour" -secretary ' \
             '-receptionist -"assistant" -clerk -instructor -coordinator -tutor -cook -operator -manager -accountant ' \
             '-senior -director -"film" -"social worker" -teacher -designer -psychologist -"architect" ' \
             '-optician -optician -"RN" -"accounting" -"mechanic" -"Producer" -"Counsellor" -"Representative" ' \
             '-"Accounts Payable" -"plumber"'

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

        print(unformatted_display_query.format(q1))

        bot = IndeedRobot(UserConfig())
        bot.search_with_api(params=params)
        bot.login()
        bot.apply_jobs()
        bot.shut_down()

    elif args.option == JobBot.AngelBot.value:
        query_parameters = {"types": "internship",
                            "roles": [
                                "Software Engineer"
                                ],
                            "last_active" : "30",
                            "excluded_keywords": ["unpaid"]
                            }
        print(unformatted_display_query.format(query_parameters))

        bot = AngelBot(UserConfig())
        bot.login()
        #bot.gather(query_parameters)
        bot.apply()
        bot.shut_down()

    else:
        print('Pick one of these options:')
        for bot in JobBot:
            print('{0} : {1}'.format(bot.value, bot.name))

