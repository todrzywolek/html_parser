import graphics
from parser import parse

def interpret(webpage): # Hello, friend
    for tree in webpage:
        nodetype=tree[0]
        if nodetype == "Text":
            graphics.word(tree[1])
        elif nodetype == "Element":
            tagname = tree[1]
            tagargs = tree[2]
            if len(tree) > 3:
                subtrees = tree[3]
            else:
                subtrees = []
            graphics.begintag(tagname, tagargs)
            interpret(subtrees)
            graphics.endtag()

webpage = """
    <!DOCTYPE html>
    <!-- just a comment -->
    <script type="text/javascript"></script>
    <h1>Title</h1>
    <h2>Subtitle</h2>
    Hello
    <b>friend</b>
    <ol>
        <li>Item 1</li>
        <li>Item 2</li>
    </ol>
    <ul>
        <li>Item 3</li>
        <li>Item 4</li>
    </ul>
    <a href="http://google.com" name="google">Google</a>
    <p>Paragraph 1</p>
""".strip()

parsed_webpage = parse(webpage)

graphics.initialize() # Enables display of output.\
interpret(parsed_webpage[1])
graphics.finalize() # Enables display of output.