import translitcodec
import codecs
import re

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
_punct_re = '[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+'


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    print(_punct_re)
    print(_punct_re.split(text.lower()))
    for word in _punct_re.split(text.lower()):
        print(word)
        word = codecs.encode(word, 'translit/long')
        if word:
            result.append(word)
    return str(delim.join(result))

text = 'Hello world!'

slugify(text)
