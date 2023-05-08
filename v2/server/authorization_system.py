import string
import random
from models import User, Directory, LastTimeModification, File, db


def generate_token():
    length = 32
    res = ''
    chars = string.digits + string.ascii_letters
    for _ in range(length):
        res += random.choice(chars)
    return res


def get_user_by_token(token):
    pass