import random


def id_generator(size, chars='123456789abcdef'):
    return ''.join(random.choice(chars) for _ in range(size))
