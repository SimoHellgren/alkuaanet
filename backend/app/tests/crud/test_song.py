from backend.app import crud, schemas

def test_create_song(test_db_session):
    name = 'Test song'
    tones = 'A4'
    song_in = schemas.SongCreate(name=name, tones=tones)

    song = crud.create_song(test_db_session, song_in)

    assert song.name == name
    assert song.tones == tones
    assert song.id
    assert song.opus
    assert song.created_at
    assert song.updated_at
    assert song.created_at == song.updated_at


def test_get_song(test_db_session):
    name = 'Test song'
    tones = 'A4'
    song_in = schemas.SongCreate(name=name, tones=tones)

    song = crud.create_song(test_db_session, song_in)

    get_song = crud.get_song(test_db_session, song.id)

    assert song == get_song


def test_update_song(test_db_session):
    name = 'Test song'
    tones = 'A4'
    song_in = schemas.SongCreate(name=name, tones=tones)

    song = crud.create_song(test_db_session, song_in)
    old_opus = song.opus

    new_name = 'Test song 2'
    new_tones = 'A#4'

    new_song_in = schemas.SongUpdate(id=song.id, name=new_name, tones=new_tones)

    new_song = crud.update_song(test_db_session, new_song_in)

    assert song.id == new_song.id
    assert new_song.name == new_name
    assert new_song.tones == new_tones
    assert new_song.opus != old_opus
    assert song.created_at == new_song.created_at
    assert new_song.created_at < new_song.updated_at