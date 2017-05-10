import re

class Chat:
    def __init__(self, filename):
        self.file = open(filename, 'r+')

    def comments(self):
        re.compile('\d\d\d\d-\d\d-\d\d\(T\)\d\d:\d\d:\d\d')


def is_item_start(line):
    s = re.sub(r'(\d\d\/\d\d\/\d\d\d\d), (\d\d:\d\d:\d\d.*)', r'\1 \2', line)
    return s