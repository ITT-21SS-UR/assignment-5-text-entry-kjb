#https://doc.qt.io/qt-5/qstringlist.html
#https://doc.qt.io/qt-5/qtwidgets-tools-customcompleter-example.html
#https://www.howtobuildsoftware.com/index.php/how-do/IFK/python-3x-autocomplete-pyqt-qtextedit-pyqt5-pyqt5-qtextedit-auto-completion


from PyQt5 import QtWidgets, QtCore, QtGui

class AutoCompleter(QtWidgets.QTextEdit):

    def __init__(self, model, parent=None):
        super(AutoCompleter, self).__init__(parent)

        self.__model = model
        #self.__setup_ui()
        self.__completer = None

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

        self.__completer.activated.connect(self.__insert_completion)