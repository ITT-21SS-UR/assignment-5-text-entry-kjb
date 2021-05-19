
"""
Work distribution was as follows:
handling of key events and creating overall structure mainly done by joshua benker, integrating completions into
TypingModel and review of script mainly done by kay brinkmann
"""

# https://doc.qt.io/qt-5/qstringlist.html

# https://www.howtobuildsoftware.com/index.php/how-do/IFK/python-3x-autocomplete-pyqt-qtextedit-pyqt5-pyqt5-qtextedit-auto-completion

# code mainly from https://doc.qt.io/qt-5/qtwidgets-tools-customcompleter-example.html
# and https://github.com/baoboa/pyqt5/blob/master/examples/tools/customcompleter/customcompleter.py

# script was created by both team members

from PyQt5 import QtWidgets, QtCore, QtGui


class TextEdit(QtWidgets.QTextEdit):

    def __init__(self, model, parent=None):
        super(TextEdit, self).__init__(parent)

        self.__model = model
        self.__completer = None

    # the setCompleter() function accepts a completer and sets it up
    def set_completer(self, completer):

        if self.__completer:
            self.disconnect(self)
        if self.__model.use_completer:
            self.__completer = completer

        if not self.__completer:
            return

        self.__completer.setWidget(self)
        self.__completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.__completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.__completer.activated.connect(self.insertCompletion)

    # the insertCompletion() function is responsible for completing the word using a QTextCursor object
    def insertCompletion(self, completion):
        if self.__completer.widget() != self:
            return
        tc = self.textCursor()

        extra = len(completion) - len(self.__completer.completionPrefix())
        if extra != 0:
            tc.movePosition(QtGui.QTextCursor.Left)
            tc.movePosition(QtGui.QTextCursor.EndOfWord)
            tc.insertText(completion[-extra:])
            self.setTextCursor(tc)
            self.__model.word += completion[-extra:]
            self.__model.sentence += completion[-extra:]
            self.__model.eventLog("completed word", completion)
    
    # The textUnderCursor() function uses a QTextCursor, tc, to select a word under the cursor and return it
    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def popUpVisible(self):
        if self.__completer and self.__completer.popup().isVisible():
            return True
        else:
            return False

    # The TextEdit class reimplements focusInEvent() function, which is an event handler used to
    # receive keyboard focus events for the widget
    def focusInEvent(self, event):
        if self.__completer:
            self.__completer.setWidget(self)

        super(TextEdit, self).focusInEvent(event)

    # handles keypress events and completer
    def keyPressEvent(self, event):
        if not self.__model.testStarted:
            self.__model.testStarted = True
            self.__model.timer_word.start()

        if self.__model.testStarted:
            if event.key() == QtCore.Qt.Key.Key_Space:
                self.__model.eventLog("word typed", self.__model.word)
                self.__model.word_times.append(self.__model.timer_word.restart())
                self.__model.word = ""
                self.__model.sentence += " "
                self.__model.eventLog("key pressed", "space")

            elif event.key() == QtCore.Qt.Key.Key_Return:
                if not self.popUpVisible():
                    self.__model.eventLog("word typed", self.__model.word)
                    self.__model.eventLog("sentence typed", self.__model.sentence)
                    self.__model.word_times.append(self.__model.timer_word.restart())
                    self.__model.setSentence()
                    self.__model.sentence = ""
                    self.__model.word = ""
                    self.__model.eventLog("key pressed", "return")

            elif event.key() == QtCore.Qt.Key.Key_Backspace:
                self.__model.word = self.__model.word[:-1]
                self.__model.sentence = self.__model.sentence[:-1]
                self.__model.eventLog("key pressed", "backspace")

            else:
                char = event.text()
                self.__model.word += char
                self.__model.sentence += char
                self.__model.eventLog("key pressed", char)

        if self.__completer is not None and self.__completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return,
                               QtCore.Qt.Key_Escape, QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab):
                event.ignore()
                # Let the completer do default behavior.
                return

        isShortcut = ((event.modifiers() & QtCore.Qt.ControlModifier) != 0 and event.key() == QtCore.Qt.Key_Minus)
        if self.__completer is None or not isShortcut:
            # Do not process the shortcut when we have a completer.
            super(TextEdit, self).keyPressEvent(event)

        ctrlOrShift = event.modifiers() & (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier)
        if self.__completer is None or (ctrlOrShift and len(event.text()) == 0):
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        hasModifier = (event.modifiers() != QtCore.Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()

        # changed minimum character count to 2
        if not isShortcut and (hasModifier or len(event.text()) == 0 or
                               len(completionPrefix) < 2 or event.text()[-1] in eow):
            self.__completer.popup().hide()
            return

        if completionPrefix != self.__completer.completionPrefix():
            self.__completer.setCompletionPrefix(completionPrefix)
            self.__completer.popup().setCurrentIndex(
                    self.__completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self.__completer.popup().sizeHintForColumn(0) +
                    self.__completer.popup().verticalScrollBar().sizeHint().width())
        self.__completer.complete(cr)
