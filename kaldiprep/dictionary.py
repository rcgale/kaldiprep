import os

from kaldiprep.utterances import _write_file


def write_lexicon(entries, path, encoding=None):
    if not os.path.exists(path):
        os.makedirs(path)

    if isinstance(entries, dict):
        entries = entries.items()

    lexicon_lines = ["{} {}".format(word, pronunciation) for word, pronunciation in _iterate_entries(entries)]
    _write_file("lexicon.txt", lexicon_lines, path, encoding=encoding)


def _iterate_entries(entries):
    for word, pronunciation in sorted(entries):
        if isinstance(pronunciation, str):
            yield word, pronunciation

        try:
            for p in pronunciation:
                yield word, p
        except:
            raise TypeError('Couldn\'t handle lexicon entry {} of type {}'.format(pronunciation, type(pronunciation)))
