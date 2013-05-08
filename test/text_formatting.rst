From http://en.wikibooks.org/wiki/LaTeX/Text_Formatting

>>> from nitrile import *
>>> env = Environment('spacing', '2.5')
>>> env.write('This paragraph has')
>>> env += LineBreak()
>>> print env
\begin{spacing}{2.5}
This paragraph has\\
<BLANKLINE>
\end{spacing}
<BLANKLINE>

>>> txt = Content()
>>> txt += T('D.~')
>>> txt += Command('textsc', 'Knuth')
>>> print txt
D.~\textsc{Knuth}
<BLANKLINE>

>>> txt = Content()
>>> txt += "Author Name"
>>> txt += Command('hfill')
>>> txt += Command('today')
>>> print txt
Author Name\hfill\today

>>> txt = Content()
>>> txt += "electromagnetic"
>>> txt += Command('hyp')
>>> txt += 'endioscopy'
>>> print txt
electromagnetic\hyp{}endioscopy

>>> cmd = Command('hypenpenalty=100000')
>>> print cmd
\hypenpenalty=100000

>>> q = DQuote('quote')
>>> print q
``quote''
