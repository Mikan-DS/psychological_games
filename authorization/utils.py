import random
import string


def generate_random_code(length=4, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(length))