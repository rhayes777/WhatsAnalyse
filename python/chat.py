import re
import datetime

DATE_TIME_FORMAT = "%d/%m/%Y, %H:%M:%S"


class Item:
    def __init__(self, line):
        self.line = line

    @property
    def datetime(self):
        date_part = self.line.split(": ")[0]
        return datetime.datetime.strptime(date_part, DATE_TIME_FORMAT)

    @property
    def is_comment(self):
        return len(self.line.split(": ")) > 2 and not self.is_image

    @property
    def author(self):
        return self.line.split(": ")[1]

    @property
    def text(self):
        return self.line.split(" {}: ".format(self.author))[-1]

    @property
    def is_image(self):
        return '<\xe2\x80\x8eimage omitted>\r\n' == self.line.split(" {}: ".format(self.author))[-1]


class Chat:
    def __init__(self, filename):
        f = open(filename, 'r+')
        self.lines = f.readlines()
        f.close()

    @property
    def items(self):
        return map(Item, self.lines)

    @property
    def comments(self):
        return filter(lambda i: i.is_comment, self.items)


def is_item_start(line):
    s = re.sub(r'(\d\d\/\d\d\/\d\d\d\d), (\d\d:\d\d:\d\d.*)', r'\1 \2', line)
    return s
