#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout
import json
import string

from text_input_technique import TextEdit

"""
Work distribution was as follows:
logic for logging and parsing arguments mainly by kay brinkmann, event logic and ui mainly by Joshua benker,
general script structure by both
"""

"""
setup json file should look like this
{
  "USER_ID": 1,
  "TEXT_FILE": "test.txt",
  "WORDS_FILE": "words.txt",
  "USE_COMPLETER": "yes"
}
TEXT_FILE should be a list of sentences with each sentence in a new line 
(if file can't be opened default sentences are used)
WORDS_FILE is a file with words for the autocompleter feature. Can be any type of text as long as words are seperated by
either whitespaces of new lines. Duplicate words are removed. Can be empty string if autocomplete feature is not used
USE_COMPLETER decides if autocompleter is used in the test. Use "yes" if you want to use autocompleter.
"""


# model class for all test logic like logging etc.
class TypingModel(object):

    def __init__(self, user_id, sentences, autocomplete_words, use_completer):
        self.timer = QtCore.QTime()
        self.user_id = user_id
        self.sentences = sentences
        self.sentence_number = 1
        self.autocomplete_words = autocomplete_words
        self.use_completer = use_completer
        self.current_sentence = sentences[0]
        self.words = sentences[0].split()
        self.sentence = ""
        self.word = ""
        self.timer_word = QtCore.QTime()
        self.testStarted = False
        self.wordFinished = False
        self.word_times = []
        self.log_writer = csv.writer(sys.stdout)

    # sets sentence and updates sentence number
    def setSentence(self):
        if self.sentence_number < len(self.sentences):
            self.statsLog()

            self.current_sentence = self.sentences[self.sentence_number]
            self.words = self.sentences[self.sentence_number].split()
            # sys.stdout.write(self.current_sentence)
            self.sentence_number += 1
        else:
            self.statsLog()
            self.eventLog("test finished", "")
            sys.exit()

    # for logging sentence writing statistics, used www.cse.yorku.ca/~stevenc/tema/ for overall structure
    def statsLog(self):
        time = sum(self.word_times)
        presented_text = self.current_sentence
        transcribed_text = self.sentence
        presented_characters = len(presented_text)
        transcribed_characters = len(transcribed_text)
        wpm = self.wordsPerMinute(transcribed_text, time)
        self.log_writer.writerow(["stats_log", self.user_id, presented_text, transcribed_text,
                                  presented_characters, transcribed_characters, time/1000, wpm])

    # for logging event data (i.e. key presses), used www.cse.yorku.ca/~stevenc/tema/ for overall structure
    def eventLog(self, event_type, event_):
        timestamp = self.timestamp()
        self.log_writer.writerow(["event_log", self.user_id, event_type, event_, timestamp])

    # returns timestamp of current time
    def timestamp(self):
        return QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)

    # calculates words per minute
    def wordsPerMinute(self, text, time):
        words = text.split()
        word_length = (len(words) - 1 + sum(len(word) for word in words)) / len(words)
        if word_length == 0:
            wpm = float(0)
        else:
            wpm = len(text) / (time / 1000) * 60 / word_length
        return wpm


# Qwidget class for handling the UI
class TypingTest(QtWidgets.QWidget):

    def __init__(self, model):
        super(TypingTest, self).__init__()
        self.model = model
        self.initUI()

    # sets up completer if necessary
    def __setup_completer(self):
        if self.model.use_completer:
            completer = QtWidgets.QCompleter(self.model.autocomplete_words, self)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            completer.setWrapAround(False)
            self.text_edit.set_completer(completer)

    def initUI(self):
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle('Speed Test')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.rules = QtWidgets.QLabel(self)
        self.rules.setAlignment(QtCore.Qt.AlignCenter)
        self.rules.setText("<u>please write the shown sentence(s) below:</u>")
        self.testtext = QtWidgets.QLabel(self)
        self.testtext.setAlignment(QtCore.Qt.AlignCenter)
        self.testtext.setText(self.model.current_sentence)
        self.text_edit = TextEdit(self.model)
        if self.model.use_completer:
            self.__setup_completer()
        layout = QVBoxLayout()
        layout.addWidget(self.rules)
        layout.addWidget(self.testtext)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        self.show()

    # if enter is pressed outside of autocomplete move to next sentence
    # had no way of accessing the testtext from outside this file
    def keyReleaseEvent(self, event):
        if not self.text_edit.popUpVisible():
            if event.key() == QtCore.Qt.Key.Key_Return:
                self.updateText()

    # updates shown sentence according to current sentence
    def updateText(self):
        self.testtext.setText(self.model.current_sentence)


def main():
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) < 1:
        sys.stderr.write("you need to pass a setup file")
        sys.exit(1)
    model = TypingModel(*parse_config(sys.argv[1]))
    typingtest = TypingTest(model)
    sys.exit(app.exec())


# creates a list of sentences from file where each list element represents a line in the file
def sentences_file_to_list(filename):
    sentences = []
    try:
        file = open(filename).readlines()
    except IOError:
        # use default sentences if file can't be opened
        return ["This is default text.", "It can be used for testing."]
    for line in file:
        sentences.append(line)
    return sentences


# reads words file and turns it into a list of words
# can create word list from any type of text, there only needs to be either a space or newline between each word
def words_file_to_list(filename):
    try:
        file = open(filename)
    except IOError:
        return []
    text = file.read().replace("/n", " ")
    text_without_punct = text.translate(str.maketrans('', '', string.punctuation))
    raw_word_list = text_without_punct.split()
    word_list = list(set(raw_word_list))
    word_list.sort()
    file.close()
    return word_list


def parse_config(file):
    with open(str(file)) as f:
        setup_dict = json.load(f)
    sentences = sentences_file_to_list(setup_dict["TEXT_FILE"])
    autocomplete_words = words_file_to_list(setup_dict["WORDS_FILE"])
    user_id = setup_dict["USER_ID"]
    if setup_dict["USE_COMPLETER"] == "yes":
        use_completer = True
    else:
        use_completer = False
    return user_id, sentences, autocomplete_words, use_completer


if __name__ == '__main__':
    main()
