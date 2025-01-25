import random
import string

def random_string(length, digits=True, incUppercase=True):
    letters = string.ascii_letters if incUppercase else string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))