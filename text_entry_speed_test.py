#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout
import json
import re

from text_input_technique import AutoCompleter 

"""
Work distribution was as follows:
logic for logging and parsing arguments by kay brinkmann, event logic and ui by Joshua benker,
general script structure by both
"""

"""
setup.json
{
  "USE_COMPLETER": "yes"
}

"""

class TypingModel(object):

    def __init__(self, sentences, user_id, use_completer):
        self.timer = QtCore.QTime()
        self.user_id = user_id
        self.sentences = sentences
        self.sentence_number = 1
        self.sentence = ""
        self.use_completer = use_completer
        self.current_sentence = sentences[0]
        self.words = sentences[0].split()
        self.word = ""
        self.timer_word = QtCore.QTime()
        self.testStarted = False
        self.wordFinished = False
        self.word_times = []
        self.log_writer = csv.writer(sys.stdout)


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

    def statsLog(self):
        time = sum(self.word_times)
        presented_text = self.current_sentence
        transcribed_text = self.sentence
        presented_characters = len(presented_text)
        transcribed_characters = len(transcribed_text)
        wpm = self.wordsPerMinute(transcribed_text, time)
        self.log_writer.writerow([self.user_id, presented_text, transcribed_text, presented_characters, transcribed_characters,
                                 time/1000, wpm])

    def eventLog(self, event_type, event_):
        timestamp = self.timestamp()
        self.log_writer.writerow([event_type, event_, timestamp])

    def timestamp(self):
        return QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)

    def wordsPerMinute(self, text, time):
        words = text.split()
        word_length = (len(words) - 1 + sum(len(word) for word in words)) / len(words)
        wpm = len(text) / (time / 1000) * 60 / word_length
        return wpm


class TypingTest(QtWidgets.QWidget):

    def __init__(self, model):
        super(TypingTest, self).__init__()
        self.model = model
        self.initUI()
        self.__edit_text = AutoCompleter(model)
        self.__setup_completer()

    def __setup_completer(self):
        if self.model.use_completer:
            #wordList = ['Hallo', 'was', 'geht?', 'Noch', 'ein', 'Satz', 'zum', 'lesen.', 'Der', 'letzte', 'Satz', 'für', 'heute.']
            completer = QtWidgets.QCompleter(self.get_word_list(), self)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            completer.setWrapAround(False)
            self.__edit_text.set_completer(completer)

    def get_word_list(self):
        words_list = [] 
        for i in range(len(self.model.sentences)):
            words_list += self.model.sentences[i].replace(" ", "\n").split("\n")
        while '' in words_list:
            words_list.remove('')
        return words_list

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
        self.text_edit = QtWidgets.QTextEdit(self)
        layout = QVBoxLayout()
        layout.addWidget(self.rules)
        layout.addWidget(self.testtext)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        self.show()

    def updateText(self):
        self.testtext.setText(self.model.current_sentence)

    def keyReleaseEvent(self, event):
        if not self.model.testStarted:
            self.model.testStarted = True
            self.model.timer_word.start()

        if self.model.testStarted:
            if event.key() == QtCore.Qt.Key.Key_Space:
                self.model.eventLog( "word typed", self.model.word)
                self.model.word_times.append(self.model.timer_word.restart())
                self.model.word = ""
                self.model.sentence += " "
                event_ = "space"

            elif event.key() == QtCore.Qt.Key.Key_Return:
                self.model.eventLog("word typed", self.model.word)
                self.model.eventLog("sentence typed", self.model.sentence)
                self.model.word_times.append(self.model.timer_word.restart())
                self.model.setSentence()
                self.updateText()
                self.model.word = ""
                self.model.sentence = ""
                event_ = "return"

            elif event.key() == QtCore.Qt.Key.Key_Backspace:
                self.model.word = self.model.word[:-1]
                self.model.sentence = self.model.sentence[:-1]
                event_ = "backspace"

            else:
                char = event.text()
                self.model.word += char
                self.model.sentence += char
                event_ = char

            self.model.eventLog("key pressed", event_)


def main():
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) < 4:
        sys.stderr.write("you need to pass a textfile and the user id")
        sys.exit(1)
    model = TypingModel(parsedata(sys.argv[1]), sys.argv[2], parseconfig(sys.argv[3]))
    typing_test = TypingTest(model)
    sys.exit(app.exec_())


def parsedata(filename):
    sentences = []
    try:
        file = open(filename).readlines()
    except IOError:
        sys.stdout.write("Error: File does not appear to exist. Useddefault text instead")
        return ["This is default text.", "It can be used for testing."]
    for line in file:
        sentences.append(line)
    return sentences

def parseconfig(file):
    with open(str(file)) as f:
        setup_dict = json.load(f)
    if setup_dict["USE_COMPLETER"] == "yes":
        use_completer = True
    else:
        use_completer = False
    return use_completer

if __name__ == '__main__':
    main()
