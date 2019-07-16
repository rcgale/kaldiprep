import os

from kaldiprep.utterances import _write_file


def write_lexicon(entries, path, encoding=None):
    if not os.path.exists(path):
        os.makedirs(path)

    lexicon_lines = ["{} {}".format(word, pronunciation) for word, pronunciation in sorted(entries)]
    _write_file("lexicon.txt", lexicon_lines, path, encoding=encoding)
