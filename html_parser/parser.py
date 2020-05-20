from sly import Lexer, Parser


class HTMLLexer(Lexer):
    tokens = {
        COMMENT, 
        DOCTYPE,
        TAG_OPEN_SLASH,
        TAG_OPEN,
        TEXT,
        JAVASCRIPT
    }

    ignore = ' \t\r\n'

    COMMENT = r'<!-- .*? -->'
    DOCTYPE = r'<!DOCTYPE html>'
    JAVASCRIPT = r'\<script\ type=\"text\/javascript\"\>.*</script>'
    TAG_OPEN_SLASH = r'</'
    TAG_OPEN = r'<'
    TEXT = r'[^<]+'

    def TAG_OPEN(self, t):
        self.begin(TagLexer)
        return t

    def TAG_OPEN_SLASH(self, t):
        self.begin(TagLexer)
        return t


class TagLexer(Lexer):
    tokens = {
        TAG_CLOSE,
        TAG_SLASH_CLOSE,
        NAME,
        EQUALS
    }

    ignore = ' \t\r\n'

    TAG_CLOSE = r'>'
    TAG_SLASH_CLOSE = r'/>'
    NAME = r'[0-9a-zA-Z]+'
    EQUALS = r'='

    def TAG_CLOSE(self, t):
        self.begin(HTMLLexer)
        return t

    def TAG_SLASH_CLOSE(self, t):
        self.begin(HTMLLexer)
        return t

    def EQUALS(self, t):
        self.begin(AttributeValueLexer)
        return t


class AttributeValueLexer(Lexer):
    tokens = {
        UNQUOTED,
        SINGLE_QUOTED,
        DOUBLE_QUOTED,
    }

    UNQUOTED = r'[^ "\'=><~]+'
    SINGLE_QUOTED = r'\'[^\']*\''
    DOUBLE_QUOTED = r'"[^"]*"'

    def UNQUOTED(self, t):
        self.begin(TagLexer)
        return t

    def SINGLE_QUOTED(self, t):
        self.begin(TagLexer)
        t.value = t.value.strip("'")
        return t

    def DOUBLE_QUOTED(self, t):
        self.begin(TagLexer)
        t.value = t.value.strip('"')
        return t


class HTMLParser(Parser):
    tokens = HTMLLexer.tokens | TagLexer.tokens | AttributeValueLexer.tokens

    @_('DOCTYPE html_elements')
    def html_document(self, p):
        return ("HTML Document", p.html_elements)

    @_('')
    def html_elements(self, p):
        return []

    @_('html_element')
    def html_elements(self, p):
        return [p.html_element]

    @_('html_element html_elements')
    def html_elements(self, p):
        return [p.html_element] + p.html_elements

    @_('COMMENT')
    def html_element(self, p):
        return ("Comment", p.COMMENT[5:-4])

    @_('TEXT')
    def html_element(self, p):
        return ("Text", p.TEXT.strip())

    @_('JAVASCRIPT')
    def html_element(self, p):
        return ("Javascript", p.JAVASCRIPT.strip())

    @_('TAG_OPEN NAME tag_contents TAG_CLOSE html_elements TAG_OPEN_SLASH NAME TAG_CLOSE')
    def html_element(self, p):
        return ("Element", p.NAME0, p.tag_contents, p.html_elements)

    @_('TAG_OPEN NAME tag_contents TAG_SLASH_CLOSE')
    def html_element(self, p):
        return ("Element", p.NAME, p.tag_contents)

    @_('')
    def tag_contents(self, p):
        return []

    @_('tag_content')
    def tag_contents(self, p):
        return [p.tag_content]

    @_('tag_content tag_contents')
    def tag_contents(self, p):
        return [p.tag_content] + p.tag_contents

    @_('NAME EQUALS UNQUOTED')
    def tag_content(self, p):
        return ("Attribute", p.NAME, p.UNQUOTED)

    @_('NAME EQUALS SINGLE_QUOTED')
    def tag_content(self, p):
        return ("Attribute", p.NAME, p.SINGLE_QUOTED)

    @_('NAME EQUALS DOUBLE_QUOTED')
    def tag_content(self, p):
        return ("Attribute", p.NAME, p.DOUBLE_QUOTED)


def parse(webpage):
    lexer = HTMLLexer()
    parser = HTMLParser()
    return parser.parse(lexer.tokenize(webpage))

if __name__ == '__main__':
    data = """
        <!DOCTYPE html>
        <!-- just a comment -->
        <script type="text/javascript"></script>
        Hello
        <a b=c />
        <a href="http">Tomek</a>
        <b></b>
    """.strip()

    lexer = HTMLLexer()
    parser = HTMLParser()

    for tok in lexer.tokenize(data):
        print('type=%r, value=%r' % (tok.type, tok.value))

    result = parser.parse(lexer.tokenize(data))
    print(result)
