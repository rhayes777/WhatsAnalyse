import whatsanalyse
import datetime
from matplotlib import pyplot as plt
import sys


def plot_usage_over_time(chat_name):
    chat = whatsanalyse.Chat(chat_name)
    labels = []

    fig, ax = plt.subplots()
    for author in chat.authors:
        labels.append(author.name)
        tuple_list = whatsanalyse.bucket_comments_by_date(author.comments, chat.start_datetime, chat.end_datetime,
                                                          datetime.timedelta(days=7))
        tuple_list = map(lambda tup: (tup[0], len(tup[1])), tuple_list)

        plt.xticks(range(len(tuple_list)), map(lambda t: t[0], tuple_list))
        ax.plot(range(len(tuple_list)), map(lambda t: t[1], tuple_list), label=author.name)
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    plt.show()


def plot_usage_over_day(chat_name):
    chat = whatsanalyse.Chat(chat_name)
    labels = []

    def format_minutes_of_day(minutes):
        hour = minutes / 60
        minute = minutes % 60
        return "{:02d}:{:02d}".format(hour, minute)

    fig, ax = plt.subplots()
    for author in chat.authors:
        labels.append(author.name)
        tuple_list = whatsanalyse.bucket_comments_by_time_of_day(author.comments, 15)
        print tuple_list
        tuple_list = map(lambda tup: (tup[0], len(tup[1])), tuple_list)

        plt.xticks(range(len(tuple_list)), map(lambda t: t[0], tuple_list))
        ax.plot(range(len(tuple_list)), map(lambda t: t[1], tuple_list), label=author.name)
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    plt.show()


if __name__ == "__main__":
    # plot_usage_over_time(sys.argv[1])
    plot_usage_over_day(sys.argv[1])
