import re
import datetime

DATE_TIME_FORMAT = "%d/%m/%Y, %H:%M:%S"

EXCLUDED_WORDS = {
    "the",
    "a",
    "i",
    "to",
    "of",
    "you",
    "is",
    "and",
    "for",
    "in",
    "on",
    "it",
    "my",
    "be",
    "i'm",
    "that",
    "and",
    "have",
    "are",
    "with",
    "at",
    "it's",
    "we",
    "me",
    "he",
    "your",
    "do",
    "no",
    "get",
    "it",
    "not",
    "but",
    "just",
    "was",
    "like",
    "so",
    "oh",
    "if",
    "can",
    "this",
    "don't",
    "all",
    "got",
    "as",
    "will"}


class Item:
    def __init__(self, line):
        self.line = line

    @property
    def datetime(self):
        date_part = self.line.split(": ")[0]
        return datetime.datetime.strptime(date_part, DATE_TIME_FORMAT)

    @property
    def is_comment(self):
        return len(self.line.split(": ")) > 2 and not self.is_image and not self.is_gif

    @property
    def is_gif(self):
        return "GIF omitted" in self.text

    @property
    def author_name(self):
        return self.line.split(": ")[1]

    @property
    def text(self):
        return self.line.split(" {}: ".format(self.author_name))[-1]

    @property
    def is_image(self):
        return '<\xe2\x80\x8eimage omitted>\r\n' == self.line.split(" {}: ".format(self.author_name))[-1]

    def __repr__(self):
        if self.is_comment:
            return "{} ({}):\n{}".format(self.author_name, self.datetime, self.text)

    def __iter__(self):
        for word in filter(lambda w: w != " ", self.text.replace('\n', '').split(" ")):
            yield word


class Author:
    def __init__(self, name, chat):
        self.name = name
        self.chat = chat

    @property
    def comments(self):
        return self.chat.filtered_comments(self.name)

    def word_counts(self, exclude_common_words=True):
        count_dict = {}
        for comment in self.comments:
            for word in comment:
                word = word.lower()
                if exclude_common_words and word in EXCLUDED_WORDS:
                    continue
                if word not in count_dict:
                    count_dict[word] = 0
                count_dict[word] += 1
        return sorted(count_dict.iteritems(), key=lambda i: i[1], reverse=True)

    def __repr__(self):
        return self.name

    def print_word_counts(self, limit=20, exclude_common_words=True):
        word_counts = self.word_counts(exclude_common_words)
        for n in range(limit):
            word_count = word_counts[n]
            print "{} - {}".format(word_count[0], word_count[1])


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

    @property
    def authors(self):
        return map(lambda name: Author(name, self), {comment.author_name for comment in self.comments})

    def filtered_comments(self, author_name=None, key_word=None):
        comments = self.comments

        if author_name is not None:
            comments = filter(lambda comment: comment.author_name == author_name, comments)

        if key_word is not None:
            comments = filter(lambda comment: key_word.lower() in comment.text.lower(), comments)

        return comments

    # def print_mentions(self):
    #     for author in self.authors:
    #         for word_count in author.word_counts():
    #             if word_count[0] in names:
    #                 print "{} {}".format(word_count[0], word_count[1])
    #         print "\n"

    def __iter__(self):
        for comment in self.comments:
            yield comment


def is_item_start(line):
    s = re.sub(r'(\d\d\/\d\d\/\d\d\d\d), (\d\d:\d\d:\d\d.*)', r'\1 \2', line)
    return s
