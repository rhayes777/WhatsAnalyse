A python project to parse and analyse WhatsApp conversations.

# Basic Usage:

python whatsanalyse.py _chat.txt moose

Will print all the comments in the exported WhatsApp chat "_chat.txt" containing the word "moose"

# Advanced Usage:

Create an instance of Chat in python:

chat = whatsanalyse.Chat("_chat.txt")

Get comments:

comments = chat.comments

comments[0].datetime
comments[0].text

Get authors:

authors = chat.authors

See whatsanalyse.py for more information
