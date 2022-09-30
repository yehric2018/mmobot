ALPHANUM_DIGITS = '0123456789abcdefghijklmnopqrstuvwxyz'


def convert_int_to_alphanum(n):
    alphanum_id = ''
    while n > 0:
        alphanum_id = ALPHANUM_DIGITS[n % len(ALPHANUM_DIGITS)] + alphanum_id
        n = n // len(ALPHANUM_DIGITS)
    return alphanum_id


def convert_alphanum_to_int(n):
    decimal_id = 0
    for digit in n:
        decimal_id *= len(ALPHANUM_DIGITS)
        decimal_id += ALPHANUM_DIGITS.index(digit)
    return decimal_id
