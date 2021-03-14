from backend.app import crud, schemas


composer1 = schemas.ComposerCreate(lastname='Säveltäjä', firstname='Sanni')
composer2 = schemas.ComposerCreate(lastname='Komposiittori', firstname='Keijo')

song1 = schemas.SongCreate(name='Testsong', tones='C4-G3-E3-C3')

def test_create_composer(test_db_session):
    composer_in = composer1

    composer = crud.create_composer(test_db_session, composer_in)

    assert composer.id
    assert composer.lastname == composer_in.lastname
    assert composer.firstname == composer_in.firstname


def test_get_composer(test_db_session):
    composer_in = composer1

    composer = crud.create_composer(test_db_session, composer_in)

    get_composer = crud.get_composer(test_db_session, composer.id)

    assert composer == get_composer


def test_add_song_to_composer(test_db_session):
    # This tests two things: adding songs and getting a composer's songs.
    # Should probably be separated somehow 
    composer = crud.create_composer(test_db_session, composer1)
    song = crud.create_song(test_db_session, song1)

    crud.add_song_to_composer(test_db_session, composer.id, song.id)

    composer_songs = crud.get_songs_by_composer(test_db_session, composer.id)

    assert song in composer_songs

def test_search_composers(test_db_session):
    db_composer1 = crud.create_composer(test_db_session, composer1)
    db_composer2 = crud.create_composer(test_db_session, composer2)

    # ensure case insensitivity
    composers = crud.search_composers_by_lastname(test_db_session, 'sÄVel')

    assert db_composer1 in composers
    assert db_composer2 not in composers