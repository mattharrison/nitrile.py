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

Context Manager style

>>> doc = Document()
>>> doc += Comment('hello.tex - Our first LaTex example!')
>>> doc += Command('documentclass', 'article')
>>> with doc.Environment('document') as env:
...      env.write('Hello World!')
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

>>> c8 = Command('color', 'blue')
>>> content = Content()
>>> content +=c8 + T('Name') + LineBreak() + T('Work')
>>> c9 = Command('author', content)
>>> print c9
\author{\color{blue}
Name\\
Work}
<BLANKLINE>

>>> c10 = Command('today')
>>> print c10
\today
<BLANKLINE>
"""
RESERVED = """# $ % ^ & _ { } \ ~""".split()

class _Node(object):
    def __init__(self):
        self.children = []
        self.parent = None

    def next_sibling(self, sib):
        # get sibling to right of sib
        idx = self.children.index(sib)
        try:
            return self.children[idx + 1]
        except IndexError:
            return None

    def __call__(self, *args):
        if self.name is None:
            self.name = args[0]
            return self

    def __getattr__(self, name):
        if name == 'Environment':
            env = Environment(None)
            self += env
            return env
        elif name == 'Command':
            cmd = Command(None)
            self += cmd
            return cmd
        raise KeyError

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __iter__(self):
        return iter(self.children)

    def __iadd__(self, other):
        if isinstance(other, basestring):
            other = T(other)
        self.children.append(other)
        other.parent = self
        return self

    def __add__(self, other):
        if isinstance(other, basestring):
            other = T(other)
        self.children.append(other)
        other.parent = self
        return self

    def write(self, txt):
        self += Text(txt)

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
    def __init__(self, *args):
        super(Environment, self).__init__()
        self.name = args[0] if args else None
        self.rest = args[1:]

    def start(self):
        return u'\\begin{{{0}}}{1}\n'.format(
            self.name,
            ''.join('{{{0}}}'.format(x) for x in self.rest)
            )

        return
    def end(self):
        return u'\n\\end{{{0}}}\n'.format(self.name)


class Command(_Node):
    def __init__(self, name, arguments=None, options=None,
                 add_newline=False):
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
            self.arguments = arguments
        # self.arguments = [arguments] if isinstance(arguments, basestring) else arguments
        self.options = [options] if isinstance(options, basestring) else options
        self.add_newline = add_newline

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
        return u'\{0}{1}{2}{3}{4}'.format(
            self.name,
            one,
            two,
            '{}' if self.insert_space() else '',
            '\n' if self.add_newline else ""
           )

    def insert_space(self):
        if self.parent:
            sib = self.parent.next_sibling(self)
            return sib and isinstance(sib, T)


class Switch(_Node):
    def __init__(self, name):
        super(Switch, self).__init__()
        self.name = name

    def __str__(self):
        return u'{0}\{{1}\}'.format(
            self.name,
            self.content()
           )


class DQuote(_Node):
    def __init__(self, txt):
        super(DQuote, self).__init__()
        self.txt = txt

    def content(self):
        return self.txt

    def start(self):
        return u'``'

    def end(self):
        return u"''"


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
    doctest.testfile('test/text_formatting.rst')
