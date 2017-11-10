# def plot_tuples(tuple_lists, labels, title=None):
#     fig, ax = plt.subplots()
#     if title is not None:
#         ax.set_title(title)
#     for i, tuple_list in enumerate(tuple_lists):
#         print "\n" + labels[i]
#         print tuple_list
#         print len(tuple_list)
#         plt.xticks(range(len(tuple_list)), map(lambda t: month_abbreviation(t[0]), tuple_list))
#         ax.plot(range(len(tuple_list)), map(lambda t: t[1], tuple_list), label=labels[i])
#     handles, _ = ax.get_legend_handles_labels()
#     ax.legend(handles, labels)
#     plt.show()