from Bot import IndeedBot
from userconfig import UserConfig

if __name__ == "__main__":
    bot = IndeedBot(UserConfig(),dryRun=False)
    # bot.login()
    # bot.searchJobs()
    bot.applyJobs()
    bot.shutDown()