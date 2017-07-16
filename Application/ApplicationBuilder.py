from models import Blurb, Tag
from run import UserConfig
import nltk
import re
from models import Question
import peewee
from Application.constants import ApplicationBuilderConstants as ABConstants
import typing
from models import Job

class ApplicationBuilder:
    def __init__(self, user_config: UserConfig):
        # Create tables
        Blurb.create_table(fail_silently=True)
        Tag.create_table(fail_silently=True)
        self.user_config = user_config

    # TODO: Implement a function that can decide which resume to send
    def generate_resume(self, description):
        raise NotImplementedError

    def answer_question(self, job: Job, question_label: str, default_experience_answer=False):
        """
        This function attempts to answer the question given just it's label
        1. If the question is asking for a cover-letter it will generate one base on the job description
        2. If the question is already in the database it will return the 'answer' field, which may be empty
        3. If it is asking for experience and there is no answer in the database, you can specify a default answer
        :param job:
        :param question_label:
        :param default_experience_answer:
        :return:
        """
        if ABConstants.QuestionNeedle.MESSAGE in question_label:
            job.message = self.generate_message(job.description, job.company)
            return job.message

        try:
            question = Question.get(Question.label == question_label)
            if question.answer is None:
                if question.question_type == ABConstants.QuestionTypes.EXPERIENCE:
                    if self.user_config.Settings.DEFAULT_EXPERIENCE is not None:
                        question.answer = self.user_config.Settings.DEFAULT_EXPERIENCE
                        return question.answer
                if question.question_type == ABConstants.QuestionTypes.LOCATION:
                    if ('vancouver, bc' not in question.label) and ('burnaby, bc' not in question.label):
                        question.answer = 'No'
                    else:
                        question.answer = 'Yes'

            return question.answer

        except peewee.DoesNotExist:
            pass

        return None

    @staticmethod
    def get_question_from_label(question_label: str) -> typing.Optional[Question]:
        try:
            return Question.get(Question.label == question_label)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def add_question_to_database(q_object: Question):
        def _categorize_question(q: Question):
            # TODO: Change all these to any
            if ABConstants.QuestionNeedle.RESUME in q.label:
                q.question_type = ABConstants.QuestionTypes.RESUME

            elif ABConstants.QuestionNeedle.MESSAGE in q.label:
                q.question_type = ABConstants.QuestionTypes.MESSAGE

            elif any(string in q.label for string in ABConstants.QuestionNeedle.LIST_LOCATION):
                q.question_type = ABConstants.QuestionTypes.LOCATION

            elif ABConstants.QuestionNeedle.EXPERIENCE in q.label:
                q.question_type = ABConstants.QuestionTypes.EXPERIENCE

            elif any(string in q.label for string in ABConstants.QuestionNeedle.LIST_EDUCATION):
                q.question_type = ABConstants.QuestionTypes.EDUCATION

            elif ABConstants.QuestionNeedle.LANGUAGE in q.label:
                q.question_type = ABConstants.QuestionTypes.LANGUAGE

            elif ABConstants.QuestionNeedle.CERTIFICATION in q.label:
                q.question_type = ABConstants.QuestionTypes.CERTIFICATION

            elif any(string in q.label for string in ABConstants.QuestionNeedle.LIST_CONTACT_INFO):
                q.question_type = ABConstants.QuestionTypes.CONTACT_INFO

            q.save()

        try:
            q = Question.create(
                label=q_object.label,
                website=q_object.website,
                input_type=q_object.input_type,
                secondary_input_type=q_object.secondary_input_type
            )
            _categorize_question(q)

        except peewee.IntegrityError:
            pass

    def generate_message(self, description: str, company: str) -> typing.Optional[str]:
        """
        Returns a generated message based on the job description and company
        If 'containMinBlurbs' == True, then return None if not enough tags are in description
        --Useful to see if you are decent fit for the job
        :param description:
        :param company:
        :param contain_min_blurbs:
        :param alt_end_tag:
        :return:
        """
        intro_tag = Tag.get(Tag.text == ABConstants.START_TAG)
        if self.user_config.Settings.USE_ALT_END_TAG:
            end_tag = Tag.get(Tag.text == ABConstants.END_TAG_ALT)
        else:
            end_tag = Tag.get(Tag.text == ABConstants.END_TAG)

        blurb_intro = Blurb.get(Blurb.id == intro_tag.blurb.id)
        blurb_end = Blurb.get(Blurb.id == end_tag.blurb.id)

        best_blurb_ids = self.pick_best_blurbs(description)
        message_body = ''
        # If not enough blurbs
        if len(set(best_blurb_ids)) < self.user_config.Settings.MINIMUM_NUMBER_MATCHING_KEYWORDS:
            return None

        for b_id in best_blurb_ids:
            blurb = Blurb.get(Blurb.id == b_id)
            message_body += ABConstants.BULLET_POINT + blurb.text + "\n"

        final_message = "{0}\n{1}\n\n{2}".format(blurb_intro.text, message_body, blurb_end.text)
        return final_message.replace(ABConstants.REPLACE_COMPANY_STRING, company)

    def pick_best_blurbs(self, job_description: str) -> typing.List[str]:
        tokens = nltk.word_tokenize(job_description)
        word_list = set([word.lower() for word in tokens if word.isalpha()])
        # Remove stopwords (the, a)
        key_words = [word for word in word_list if word not in nltk.corpus.stopwords.words('english')]

        blurb_id_list = []
        for word in key_words:
            tag_query = Tag.select().where(Tag.text == word)
            for tag in tag_query:
                blurb_id_list.append(tag.blurb.id)

        # Avoid blurb repeats
        return sorted(set(blurb_id_list))

    def read_tag_blurbs(self, file_path: str):
        with open(file_path, "r") as f:
            content = f.read()
            list_list_tags = re.findall(ABConstants.REGEX_TAGS_CAPTURE, content)
            list_blurbs = re.findall(ABConstants.REGEX_BLURB_CAPTURE, content)
            if len(list_list_tags) == len(list_blurbs):
                for i in range(0, len(list_blurbs)):
                    list_tags = list_list_tags[i].split(',')
                    blurb_id = self.create_blurb(list_blurbs[i].strip())
                    self.add_tags_to_blurb(list_tags, blurb_id)
            else:
                print('Length of tags and blurbs do not match. Perhaps you have a formatting error?')

    @staticmethod
    def get_blurbs():
        return Blurb.select()

    @staticmethod
    def get_tags():
        return Tag.select()

    @staticmethod
    def create_blurb(blurb_text: str) -> int:
        b = Blurb.create(text=blurb_text)
        return b.id

    def add_tags_to_blurb(self, tags, blurb_id: int):
        query = Blurb.select().where(Blurb.id == blurb_id)
        if query.exists():
            for tag in tags:
                self._add_tag_to_blurb(tag, blurb_id)
        else:
            print('Blurb id: {0} is not in the database!'.format(blurb_id))

    @staticmethod
    def _add_tag_to_blurb(tag, blurb_id):
        b = Blurb.select().where(Blurb.id == blurb_id)
        Tag.create(text=tag.lower().strip(), blurb=b)

    @staticmethod
    def reset_all_tables():
        Tag.drop_table()
        Blurb.drop_table()

        Blurb.create_table(fail_silently=True)
        Tag.create_table(fail_silently=True)

if __name__ == "__main__":
    a = ApplicationBuilder(UserConfig())
    desc = '''Co-Op – Applications and Testing 
Insurance Corporation of British Columbia  73 reviews - North Vancouver, BC
A career at ICBC is an opportunity to be part of a talented, diverse and inclusive team that is driven to serve its customers and community. Make the most of your skills and take the opportunity to grow and develop your career. You can expect a competitive salary, comprehensive benefits and a challenging work environment. Drive your career with us.

ICBC is an equal opportunity employer, and invites applications from all qualified candidates.

Co-Op – Applications and Testing

Job Title: (O) Coop Student Wt 2

Location: North Vancouver

Hours of Work: 7.5 hr Day Shift (M-F)

Reference Number: 109906

Employment Type: Co-op

Position Highlights

Working as a member on one of ICBC’s Applications and Testing teams, you’ll be assigned to various projects and engagements that will expose you to hundreds of applications, business insights and content management solutions which are used by thousands of internal and external users.

We have an excellent opportunity for a 4 or 8 month assignment where you have the opportunity to work in:

APPLICATIONS:

An agile development shop that technologies and programming languages such as: Java, UNIX, Oracle Database, C#/.NET,

C++, SAP, Guidewire ClaimCenter and PolicyCenter, SQL, SQL Server, Splunk, Opnet, Business Objects, Tableau, SAS,

HTML, CSS and JavaScript.

We are looking for a qualified co-op student who:

Will play a supporting role for development teams within IS Claims or Insurance Applications;
Will analyze P1 & P2 incidents of applications in production, and assist with post-incident review (PIR);
Gather and analyze user requirements for new application functionality;
Build web prototypes;
Create/update system documentation;
Create/modify reporting solutions;
Has an ability to work cooperatively within a team environment and other departments to provide support for data integration,
data analysis and data visualization.

AND/OR, TESTING

Integration and automation testing team, supporting functional regression and performance testing, for different release and

project teams, across multiple lines of business, using a variety of software tools, including: HP UFT, Selenium, HP ALM, Load

Runner, Splunk, Soap UI, and VSTS.

We are looking for a qualified co-op student who will:

Develop automated scripts for regressions testing needs of various release teams;
Understand the testing requirement and suggest simple and quick solutions to automate it;
Troubleshoot and resolve issues with automation framework;
Perform Proofs-of concept with multiple automation tools;
Create/update system documentation; and
Create/modify reporting solutions.
Position Requirements

The ideal candidate will have the following:

For Applications Roles

Good understanding of client server and web technologies;
Good understanding of Java and .NET/C# (UNIX would be a bonus), SQL database queries;
Good understanding of standard web technologies and libraries (i.e. HTML, CSS, JavaScript and JQuery);
Good understanding of quality assurance practices relating to software development; and
Ability to work cooperatively within a team environment and other departments to provide support for data integration, data
analysis and data visualization.

For Testing Roles

Good understanding of client server and web technologies;
Good understanding of Java, Ruby , .NET, VB and SQL database queries;
Good understanding of standard web technologies and libraries (ie HTML, CSS, JavaScript and JQuery);
Good understanding of SOA and web services;
Good understanding of quality assurance practices relating to software development; and
Willingness to learn with a strong analytical mindset.
For both Applications or Testing Roles

Excellent inter-personal skills;
Excellent communication/presentation skills; and
Excellent organizational and writing skills.
Position Information

As a valued member of the ICBC team, you’ll thrive in a performance-driven environment that emphasizes employee leadership

and accountability for delivering results. Anticipate a competitive salary, comprehensive benefits and a challenging work

environment.

If you’re ready to join a driven team, we’d love to hear from you.

ICBC is a welcoming, equal opportunity employer, and invites applications from all qualified candidates.

'''
    a.reset_all_tables()
    a.read_tag_blurbs(r'C:\Users\arash\Github\JobBot\blurbs.txt')
    print(a.generate_message(desc, 'ICBC'))