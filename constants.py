from helpers import Const


class HTML(Const):

    class TagType(Const):
        DIV = 'div'
        SPAN = 'span'
        INPUT = 'input'
        TEXTAREA = 'textarea'
        SELECT = 'select'
        H2 = 'h2'
        ANCHOR = 'a'

    class Attributes(Const):
        HREF = 'href'
        TYPE = 'type'
        ID = 'id'
        INNER_TEXT = 'innerText'
