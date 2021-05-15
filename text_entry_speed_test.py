#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
from PyQt5 import QtGui, QtCore, QtWidgets
import re

class TypingModel(object):

    def __init__(self, sentences, user_id):
        self.timer = QtCore.QTime()
        self.user_id = user_id
        self.sentences = sentences
        self.sentence_number = 0
        self.setSentence()
        self.log_writer = csv.writer(sys.stdout)

    def setSentence(self):
        if self.sentence_number < len(self.sentences):
            self.current_sentence = self.sentences[self.sentence_number]
            self.words = self.sentences[self.sentence_number].split()
            print(self.current_sentence)
            self.sentence_number += 1
        else:
            print("test done")


class TypingTest(QtWidgets.QTextEdit):
 
    def __init__(self, model):
        super(TypingTest, self).__init__()
        self.model = model
        self.initUI()
        
    def initUI(self):      
        self.setGeometry(0, 0, 400, 400)
        self.setWindowTitle('SuperText')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)
        self.show()


    def keyPressEvent(self, event):
        self.model.setSentence()
        print(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) < 3:
        sys.stderr.write("you need to pass a textfile and the user id")
        sys.exit(1)
    model = TypingModel(parsedata(sys.argv[1]), sys.argv[2])
    typing_test = TypingTest(model)
    sys.exit(app.exec_())


def parsedata(filename):
    sentences = []
    try:
        file = open(filename).readlines()
    except IOError:
        print("Error: File does not appear to exist. Useddefault text instead")
        return ["This is default text.", "It can be used for testing."]
    for line in file:
        sentences.append(line)
    return sentences
if __name__ == '__main__':
    main()
