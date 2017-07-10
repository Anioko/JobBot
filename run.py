from Bot.IndeedBot import IndeedBot
from userconfig import UserConfig
from indeed import IndeedClient

if __name__ == "__main__":
    #bot = IndeedBot(UserConfig(), dry_run=False)
    # bot.login()
    # bot.searchJobs()
    #bot.apply_jobs()
    #bot.shut_down()
    userConfig = UserConfig()
    client = IndeedClient(publisher=userConfig.INDEED_API_KEY)
    params = {
        'q': "python",
        'l': "austin",
        'userip': "1.2.3.4",
        'useragent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)"
    }

    search_response = client.search(**params)
    print(search_response['results'])