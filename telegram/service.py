from io import BytesIO
from requests import Session


class SongsAPI(Session):
    def __init__(self, baseurl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.baseurl = baseurl

    def request(self, method, relpath, *args, **kwargs):
        return super().request(method, self.baseurl + relpath, *args, **kwargs)

    def get_song(self, song_id):
        return self.get(f'/songs/{song_id}').json()

    def get_song_opus(self, song_id):
        blob = self.get(f'/songs/{song_id}/opus').content
        return BytesIO(blob)

    def search_songs(self, query):
        return self.get(f'/songs/search/{query}').json()

    def get_collections(self):
        return self.get('/collections').json()

    def get_collection_songs(self, collection_id):
        return self.get(f'/collections/{collection_id}/songs').json()

    def search_collections(self, q):
        return self.get(f'/collections/search/{q}').json()

    def get_composers(self):
        return self.get('/composers').json()

    def get_composer_songs(self, composer_id):
        return self.get(f'/composers/{composer_id}/songs').json()

    def search_composers(self, query):
        return self.get(f'/composers/search/{query}').json()