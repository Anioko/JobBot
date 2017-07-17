import json
import typing

import peewee

from Application.constants import ApplicationBuilderConstants as ABConstants
from userconfig import UserConfig
from models import Blurb, Tag, Question, create_question_from_model
from helpers import tokenize_text, any_in


class ApplicationBuilder:
    def __init__(self, user_config: UserConfig):
        # Create tables
        Blurb.create_table(fail_silently=True)
        Tag.create_table(fail_silently=True)
        self.user_config = user_config

    # TODO: Implement a function that can decide which resume to send
    def generate_resume(self, description):
        raise NotImplementedError

    @staticmethod
    def add_question_to_database(q_object: Question):
        def _categorize_question(q_instance: Question):
            if any_in(q_instance.tokens, ABConstants.QuestionNeedle.NEEDLES_RESUME):
                q_instance.question_type = ABConstants.QuestionTypes.RESUME

            elif any_in(q_instance.tokens, ABConstants.QuestionNeedle.NEEDLES_MESSAGE):
                q_instance.question_type = ABConstants.QuestionTypes.MESSAGE

            elif any_in(q_instance.tokens, ABConstants.QuestionNeedle.NEEDLES_LOCATION):
                q_instance.question_type = ABConstants.QuestionTypes.LOCATION

            elif any_in(q_instance.tokens, ABConstants.QuestionNeedle.NEEDLES_EXPERIENCE):
                q_instance.question_type = ABConstants.QuestionTypes.EXPERIENCE

            elif any_in(q_instance.tokens, ABConstants.QuestionNeedle.NEEDLES_EDUCATION):
                q_instance.question_type = ABConstants.QuestionTypes.EDUCATION

            elif any_in(q_instance.tokens, ABConstants.QuestionNeedle.NEEDLES_LANGUAGE):
                q_instance.question_type = ABConstants.QuestionTypes.LANGUAGE

            elif any_in(q_instance.tokens, ABConstants.QuestionNeedle.NEEDLES_CERTIFICATION):
                q_instance.question_type = ABConstants.QuestionTypes.CERTIFICATION

            elif any_in(q_instance.tokens, ABConstants.QuestionNeedle.NEEDLES_CONTACT_INFO):
                q_instance.question_type = ABConstants.QuestionTypes.CONTACT_INFO

            elif ABConstants.QuestionNeedle.NAME_MULTI_ATTACH in q_instance.name:
                q_instance.question_type = ABConstants.QuestionTypes.ADDITONAL_ATTACHMENTS
            q_instance.save()

        q = create_question_from_model(q_object)
        if q is not None:
            _categorize_question(q)

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
        intro_tag = Tag.get(Tag.text == ABConstants.TagBlurb.TAG_START)
        if self.user_config.Settings.USE_ALT_END_TAG:
            tag_end = Tag.get(Tag.text == ABConstants.TagBlurb.TAG_END_ALT)
        else:
            tag_end = Tag.get(Tag.text == ABConstants.TagBlurb.TAG_END)

        blurb_intro = Blurb.get(Blurb.id == intro_tag.blurb.id)
        blurb_end = Blurb.get(Blurb.id == tag_end.blurb.id)

        best_blurb_ids = self.pick_best_blurbs(description)
        message_body = ''
        # If not enough blurbs
        if len(best_blurb_ids) < self.user_config.Settings.MINIMUM_NUMBER_MATCHING_KEYWORDS:
            return None

        for b_id in best_blurb_ids:
            blurb = Blurb.get(Blurb.id == b_id)
            if self.user_config.Settings.USE_LONG_TEXT:
                string_blurb = ABConstants.BULLET_POINT + blurb.long_text + "\n"
            else:
                string_blurb = ABConstants.BULLET_POINT + blurb.short_text + "\n"
            message_body += string_blurb

        # TODO: Figure out how not to repeat this condition check
        if self.user_config.Settings.USE_LONG_TEXT:
            final_message = "{0}\n\n{1}\n{2}".format(blurb_intro.long_text, message_body, blurb_end.long_text)
        else:
            final_message = "{0}\n\n{1}\n{2}".format(blurb_intro.short_text, message_body, blurb_end.short_text)

        return final_message.replace(ABConstants.COMPANY_PLACEHOLDER, company)

    def pick_best_blurbs(self, job_description: str) -> typing.List[str]:
        key_words = tokenize_text(job_description)

        blurb_id_list = []
        for word in key_words:
            tag_query = Tag.select().where(Tag.text == word)
            for tag in tag_query:
                blurb_id_list.append(tag.blurb.id)

        # Avoid blurb repeats
        return list(set(blurb_id_list))

    def read_tag_blurbs(self, file_path: str):
        with open(file_path, 'r') as fp:
            content = json.load(fp)
        blurbs = content[ABConstants.TagBlurb.KEY_BLURBS]
        for json_blurb in blurbs:
            blurb = Blurb.create(
                long_text=json_blurb[ABConstants.TagBlurb.KEY_BLURB_LONG_TEXT],
                short_text=json_blurb[ABConstants.TagBlurb.KEY_BLURB_SHORT_TEXT]
            )
            self.add_tags_to_blurb(json_blurb[ABConstants.TagBlurb.KEY_BLURB_TAGS], blurb.id)

    @staticmethod
    def get_blurbs():
        return Blurb.select()

    @staticmethod
    def get_tags():
        return Tag.select()

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