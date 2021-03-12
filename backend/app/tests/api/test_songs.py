def test_post_song(client):
    name = 'Test Song'
    tones = 'A4'

    song = {'name': name, 'tones': tones}
    response = client.post('/songs/', json=song)

    assert response.status_code == 201

    song_id = response.json()['id']

    assert song_id

    response = client.get(f'/songs/{song_id}')
    assert response.status_code == 200

    data = response.json()

    assert data['id'] == song_id
    assert data['name'] == name
    assert data['tones'] == tones




