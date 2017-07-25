from Shared.helpers import Const


class HTMLConstants(Const):

    class TagType(Const):
        DIV = 'div'
        SPAN = 'span'
        INPUT = 'input'
        TEXT_AREA = 'textarea'
        SELECT = 'select'
        H2 = 'h2'
        ANCHOR = 'a'
        PARAGRAPH = 'p'

    class Attributes(Const):
        HREF = 'href'
        TYPE = 'type'
        ID = 'id'
        INNER_TEXT = 'innerText'
        NAME = 'name'
        FOR = 'for'
        VALUE = 'value'
        CLASS = 'class'

    class InputTypes(Const):
        RADIO = 'radio'
        TEXT = 'text'
        PHONE = 'tel'
        EMAIL = 'email'
        FILE = 'file'
        TEXT_AREA = 'textarea'
        HIDDEN = 'hidden'
        CHECK_BOX = 'checkbox'
        SELECT_ONE = 'select-one'
        FILE = 'file'

