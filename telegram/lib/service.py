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
    q = f"""
    {{
        search (kind: {kind}, string: "{search_string}") {{
            id, name
        }}
    }}"""
    result = query(q)

    return result["data"]["search"]


def get_song(song_id: int):
    q = f"""{{song (id: {song_id}) {{ id, name, tones, opus }} }}"""
    result = query(q)
    song = result["data"]["song"]

    # convert opus to bytestream
    opus = BytesIO(base64.b64decode(song["opus"]))
    song["opus"] = opus
    return song


def get_songlist(group_pk: str):
    """Splitting the pk here is a bit smelly"""
    kind, num = group_pk.split(":")

    q = f"""
    {{
        {kind} (id: {num}) {{
            songs {{
                id, name
            }}
        }}
    }}
    """

    result = query(q)

    return result["data"][kind]["songs"]


def get_random_song():
    q = "{randomSong {id, name, tones, opus}}"
    result = query(q)
    song = result["data"]["randomSong"]

    # convert opus to bytestream
    opus = BytesIO(base64.b64decode(song["opus"]))
    song["opus"] = opus
    return song
