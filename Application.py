from models import Blurb, Tag
from userconfig import UserConfig
import os
import nltk

class ApplicationBuilder:
    def __init__(self, userConfig):
        # Create tables
        Blurb.create_table(fail_silently=True)
        Tag.create_table(fail_silently=True)
        self.userConfig = userConfig

    def generateCoverLetter(self, jobDescription, company):
        tokens = nltk.word_tokenize(jobDescription)
        words = sorted(set([word.lower() for word in tokens if word.isalpha()]))
        print(len(words))
        print(words)

    def getBlurbs(self):
        return Blurb.select()

    def getTags(self):
        return Tag.select()

    def createBlurb(self, blurb):
        b = Blurb.create(text = blurb)

    def addTagsToBlurb(self, tags, blurbId):
        query = Blurb.select().where(Blurb.id == blurbId)
        if query.exists():
            for tag in tags:
                self._addTagToBlurb(tag, blurbId)
        else:
            print('Blurb id: {0} is not in the database!'.format(blurbId))

    def _addTagToBlurb(self, tag, blurbId):
        b = Blurb.select().where(Blurb.id == blurbId)
        t = Tag.create(text=tag.lower(), blurb=b)

    def resetAllTables(self):
        Tag.drop_table()
        Blurb.drop_table()

        Blurb.create_table(fail_silently=True)
        Tag.create_table(fail_silently=True)

if __name__ == "__main__":
    a = ApplicationBuilder(UserConfig)

    optionsText = '''
    0: Print Blurbs
    1: Print Tags
    2: Insert a new blurb
    3: Add tags to blurb
    4: Generate cover letter for job description
    -1: End application
    -2: Reset tables
    '''

    while True:
        print(optionsText)
        userInput = int(input('Make a choice:\n'))
        if userInput == 0:
            print(Blurb.getHeader())
            for blurb in a.getBlurbs():
                print(blurb)

        elif userInput == 1:
            print(Tag.getHeader())
            for tag in a.getTags():
                print(tag)

        elif userInput == 2:
            blurb = input('Insert a new blurb:\n\n')
            a.createBlurb(blurb)

        elif userInput == 3:
            blurbId = input('Enter the Blurb ID to associate tags with:\n')
            tags = input('Input tags seperated with commas:\n')
            tagList = tags.split(',')
            a.addTagsToBlurb(tagList, blurbId)

        elif userInput == 4:
            jobText = ""
            print(('Paste the job description here:\n'))
            while True:
                line = input()
                if line:
                    jobText += line
                else:
                    break

            print()
            company = input('Enter the company name:\n')
            a.generateCoverLetter(jobDescription=jobText, company=company)

        elif userInput == -1:
            print('End application input')
            break

        elif userInput == -2:
            a.resetAllTables()
