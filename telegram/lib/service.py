from io import BytesIO
import base64
import requests
from enum import StrEnum, auto
import os

APIURL = os.environ["API_URL"]


class Kind(StrEnum):
    song = auto()
    composer = auto()
    collection = auto()


# graph api wrapper implementation
def query(q: str):
    return requests.post(APIURL, json={"query": q}).json()


def search(kind: Kind, search_string: str):
    q = f"""{{search (kind: "{kind}", string: "{search_string}") {{id, name}}}}"""
    result = query(q)

    return result["data"]["search"]


def get_song(song_id):
    q = f"""{{song (songId: "{song_id}") {{ id, name tones, opus }} }}"""
    result = query(q)
    song = result["data"]["song"]

    # convert opus to bytestream
    opus = BytesIO(base64.b64decode(song["opus"]))
    song["opus"] = opus
    return song


def get_songlist(group_id: str):
    q = f"""{{item (pk: "{group_id}", sk: "song"){{id, name}}}}"""
    result = query(q)
    return result["data"]["item"]
