import re
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s : %(message)s')


# global expression
# http request exception
class HttpRequestExceptions(Exception):
    'http request error exception'
    pass


# SpecialException
class SpecialException(Exception):
    'Someting when wrong exception'


def sorted_alphanumeric(data):
    def alphanum_key(key):
        return [int(c) for c in re.split('([0-9]+)', key) if c.isdigit()]
    return sorted(data, key=alphanum_key)


def clearSpecialCharacters(texts):
    special_characters = ['!', ':', '/', '?',
                          '"', "'", '|', '\\', '*', '<', '>']
    for character in special_characters:
        texts = texts.replace(character, '')

    return texts


def format_text(texts):
    # remove number
    res = re.sub(r'\d', '', texts)
    res = texts.replace('\n', '.')

    # remove double space
    res = ' '.join(res.lower().split()).replace('..', '.')
    return res
