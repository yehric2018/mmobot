from mmobot.utils.discord import is_mention


def test_isMention_valid():
    assert is_mention('<@12345>') is True
    assert is_mention('<@926384572215>') is True


def test_isMention_invalid():
    assert is_mention('nickname') is False
    assert is_mention('12345678') is False
    assert is_mention('<@nickname>') is False
    assert is_mention('<@1235732') is False
    assert is_mention('@nickname') is False
    assert is_mention('@1234567>') is False
    assert is_mention('<@>') is False
    assert is_mention('<@1234 5678>') is False
