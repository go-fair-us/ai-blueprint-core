from defs import progress


def test_say_silent_when_disabled(capsys):
    progress._enabled = False
    progress.say("should not print")
    assert capsys.readouterr().out == ""


def test_say_prints_when_enabled(capsys):
    progress.enable()
    progress.say("hello")
    out = capsys.readouterr().out
    assert "[cedar" in out
    assert "hello" in out
    progress._enabled = False
