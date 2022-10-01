from mmobot.utils.entities import convert_int_to_alphanum, convert_alphanum_to_int


def test_convert_int_to_alphanum():
    assert convert_int_to_alphanum(1) == '1'
    assert convert_int_to_alphanum(10) == 'a'
    assert convert_int_to_alphanum(36) == '10'


def test_convert_alphanum_to_int():
    assert convert_alphanum_to_int('1') == 1
    assert convert_alphanum_to_int('a') == 10
    assert convert_alphanum_to_int('10') == 36


def test_convert_alphanum_int_inverse():
    assert convert_alphanum_to_int(convert_int_to_alphanum(999)) == 999
    assert convert_int_to_alphanum(convert_alphanum_to_int('abc2')) == 'abc2'
