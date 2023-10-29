from io import BytesIO
import base64
from requests import Session
import requests
from . import config


# graph api wrapper implementation
def query(q: str):
    return requests.post(config.apiurl, json={"query": q}).json()


def search_songs(search_string: str):
    q = f"""{{search (string: "{search_string}") {{id, name}}}}"""

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


class SongsAPI(Session):
    def __init__(self, baseurl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseurl = baseurl

    def request(self, method, relpath, *args, **kwargs):
        return super().request(method, self.baseurl + relpath, *args, **kwargs)

    def get_songs(self, params={}):
        return self.get("/songs/", params=params).json()

    def get_song(self, song_id):
        return self.get(f"/songs/{song_id}").json()

    def get_song_opus(self, song_id):
        blob = self.get(f"/songs/{song_id}/opus").content
        return BytesIO(blob)

    def get_collections(self, params={}):
        return self.get("/collections", params=params).json()

    def get_collection_songs(self, collection_id):
        return self.get(f"/collections/{collection_id}/songs").json()

    def get_composers(self, params={}):
        return self.get("/composers", params=params).json()

    def get_composer_songs(self, composer_id):
        return self.get(f"/composers/{composer_id}/songs").json()
