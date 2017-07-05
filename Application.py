from models import Blurb, Tag
from userconfig import UserConfig
import helpers
import nltk
import re

class ABConfig(helpers.Const):
    REGEX_TAGS_CAPTURE = re.compile(r"'''(.*?)'''", re.DOTALL)
    REGEX_BLURB_CAPTURE = re.compile(r'"""(.*?)"""', re.DOTALL)
    START_TAG = 'start_tag'
    END_TAG = 'end_tag'
    REPLACE_COMPANY_STRING = r'{COMPANY}'
    BULLET_POINT = "-"

class ApplicationBuilder:
    def __init__(self, userConfig):
        # Create tables
        Blurb.create_table(fail_silently=True)
        Tag.create_table(fail_silently=True)
        self.userConfig = userConfig

    def generateMessage(self, jobDescription, company):
        introTag = Tag.get(Tag.text == ABConfig.START_TAG)
        endTag = Tag.get(Tag.text == ABConfig.END_TAG)

        blurbIntro = Blurb.get(Blurb.id == introTag.blurb.id)
        messageBody = self._pickBestBlurbs(jobDescription)
        blurbEnd = Blurb.get(Blurb.id == endTag.blurb.id)

        finalMessage = "{0}\n{1}\n\n{2}".format(blurbIntro.text, messageBody, blurbEnd.text)
        return finalMessage.replace(ABConfig.REPLACE_COMPANY_STRING, company)

    def _pickBestBlurbs(self, jobDescription):
        coverLetterBody = ""
        tokens = nltk.word_tokenize(jobDescription)
        words = set([word.lower() for word in tokens if word.isalpha()])
        # TODO: Singularize words?
        for word in words:
            tagQuery = Tag.select().where(Tag.text == word)
            for tag in tagQuery:
                b = Blurb.get(Blurb.id == tag.blurb.id)
                coverLetterBody += ABConfig.BULLET_POINT + b.text + "\n"

        return coverLetterBody

    def readTagBlurbs(self, filePath):
        with open(filePath, "r") as f:
            content = f.read()
            list_list_tags = re.findall(ABConfig.REGEX_TAGS_CAPTURE, content)
            list_blurbs = re.findall(ABConfig.REGEX_BLURB_CAPTURE, content)
            if len(list_list_tags) == len(list_blurbs):
                for i in range(0, len(list_blurbs)):
                    list_tags = list_list_tags[i].split(',')
                    blurbId = self.createBlurb(list_blurbs[i].strip())
                    self.addTagsToBlurb(list_tags, blurbId)
            else:
                print('Length of tags and blurbs do not match. Perhaps you have a formatting error?')

    def getBlurbs(self):
        return Blurb.select()

    def getTags(self):
        return Tag.select()

    def createBlurb(self, blurb):
        b = Blurb.create(text = blurb)
        return b.id

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
    desc = '''Test description...'''
    a.resetAllTables()
    a.readTagBlurbs('blurbs.txt')
    print(a.generateMessage(desc, 'comp'))