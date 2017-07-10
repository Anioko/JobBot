from Bot.IndeedBot import IndeedBot
from userconfig import UserConfig


if __name__ == "__main__":
    bot = IndeedBot(UserConfig(), dry_run=False)

    q1 = '((intern OR co-op) AND ' \
             '(software OR develop OR engineer OR mechanical OR mechatronics ' \
             'OR programming OR android OR ios OR technical OR qa OR testing OR automation)) ' \
             '-"marketing" -"human resources" -"hr" -unpaid -volunteer -"labor" -"labour" -secretary ' \
             '-receptionist -"assistant" -clerk -instructor -coordinator -tutor -cook -operator -manager'
    q2 = 'software AND engineer AND co-op'
    params = {
        'q': q2,
        'limit': '25',
        #'jt':'internship',
        #'fromage': '20',
        'language': 'en',
        'co': 'ca',
        'userip': "1.2.3.4",
        'useragent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    bot.search_with_api(params=params)
    bot.apply_jobs()
    bot.shut_down()