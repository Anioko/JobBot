from Bot import IndeedBot
from userconfig import UserConfig

bot = IndeedBot(UserConfig(),dryRun=True)
# bot.login()
bot.searchJobs()
#bot.applyJobs()
bot.shutDown()