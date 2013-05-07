r"""
>>> doc = Document()
>>> doc += Comment('hello.tex - Our first LaTex example!')
>>> doc += Command('documentclass', 'article')
>>> env = Environment('document')
>>> env += Text('Hello World!')
>>> doc += env
>>> print doc
% hello.tex - Our first LaTex example!
\documentclass{article}
\begin{document}
Hello World!
\end{document}
<BLANKLINE>

>>> with open('/tmp/foo.tex', 'w') as fout:
...     doc.write(fout)

>>> c2 = Command('documentclass', 'article', ['11pt', 'twoside', 'a4paper'])
>>> print c2
\documentclass[11pt,twoside,a4paper]{article}
<BLANKLINE>

>>> c3 = Command('usepackage', 'color')
>>> print c3
\usepackage{color}
<BLANKLINE>

>>> c4 = Command('usepackage', 'p1,p2,p3')
>>> print c4
\usepackage{p1,p2,p3}
<BLANKLINE>

>>> c5 = Command('usepackage', 'geometry', 'margin=2cm')
>>> print c5
\usepackage[margin=2cm]{geometry}
<BLANKLINE>

>>> foo = Content()
>>> foo += T('Andrew Roberts')
>>> foo += LineBreak()
>>> foo += T('School of Computing')
>>> foo += LineBreak()
>>> foo += Command('texttt', 'andy@foo.com')
>>> c6 = Command('author', foo)
>>> print c6
\author{Andrew Roberts\\
School of Computing\\
\texttt{andy@foo.com}
}
<BLANKLINE>

>>> c7 = Command('addcontentsline', 'toc,subsection,Preface'.split(','))

>>> print c7
\addcontentsline{toc}{subsection}{Preface}
<BLANKLINE>

"""
RESERVED = """# $ % ^ & _ { } \ ~""".split()

class _Node(object):
    def __init__(self):
        self.children = []
        self.parent = None

    def __iter__(self):
        return iter(self.children)

    def __iadd__(self, other):
        self.children.append(other)
        return self

    def __add__(self, other):
        self.children.append(other)
        return self

    def start(self):
        return ''

    def end(self):
        return ''

    def content(self):
        return ''.join(str(c) for c in self.children)

    def __str__(self):
        return ''.join([self.start(), self.content(), self.end()])


class Content(_Node):
    pass


class T(_Node):
    """Text"""
    def __init__(self, txt):
        super(T, self).__init__()
        self.txt = txt

    def content(self):
        return self.txt


class LineBreak(_Node):
    def content(self):
        return u'\\\\\n'


class Group(_Node):
    def __init__(self, name=None):
        super(Group, self).__init__()
        self.name = name

    def start(self):
        return u'{0}\n'.format(
            '\\begin'+self.name if self.name else "{",
            )

    def end(self):
        return u'\n{0}\n'.format(
            '\\end'+self.name if self.name else "{",
            )


class Environment(_Node):
    def __init__(self, name=None):
        super(Environment, self).__init__()
        self.name = name

    def start(self):
        return u'\\begin{{{0}}}\n'.format(self.name)
    def end(self):
        return u'\n\\end{{{0}}}\n'.format(self.name)


class Command(_Node):
    def __init__(self, name, arguments, options=None):
        super(Command, self).__init__()
        self.name = name
        self.list_type = False
        self.str_type = False
        if isinstance(arguments, basestring):
            self.str_type = True
            self.arguments = [arguments]
        elif isinstance(arguments, _Node):
            self.arguments = arguments
        elif isinstance(arguments, list):
            self.list_type = True
            self.arguments = arguments
        else:
            raise TypeError
        # self.arguments = [arguments] if isinstance(arguments, basestring) else arguments
        self.options = [options] if isinstance(options, basestring) else options

    def start(self):
        if self.options:
            one = '[{0}]'.format(','.join(self.options))
        else:
            one = ''
        if self.arguments:
            if self.list_type:
                two = ''.join('{{{0}}}'.format(str(x)) for x in self.arguments)
            elif self.str_type:
                two = '{{{0}}}'.format(','.join(str(x) for x in self.arguments))
            else:
                two = '{{{0}}}'.format(self.arguments)
        else:
            two = ''
        return u'\{0}{1}{2}\n'.format(
            self.name,
            one,
            two
           )


class Switch(_Node):
    def __init__(self, name):
        super(Switch, self).__init__()
        self.name = name

    def __str__(self):
        return u'{0}\{{1}\}'.format(
            self.name,
            self.content()
           )


class Comment(_Node):
    def __init__(self, txt):
        super(Comment, self).__init__()
        self.txt = txt

    def content(self):
        return self.txt

    def start(self):
        return u'% '

    def end(self):
        return '\n'


class Text(_Node):
    def __init__(self, txt):
        super(Text, self).__init__()
        self.txt = txt

    def content(self):
        return self.txt

    def __str__(self):
        return u'{0}'.format(
            self.content()
           )


class Document(_Node):
    def __str__(self):
        return u''.join(str(c) for c in self.children)

    def write(self, fout):
        fout.write(str(self))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
