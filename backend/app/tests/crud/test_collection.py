from backend.app import crud, schemas

collection1 = schemas.CollectionCreate(name='Hyviä lauluja')
collection2 = schemas.CollectionCreate(name='Huonoja lauluja')

song1 = schemas.SongCreate(name='Testsong 1', tones='C4-G3-E3-C3')
song2 = schemas.SongCreate(name='Testsong 2', tones='C4-G3-E3-C3')

def test_create_collection(test_db_session):
    db_collection = crud.create_collection(test_db_session, collection1)

    assert db_collection.id
    assert db_collection.name == collection1.name


# def test_get_composer(test_db_session):
#     composer_in = composer1

#     composer = crud.create_composer(test_db_session, composer_in)

#     get_composer = crud.get_composer(test_db_session, composer.id)

#     assert composer == get_composer


# def test_add_song_to_composer(test_db_session):
#     # This tests two things: adding songs and getting a composer's songs.
#     # Should probably be separated somehow 
#     composer = crud.create_composer(test_db_session, composer1)
#     db_song1 = crud.create_song(test_db_session, song1)
#     db_song2 = crud.create_song(test_db_session, song2)

#     crud.add_song_to_composer(test_db_session, composer.id, db_song1.id)

#     composer_songs = crud.get_songs_by_composer(test_db_session, composer.id)

#     assert db_song1 in composer_songs
#     assert db_song2 not in composer_songs

# def test_add_song_to_composer2(test_db_session):
#     # Ensure that adding a song to a composer does not add it to other composers
#     # Should probably be separated somehow 
#     db_comp1 = crud.create_composer(test_db_session, composer1)
#     db_comp2 = crud.create_composer(test_db_session, composer2)
#     song = crud.create_song(test_db_session, song1)

#     crud.add_song_to_composer(test_db_session, db_comp1.id, song.id)

#     composer_songs1 = crud.get_songs_by_composer(test_db_session, db_comp1.id)
#     composer_songs2 = crud.get_songs_by_composer(test_db_session, db_comp2.id)

#     assert song in composer_songs1
#     assert song not in composer_songs2

# def test_search_composers(test_db_session):
#     db_composer1 = crud.create_composer(test_db_session, composer1)
#     db_composer2 = crud.create_composer(test_db_session, composer2)

#     # ensure case insensitivity
#     composers = crud.search_composers_by_lastname(test_db_session, 'sÄVel')

#     assert db_composer1 in composers
#     assert db_composer2 not in composers