from io import BytesIO
import base64
import httpx
from enum import StrEnum, auto
import os

APIURL = os.environ["API_URL"]


class Kind(StrEnum):
    song = auto()
    composer = auto()
    collection = auto()


# graph api wrapper implementation
def query(q: str, vars: dict | None = None) -> dict:

    return httpx.post(APIURL, json={"query": q, "variables": vars}).json()


def search(kind: Kind, search_string: str) -> dict:
    q = """
    query search($kind: Kind!, $string: String!){
        search(kind: $kind string: $string) {
            id
            name
         }
    }
    """

    result = query(q, {"kind": kind, "string": search_string})

    return result["data"]["search"]


def get_song(song_id: int) -> dict:
    q = """
    query getSong($id: Int!) {
        song (id: $id){
            id
            name
            tones
            opus
        }
    }
    """
    result = query(q, {"id": song_id})
    song = result["data"]["song"]

    # convert opus to bytestream
    opus = BytesIO(base64.b64decode(song["opus"]))
    song["opus"] = opus
    return song


def get_songlist(group_pk: str):
    """Splitting the pk here is a bit smelly"""
    kind, num = group_pk.split(":")

    # string manipulation a bit hacky but I guess it's better than double braces
    q = """
    query listSongs($id: Int!) {
        %(kind)s (id: $id) { songs { id name } }
    }
    """ % {
        "kind": kind
    }

    result = query(q, {"id": int(num)})

    return result["data"][kind]["songs"]


def get_random_song():
    q = "{randomSong {id, name, tones, opus}}"
    result = query(q)
    song = result["data"]["randomSong"]

    # convert opus to bytestream
    opus = BytesIO(base64.b64decode(song["opus"]))
    song["opus"] = opus
    return song
