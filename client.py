import sys
from socket import *
from PyQt5 import QtWidgets
import main_ui
import signin_ui
import signon_ui
import start_ui

setdefaulttimeout(0.25)
s = socket()
ip = ''
user = ''
password = ''
port = 8080
account_id = 0


def show(ui_class):
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui_class().setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())


class Signon(signon_ui.Ui_MainWindow):
    def signon(self, MainWindow):
        global ip, user, password, port, account_id, s
        ip = self.lineEdit.text()
        user = self.lineEdit_2.text()
        password = self.lineEdit_3.text()
        print(ip, user, password, port)
        try:
            s.connect((ip, port))
            s.sendall(f'signon|{user}|{password}'.encode())
            data = s.recv(1024).decode().split('|')
            if data[0] == 'r':
                account_id = int(data[1])
                MainUi().setupUi(MainWindow)
                MainWindow.show()
            else:
                self.user_wrong = QtWidgets.QMessageBox.warning(self.centralwidget, 'wrong user', 'wrong user')
            print(ip, user, password, port, account_id)
        except OSError:
            self.error = QtWidgets.QMessageBox.critical(self.centralwidget, 'Error', 'Server not found')

    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)
        self.pushButton.clicked.connect(lambda: self.signon(MainWindow))


class Start(start_ui.Ui_MainWindow):
    def combo_box(self, MainWindow):
        print(self.comboBox.currentIndex())
        if self.comboBox.currentIndex() == 0:
            Signon().setupUi(MainWindow)
            MainWindow.show()
        else:
            signin_ui.Ui_MainWindow().setupUi(MainWindow)
            MainWindow.show()

    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)
        self.pushButton.clicked.connect(lambda: self.combo_box(MainWindow))

class MainUi(main_ui.Ui_MainWindow):
    def signout(self, MainWindow):
        global account_id, ip, user, password
        account_id, ip, user, password = 0, '', '', ''
        Start().setupUi(MainWindow)
        MainWindow.show()

    def send_message(self):
        global s
        if self.lineEdit.toPlainText()[0] == '/':
            s.sendall(f'command|{self.lineEdit.toPlainText()[1:]}|{account_id}'.encode())
        else:
            s.sendall(f'send_message|{self.lineEdit.toPlainText()}|{account_id}'.encode())
        self.lineEdit.clear()

    def retranslateUi(self, MainWindow: QtWidgets.QMainWindow):
        super().retranslateUi(MainWindow)
        self.actionexit.triggered.connect(lambda: MainWindow.close())
        self.actionsignout.triggered.connect(lambda: self.signout(MainWindow))
        self.pushButton.clicked.connect(self.send_message)


show(Start)
