from Bot.IndeedBot import IndeedBot
from userconfig import UserConfig


if __name__ == "__main__":
    bot = IndeedBot(UserConfig(), dry_run=False)

    params = {
        'q': "(co-op and (software or develop or engineer or mechanical or mechatronics "
             "or programming or android or ios or technical or qa)) -marketing",
        'limit': '25',
        'fromage': '',
        'language': 'en',
        'co': 'ca',
        'userip': "1.2.3.4",
        'useragent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    bot.search_with_api(params=params)
    bot.shut_down()