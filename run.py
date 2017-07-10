from Bot.IndeedBot import IndeedBot
from userconfig import UserConfig


if __name__ == "__main__":
    bot = IndeedBot(UserConfig(), dry_run=False)

    params = {
        'q': '((intern OR co-op) AND '
             '(software OR develop OR engineer OR mechanical OR mechatronics OR programming OR android OR ios OR technical OR qa OR testing OR automation)) '
             '-marketing -human -hr -unpaid -volunteer -labor -labour -secretary -receptionist -assistant -clerk -instructor -coordinator -tutor -cook -operator -manager',
        'limit': '25',
        'fromage': '20',
        'language': 'en',
        'co': 'ca',
        'userip': "1.2.3.4",
        'useragent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    bot.search_with_api(params=params)
    bot.apply_jobs()
    bot.shut_down()