#https://doc.qt.io/qt-5/qstringlist.html

#https://www.howtobuildsoftware.com/index.php/how-do/IFK/python-3x-autocomplete-pyqt-qtextedit-pyqt5-pyqt5-qtextedit-auto-completion

#code mainly from https://doc.qt.io/qt-5/qtwidgets-tools-customcompleter-example.html

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
        print("test")
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


    def keyReleaseEvent(self, event):
        print("key release novel")
