#https://doc.qt.io/qt-5/qstringlist.html

#https://www.howtobuildsoftware.com/index.php/how-do/IFK/python-3x-autocomplete-pyqt-qtextedit-pyqt5-pyqt5-qtextedit-auto-completion

#code mainly from https://doc.qt.io/qt-5/qtwidgets-tools-customcompleter-example.html
# and https://github.com/baoboa/pyqt5/blob/master/examples/tools/customcompleter/customcompleter.py

from PyQt5 import QtWidgets, QtCore, QtGui

class AutoCompleter(QtWidgets.QTextEdit):

    def __init__(self, model, parent=None):
        super(AutoCompleter, self).__init__(parent)

        self.__model = model
        self.__setup_ui()
        self.__completer = None
    
    def __setup_ui(self):
        self.setGeometry(0, 0, 400, 400)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    #the setCompleter() function accepts a completer and sets it up
    def set_completer(self, completer):
        if self.__completer:
            self.disconnect(self)

        self.__completer = completer

        if not self.__completer:
            return

        self.__completer.setWidget(self)
        self.__completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.__completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.__completer.activated.connect(self.insertCompletion)

    #the insertCompletion() function is responsible for completing the word using a QTextCursor object
    def insertCompletion(self, completion):
        if self.__completer.widget() != self:
            return
        tc = self.textCursor()

        extra = len(completion) - len(self.__completer.completionPrefix())
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion.right(extra))
        self.setTextCursor(tc)
    
    #The textUnderCursor() function uses a QTextCursor, tc, to select a word under the cursor and return it
    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    #The TextEdit class reimplements focusInEvent() function, which is an event handler used to 
    #receive keyboard focus events for the widget
    def focusInEvent(self, event):
        if self.__completer:
            self.__completer.setWidget(self)

        super(AutoCompleter,self).focusInEvent(event)

    def keyPressEvent(self, e):
        if self._completer is not None and self._completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if e.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, 
            QtCore.Qt.Key_Escape, QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab):
                e.ignore()
                # Let the completer do default behavior.
                return

        isShortcut = ((e.modifiers() & QtCore.Qt.ControlModifier) != 0 and e.key() == QtCore.Qt.Key_E)
        if self._completer is None or not isShortcut:
            # Do not process the shortcut when we have a completer.
            super(AutoCompleter, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier)
        if self._completer is None or (ctrlOrShift and len(e.text()) == 0):
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        hasModifier = (e.modifiers() != QtCore.Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()

        if not isShortcut and (hasModifier or len(e.text()) == 0 or len(completionPrefix) < 3 or e.text()[-1] in eow):
            self._completer.popup().hide()
            return

        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(
                    self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)

    def keyReleaseEvent(self, event):
        print("key release novel")
