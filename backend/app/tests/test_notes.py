from app.synth.notes import note_to_frequency


def test_a4():
    assert note_to_frequency("A4") == 440


def test_a5():
    assert note_to_frequency("A5") == 880


def test_enharmonic():
    assert note_to_frequency("A#4") == note_to_frequency("Bb4")


def test_double_flat():
    assert note_to_frequency("Abb4") == note_to_frequency("G4")


def test_double_sharp():
    assert note_to_frequency("A##4") == note_to_frequency("B4")
