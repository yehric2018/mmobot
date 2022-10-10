from mmobot.utils.entities import convert_int_to_alphanum, convert_alphanum_to_int, is_entity_id


def test_convert_int_to_alphanum():
    assert convert_int_to_alphanum(1) == '1'
    assert convert_int_to_alphanum(10) == 'a'
    assert convert_int_to_alphanum(36) == '10'


def test_convert_alphanum_to_int():
    assert convert_alphanum_to_int('1') == 1
    assert convert_alphanum_to_int('a') == 10
    assert convert_alphanum_to_int('A') == 10
    assert convert_alphanum_to_int('/a') == 10
    assert convert_alphanum_to_int('10') == 36


def test_convert_alphanum_int_inverse():
    assert convert_alphanum_to_int(convert_int_to_alphanum(999)) == 999
    assert convert_alphanum_to_int(convert_int_to_alphanum(21738)) == 21738
    assert convert_int_to_alphanum(convert_alphanum_to_int('abc2')) == 'abc2'
    assert convert_int_to_alphanum(convert_alphanum_to_int('nz82f')) == 'nz82f'


def test_is_entity_id():
    assert is_entity_id('/abc') is True
    assert is_entity_id('/ABC') is True
    assert is_entity_id('/356') is True
    assert is_entity_id('/3a6B') is True

    assert is_entity_id('how are you') is False
    assert is_entity_id('/how are you') is False
    assert is_entity_id('/h$$u') is False
    assert is_entity_id('/h/e/l/l/o') is False
