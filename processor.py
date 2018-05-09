import json
from itertools import cycle, islice
import re
from collections import Iterable


def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    num_active = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while num_active:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            # Remove the iterator we just exhausted from the cycle.
            num_active -= 1
            nexts = cycle(islice(nexts, num_active))


def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)

def flatten(items):
    """Yield items from any nested iterable; see REF."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def process_token(_token):
    _token = _token.strip("()").lower()
    _token = list(filter(None, re.split("(,\s)|(\.\s)", _token)))
    return list(flatten([x.split() for x in _token]))


with open('raw.json') as in_file:
    unprocessed = json.load(in_file)

data = {}
BEGINNING = "-B-"
END = "-E-"

for token in unprocessed:
    sentence = process_token(token)
    if len(sentence) % 2 == 1:  # uneven
        sentence.append(None)
    pairs = list(roundrobin(sentence, sentence))  # we leave out the first and the last one
    pairs.insert(0, BEGINNING)
    pairs.append(END)
    for token1, token2 in pairwise(pairs):
        if token1 == BEGINNING and token2 == ".":
            print(token1, token2)
            print(token)
        if token1 is None or token2 is None:
            continue
        if token1 == token2:
            print("---")
            print(token1, token2)
            print(token)
            # let's leave them in they are silly
        if token2 is not None:
            if token1 in data:
                data[token1].append(token2)
            else:
                data[token1] = [token2]
        else:
            if token1 not in data:
                data[token1] = []



# write data object
with open('data.json', 'w') as out_file:
    json.dump(data, out_file)
