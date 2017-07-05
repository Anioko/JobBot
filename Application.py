from models import Blurb, Tag

class Application:
    def __init__(self):
        # Create tables
        Blurb.create_table(fail_silently=True)
        Tag.create_table(fail_silently=True)

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
        t = Tag.create(text=tag, blurb=b)

    def resetAllTables(self):
        Tag.drop_table()
        Blurb.drop_table()

        Blurb.create_table(fail_silently=True)
        Tag.create_table(fail_silently=True)

if __name__ == "__main__":
    a = Application()

    # TODO: Add display options

    while True:
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
            blurb = input('Create a blurb:\n\n')
            a.createBlurb(blurb)

        elif userInput == 3:
            blurbId = input('Enter the Blurb ID to associate tags with:\n')
            tags = input('Input tags seperated with commas:\n')
            tagList = tags.split(',')
            a.addTagsToBlurb(tagList, blurbId)

        elif userInput == -1:
            print('End application input')
            break

        elif userInput == -2:
            a.resetAllTables()
