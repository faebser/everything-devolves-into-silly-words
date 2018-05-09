import grequests
import json
from functools import partial
from collections import Iterable
import sys
import gevent

URL = "https://www.producthunt.com/frontend/graphql"


def flatten(items):
    """Yield items from any nested iterable; see REF."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def product_hunt_uber_for_x(soup):
    return [tag.string for tag in soup.select("ul[class^=postsList] div[class*=tagline]")]


def get_params_for_topic_query(_query, slug, cursor):
    return {
        "operationName": "TopicPage",
        "variables": {
            "slug": slug, "page": "topic", "cursor": cursor
        }, "query": _query}


def recursive_follow_topic(_query, slug, cursor, counter):
    print("found more for {} with counter {}".format(slug, counter))
    _rs = (grequests.post(u, json=params) for u, params in [(URL, get_params_for_topic_query(_query, slug, cursor))])
    _topic = [x.json() for x in grequests.map(_rs)][0]

    if _topic["data"]["topic"]["posts"]["pageInfo"]["hasNextPage"] is False or counter == 0:
        # basecase, we always need it
        print("reached end for {}".format(slug))
        return [x["node"]["tagline"] for x in _topic["data"]["topic"]["posts"]["edges"]]

    # values from here and other values
    return [x["node"]["tagline"] for x in _topic["data"]["topic"]["posts"]["edges"]] + \
           pr(_topic["data"]["topic"]["slug"], _topic["data"]["topic"]["posts"]["pageInfo"]["endCursor"], counter-1)


with open("graphql-query") as g_file:
    g_query = g_file.readline().strip()

with open("topic-query") as g_file:
    topic_query = g_file.readline().strip()

sys.setrecursionlimit(3500)
print(sys.getrecursionlimit())

# load initial website
# collections
rs = (grequests.post(u, json={"operationName": "CollectionPage", "query": g_query, "variables": {"slug": "uber-for-x"}}) for u in ["https://www.producthunt.com/frontend/graphql"])
parsed = [x.json() for x in grequests.map(rs)]
text_for_json = [x["node"]["post"]["tagline"] for x in parsed[0]["data"]["collection"]["items"]["edges"]]
# topics
ptq = partial(get_params_for_topic_query, topic_query)
pr = partial(recursive_follow_topic, topic_query)
topics = [
    (URL,
     ptq("cryptocurrencies", None)),
    (URL,
     ptq("artificial-intelligence", None)),
    (URL,
     ptq("wearables", None)),
    (URL,
     ptq("internet-of-things", None)),
    (URL,
     ptq("growth-hacking", None)),
    (URL,
     ptq("tech", None)),
    (URL,
     ptq("home", None)),
    (URL,
     ptq("marketing", None)),
    (URL,
     ptq("bots", None)),
    (URL,
     ptq("marketing", None)),
    (URL,
     ptq("apis", None)),
    (URL,
     ptq("task-management", None)),
    (URL,
     ptq("social-media-tools", None)),
    (URL,
     ptq("messaging", None)),
    (URL,
     ptq("venture-capital", None)),
    (URL,
     ptq("virtual-reality", None)),
    (URL,
     ptq("augmented-reality", None)),
    (URL,
     ptq("nomad-lifestyle", None)),
    (URL,
     ptq("branding", None)),
    (URL,
     ptq("fintech", None)),
    (URL,
     ptq("drones", None)),
    (URL,
     ptq("email-marketing", None)),
    (URL,
     ptq("advertising", None)),
    (URL,
     ptq("investing", None)),
    (URL,
     ptq("text-editors", None)),
    ]

topic_rs = (grequests.post(u, json=params) for u, params in topics)
topic_parsed = [x.json() for x in grequests.map(topic_rs)]
# recursive into each topic
for_json = []
jobs = []
for topic in topic_parsed:
    if topic["data"]["topic"]["posts"]["pageInfo"]["hasNextPage"] is True:
        # we found more
        jobs.append(
            gevent.spawn(pr, topic["data"]["topic"]["slug"],
                                topic["data"]["topic"]["posts"]["pageInfo"]["endCursor"],
                                1100))
    for_json.extend([x["node"]["tagline"] for x in topic["data"]["topic"]["posts"]["edges"]])

gevent.joinall(jobs)
text_for_json.extend(flatten([job.value for job in jobs]))
text_for_json.extend(for_json)

# parsed = [BeautifulSoup(x.text, "html.parser") for x in grequests.map(rs)]
# text_for_json = [product_hunt_uber_for_x(x) for x in parsed]
# print(text_for_json)
# get all elements
# put them into the data object

# write raw data and then put processing in other file

with open('raw.json', 'w') as raw_file:
    json.dump(text_for_json, raw_file)

