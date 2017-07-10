# JobBot
In an attempt to make applying to jobs more productive and less soul-sucking I decided it would be cool if I tried to automate the process.
The JobBot application consists of multiple parts:
1. ApplicationBuilder: 
    1. This class will generate a custom message and resume (To be implemented) based on the job description given
    2. It will attempt to answer additional questions
2. Bot:       
    In general the Bots will have a search stage where they find appropiate jobs to apply to (easy apply, matches keywords) and store them in the job database.    
    In the application stage, the bot will look through the database for job applications that haven't been attempted and try to apply using ApplicationBuilder       
    The bots are seperated into which website they use as the web elements and procedures are different for each.     
      1. IndeedBot: Uses IndeedAPI for searching and fills out the applications using Selenium
      2. AngelBot: Manually crawls through job listings using Selenium and applies to them
## Required Files:
You need these files for the application to work properly:
* "blurbs.txt" - This file contains the keywords and text that are used to generate a custom message
    *The way it works is you specify keywords or tags that will trigger a blurb to be inserted into your custom message, if they are in the job description.
