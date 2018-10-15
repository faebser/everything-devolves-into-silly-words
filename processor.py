import json
from itertools import cycle, islice
import re
from collections import Iterable
import string


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
    # old code is shit
    # new code is needed
    #_token = _token.strip("()").lower()
    _token = _token.lower()
    # everything lowercase is better
    # we search for each occurrence of punctuation in the string
    # then we split there and then we split the remaining strings
    # match.span()
    # match.group()
    matches = list(re.finditer('([{}])'.format(string.punctuation), _token))
    if len(matches) != 0:
        borders = [0] + [[x.start(), x.end()] for x in matches]
        if borders[-1] != len(token) - 1:
            borders.append(len(token))
        punct_matches = [x.group() for x in matches]
        borders = list(pairwise(
            list(flatten(borders))
            ))
        token_list = []
        #borders = list(pairwise(borders))
        for index, pair in enumerate(borders):
            start, end = pair
            if index != len(borders)-1:
                match = punct_matches[index]
                token_list.append(_token[start:end].split())
                token_list.append(match)
            else:
                token_list.append(_token[start:end].split())
        token_list = list(flatten(token_list))
    else:
        token_list = _token.split()
    return token_list


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
with open('data-more-correct.json', 'w') as out_file:
    json.dump(data, out_file)
