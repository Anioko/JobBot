from Bot.IndeedBot import IndeedBot
from userconfig import UserConfig

if __name__ == "__main__":
    bot = IndeedBot(UserConfig(), dry_run=False)
    # bot.login()
    # bot.searchJobs()
    bot.apply_jobs()
    bot.shut_down()