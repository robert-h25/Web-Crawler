# Web-Crawler
A simple Web Crawler which crawled the site https://quotes.toscrape.com. This Web crawler builds an inverted index for every word found and searches until there are no new URLs. More details on the implementation can be found in the report (CW2 Report Template)

# Commands

There are 5 commands for this program: build, load, print, find, exit.

1) The first command to be used is build which crawls the web and saves the resulting inverted index to the file “inverted_index.txt”. This command must be used first as we need to build the index before we use any kind of searching features.
2) The load command loads the inverted index and saves it in the global dictionary, words.
3) The print [word] command is followed by an input which takes a word from the user. We then print the occurrence of this word for a given document index (ordered as described) if it exists.
4) The find (words) command is followed by taking a word or phrase of words. These word(s) are then used to return a list of pages, printed to the command line, in the order of best results (as described).
5) The exit command is used to exit the program.

