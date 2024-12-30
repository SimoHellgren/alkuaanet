"""Exploration of aws logs for tg bot / api usage. Potentially useful for future stats features"""

import boto3
from datetime import datetime
import json
from collections import Counter
from dotenv import load_dotenv
import os

load_dotenv()

LOG_GROUP = os.environ.get("LOG_GROUP")

client = boto3.client("logs")

response = client.describe_log_streams(
    logGroupName=LOG_GROUP,
    orderBy="LastEventTime",
    descending=True,
)

for stream in response["logStreams"]:
    print(stream["logStreamName"], stream["lastEventTimestamp"])

t = datetime(2023, 11, 28, 0, 0)
# find streams with relevant events
streams = list(
    filter(
        lambda x: x["lastEventTimestamp"] >= int(t.timestamp() * 1000),
        response["logStreams"],
    )
)

events = client.filter_log_events(
    logGroupName=LOG_GROUP,
    logStreamNames=[stream["logStreamName"] for stream in streams],
    startTime=int(t.timestamp() * 1000),
    filterPattern='{$.type = "telegram.callback"}',
)


def handle_callback_log(log):
    data = json.loads(log["message"])
    message = json.loads(data["message"])

    result = {
        "timestamp": data["timestamp"],
        "user": message["callback_query"]["from"]["username"],
        "item": message["callback_query"]["data"],
    }

    return result


data = list(map(handle_callback_log, events["events"]))

song_counter = Counter(d["item"] for d in data if d["item"].startswith("song:"))
composer_counter = Counter(d["item"] for d in data if d["item"].startswith("composer:"))
collection_counter = Counter(
    d["item"] for d in data if d["item"].startswith("collection:")
)

for song in song_counter.most_common(10):
    print(song)
