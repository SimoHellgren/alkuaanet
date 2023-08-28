from app import crud, schemas

collection1 = schemas.CollectionCreate(name="Hyviä lauluja")
collection2 = schemas.CollectionCreate(name="Huonoja lauluja")

song1 = schemas.SongCreate(name="Testsong 1", tones="C4-G3-E3-C3")
song2 = schemas.SongCreate(name="Testsong 2", tones="C4-G3-E3-C3")


def test_create_collection(test_db_session):
    db_collection = crud.create_collection(test_db_session, collection1)

    assert db_collection.id
    assert db_collection.name == collection1.name


def test_get_collection(test_db_session):
    db_collection = crud.create_collection(test_db_session, collection1)

    get_collection = crud.get_collection(test_db_session, db_collection.id)

    assert db_collection == get_collection


def test_add_song_to_collection(test_db_session):
    # this tests for quite many things. Worth considering separate tests
    db_coll1 = crud.create_collection(test_db_session, collection1)
    db_coll2 = crud.create_collection(test_db_session, collection2)

    db_song1 = crud.create_song(test_db_session, song1)
    db_song2 = crud.create_song(test_db_session, song2)

    crud.add_song_to_collection(test_db_session, db_coll1.id, db_song1.id)

    collection_songs1 = crud.get_collection_songs(test_db_session, db_coll1.id)
    collection_songs2 = crud.get_collection_songs(test_db_session, db_coll2.id)

    assert db_song1 in collection_songs1
    assert db_song1 not in collection_songs2
    assert db_song2 not in collection_songs1
    assert db_song2 not in collection_songs2


def test_add_song_many_times(test_db_session):
    # adding song to collection should be idempotent
    db_coll = crud.create_collection(test_db_session, collection1)
    db_song = crud.create_song(test_db_session, song1)

    crud.add_song_to_collection(test_db_session, db_coll.id, db_song.id)
    crud.add_song_to_collection(test_db_session, db_coll.id, db_song.id)

    collection_songs = crud.get_collection_songs(test_db_session, db_coll.id)

    assert db_song in collection_songs
    assert len(collection_songs) == 1


def test_search_collections(test_db_session):
    db_collection1 = crud.create_collection(test_db_session, collection1)
    db_collection2 = crud.create_collection(test_db_session, collection2)

    # ensure case insensitivity
    search_result1 = crud.search_collections_by_name(test_db_session, "h")

    assert db_collection1 in search_result1
    assert db_collection2 in search_result1

    search_result2 = crud.search_collections_by_name(test_db_session, "hy")

    assert db_collection1 in search_result2
    assert db_collection2 not in search_result2
