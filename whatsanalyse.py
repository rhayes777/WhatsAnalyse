import re
import datetime
import sys

DATE_TIME_FORMAT = "%d/%m/%Y, %H:%M:%S"

EXCLUDED_WORDS = {"the", "a", "i", "to", "of", "you", "is", "and", "for", "in", "on", "it", "my", "be", "i'm", "that",
                  "and", "have", "are", "with", "at", "it's", "we", "me", "he", "your", "do", "no", "get", "it", "not",
                  "but", "just", "was", "like", "so", "oh", "if", "can", "this", "don't", "all", "got", "as", "will"}


class Item:
    """
    An Item from the chat. This is usually a comment, but could be a change in the name of the chat or a media message
    such as an image
    """

    def __init__(self, line, chat):
        """

        :param line: A line from the chat text file
        :param chat: An instance of the Chat class
        """
        self.line = line
        self.chat = chat

    @property
    def datetime(self):
        """

        :return: The datetime at which this item was posted
        """
        date_part = self.line.split(": ")[0]
        return datetime.datetime.strptime(date_part, DATE_TIME_FORMAT)

    @property
    def is_comment(self):
        """

        :return: True if this item is a comment
        """
        return len(self.line.split(": ")) > 2 and not self.is_media

    @property
    def is_media(self):
        """

        :return: True if this item is a media item (e.g. video or image)
        """
        return self.is_gif or self.is_audio or self.is_video or self.is_image

    @property
    def is_gif(self):
        """

        :return: True if this item is an image
        """
        return "GIF omitted" in self.text

    @property
    def is_audio(self):
        """

        :return: True if this item is audio
        """
        return "audio omitted" in self.text

    @property
    def is_video(self):
        """

        :return: True if this item is video
        """
        return "video omitted" in self.text

    @property
    def is_image(self):
        """

        :return: True if this item is an image
        """
        return '<\xe2\x80\x8eimage omitted>\r\n' == self.line.split(" {}: ".format(self.author_name))[-1]

    @property
    def author_name(self):
        """

        :return: The name of the person that posted this item
        """
        return self.line.split(": ")[1]

    @property
    def author(self):
        """

        :return: An instance of the Author class representing the person that posted this item
        """
        return self.chat.author_with_name(self.author_name)

    @property
    def text(self):
        """

        :return: The text associated with this item. Only valid for comments
        """
        return self.line.split(" {}: ".format(self.author_name))[-1]

    @property
    def minute_of_day(self):
        return 60 * self.datetime.hour + self.datetime.minute

    def __repr__(self):
        if self.is_comment:
            return "{} {}: {}".format(self.datetime, self.author_name, self.text)

    def __str__(self):
        if self.is_comment:
            return "{} {}: {}".format(self.datetime, self.author_name, self.text)

    def __iter__(self):
        for word in filter(lambda w: w != " ", self.text.replace('\n', '').split(" ")):
            yield word

    def lowercase_words(self):
        for word in self:
            yield word.lower()


def filter_comments(comments, author_name=None, key_word=None, min_minute=None, max_minute=None, min_hour=None,
                    max_hour=None, min_datetime=None, max_datetime=None, key_words=None):
    """
    Filters a list of comments by one or more predicates
    :param comments: The original list of comments
    :param author_name: The name of the author
    :param key_word: A key word contained in the text of the comment
    :param min_minute: The minimum minute of the day on which a comment was posted (0 - 1440)
    :param max_minute: The maximum minute of the day on which a comment was posted (0 - 1440)
    :param min_hour: The minimum hour of the day on which a comment was posted (0 - 1440)
    :param max_hour: The maximum hour of the day on which a comment was posted (0 - 1440)
    :param min_datetime: The minimum datetime (inclusive) on which a comment was posted
    :param max_datetime: The maximum datetime (exclusive) on which a comment was posted
    :param key_words: A list of key words found in the comment (all must be present for a match)
    :return: A filtered list of comments
    """

    if min_hour is not None:
        min_minute = 60 * min_hour + 0 if min_minute is None else min_minute

    if max_hour is not None:
        max_minute = 60 * max_hour + 0 if max_minute is None else max_minute

    if author_name is not None:
        comments = filter(lambda comment: comment.author_name == author_name, comments)

    if key_word is not None:
        comments = filter(lambda comment: key_word.lower() in comment.lowercase_words(), comments)

    if key_words is not None:
        for kw in key_words:
            comments = filter(lambda comment: kw.lower() in comment.lowercase_words(), comments)

    if min_minute is not None:
        comments = filter(lambda comment: comment.minute_of_day >= min_minute, comments)

    if max_minute is not None:
        comments = filter(lambda comment: comment.minute_of_day < max_minute, comments)

    if min_datetime is not None:
        comments = filter(lambda comment: min_datetime <= comment.datetime, comments)

    if max_datetime is not None:
        comments = filter(lambda comment: comment.datetime < max_datetime, comments)

    return comments


def bucket_comments_by_date(comments, start_datetime, end_datetime, bucket_timedelta):
    """
    Groups comments into lists posted between date intervals
    :param comments: The comments to group
    :param start_datetime: The earliest date time
    :param end_datetime: The latest date time
    :param bucket_timedelta: The size of each bucket
    :return: A list of tuples associating start dates with lists of comments
    """
    buckets = []
    current_datetime = start_datetime
    while current_datetime < end_datetime:
        buckets.append((current_datetime, filter_comments(comments, min_datetime=current_datetime,
                                                          max_datetime=current_datetime + bucket_timedelta)))
        current_datetime += bucket_timedelta
    return buckets


def bucket_comments_by_time_of_day(comments, delta_minutes):
    """
    Groups comments into lists posted at different times of day
    :param comments: The comments to group
    :param delta_minutes: The size of each bucket
    :return: A list of tuples associating starts times, in minutes between 0 and 1440, with lists of comments
    """
    buckets = []
    minutes_in_a_day = 1440
    current = 0
    while current < minutes_in_a_day:
        buckets.append(
            (current, filter_comments(comments, min_minute=current, max_minute=current + delta_minutes)))
        current += delta_minutes
    return buckets


class Author:
    """
    The author of one or more comments in the chat
    """

    def __init__(self, name, chat):
        """

        :param name: The author's name
        :param chat: The chat in which this author is a participant
        """
        self.name = name
        self.chat = chat

    @property
    def comments(self):
        """

        :return: A list of Comment objects made by this author
        """
        return filter_comments(self.chat.comments, author_name=self.name)

    @property
    def bursts(self):
        """

        :return: A list of lists of comments made without a gap of more than 10 seconds between each comment
        """
        last_comment_time = datetime.datetime(1970, 1, 1)
        burst = None
        bursts = []
        for comment in self.comments:
            if comment.datetime - last_comment_time < datetime.timedelta(seconds=10):
                burst.append(comment)
            else:
                bursts.append(burst)
                burst = [comment]
            last_comment_time = comment.datetime
        return bursts

    @property
    def post_count(self):
        """

        :return: The number of comments this user has made
        """
        return len(self.comments)

    def word_counts(self, exclude_common_words=True):
        """

        :param exclude_common_words: Excludes commonly found words from the list if True
        :return: A sorted list of tuples indicating the number of times this author has used each word
        """
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
        """

        :param limit: The number of words to print counts for. 20 -> top 20 most used words
        :param exclude_common_words: Whether frequently used words should be excluded (see EXCLUDED_WORDS)
        :return:
        """
        word_counts = self.word_counts(exclude_common_words)
        for n in range(limit):
            word_count = word_counts[n]
            print "{} - {}".format(word_count[0], word_count[1])


class Chat:
    """
    A real chat from WhatsApp
    """

    def __init__(self, filename):
        """

        :param filename: The filename of the exported WhatsApp chat (e.g. _chat.txt)
        """
        f = open(filename, 'r+')
        self.lines = f.readlines()
        f.close()

    @property
    def items(self):
        """

        :return: Each line taken from the chat file wrapped in an Item class
        """
        return map(lambda line: Item(line, self), self.lines)

    @property
    def comments(self):
        """

        :return: All items from this chat which were comments (as oppose to images, videos etc.)
        """
        return filter(lambda i: i.is_comment, self.items)

    @property
    def start_datetime(self):
        """

        :return: The datetime of the first item in the chat
        """
        return self.items[0].datetime

    @property
    def end_datetime(self):
        """

        :return: The datetime of the last item in the chat
        """
        return self.items[-1].datetime

    @property
    def authors(self):
        """

        :return: A list of participants in the chat
        """
        return map(lambda name: Author(name, self), {comment.author_name for comment in self.comments})

    def author_with_name(self, name):
        """

        :param name: The name of an author
        :return: The author with that name
        """
        return filter(lambda author: author.name == name, self.authors)[0]

    def print_comments_with_keyword(self, key_word):
        """
        Prints a list of comments that contained a particular keyword
        :param key_word:
        """
        for comment in filter_comments(self.comments, key_word=key_word):
            print "{} {}: {}".format(comment.datetime, comment.author_name, comment.text)

    def __iter__(self):
        """
        Iterating through the chat object's comments (note: could use items instead?)
        :return: yields comments from the chat
        """
        for comment in self.comments:
            yield comment


def print_summary(filename, keyword):
    chat = Chat(filename)
    chat.print_comments_with_keyword(keyword)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print_summary(sys.argv[1], sys.argv[2])
    else:
        print "usage: whatsanalyse.py [filename] [keyword]"
