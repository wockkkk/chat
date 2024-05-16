import sys
from socket import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import main_ui
import signin_ui
import signon_ui
import start_ui

setdefaulttimeout(1)
s = socket()
ip = ''
user = ''
password = ''
port = 8080
account_id = 0
connect = False
message_index = 0


def show(ui_class):
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui_class().setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())


class Signon(signon_ui.Ui_MainWindow):
    def signon(self, MainWindow):
        global ip, user, password, port, account_id, s, connect
        ip = self.lineEdit.text()
        user = self.lineEdit_2.text()
        password = self.lineEdit_3.text()
        print(ip, user, password, port)
        try:
            if not connect:
                s.connect((ip, port))
                connect = True
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


class Signin(signin_ui.Ui_MainWindow):
    def signin(self, MainWindow):
        global ip, user, password, port, account_id, s, connect
        if self.lineEdit_3.text() == self.lineEdit_4.text():
            ip = self.lineEdit.text()
            user = self.lineEdit_2.text()
            password = self.lineEdit_3.text()
            print(ip, user, password, port)
            try:
                if not connect:
                    s.connect((ip, port))
                    connect = True
                s.sendall(f'signin|{user}|{password}'.encode())
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
        else:
                self.user_wrong = QtWidgets.QMessageBox.warning(self.centralwidget, 'wrong user', 'wrong user')

    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)
        self.pushButton.clicked.connect(lambda: self.signin(MainWindow))

        
class Start(start_ui.Ui_MainWindow):
    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        m = MainWindow.findChild(QtWidgets.QMenuBar, 'menubar')
        if m is not None:
            m.deleteLater()
        super().setupUi(MainWindow)

    def combo_box(self, MainWindow):
        print(self.comboBox.currentIndex())
        if self.comboBox.currentIndex() == 0:
            Signon().setupUi(MainWindow)
            MainWindow.show()
        else:
            Signin().setupUi(MainWindow)
            MainWindow.show()

    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)
        self.pushButton.clicked.connect(lambda: self.combo_box(MainWindow))


class MainUi(main_ui.Ui_MainWindow):
    def signout(self, MainWindow):
        global account_id, ip, user, password, message_index
        account_id, ip, user, password, message_index = 0, '', '', '', 0
        Start().setupUi(MainWindow)
        MainWindow.show()

    def send_message(self):
        global s
        if self.lineEdit.text()[0] == '/':
            s.sendall(f'command|{self.lineEdit.text()[1:]}|{account_id}'.encode())
        else:
            s.sendall(f'send_message|{self.lineEdit.text()}|{account_id}'.encode())
        self.lineEdit.clear()

    def get_message(self):
        global s, message_index
        s.sendall(f'get_message|{message_index}'.encode())
        data = s.recv(1024).decode().split('|')
        if data[0] == '':
            return
        else:
            self.listWidget.addItem(data[0])
            message_index += 1

    def retranslateUi(self, MainWindow: QtWidgets.QMainWindow):
        super().retranslateUi(MainWindow)
        self.actionexit.triggered.connect(lambda: MainWindow.close())
        self.actionsignout.triggered.connect(lambda: self.signout(MainWindow))
        self.pushButton.clicked.connect(self.send_message)
        self.timer = QTimer()
        self.timer.timeout.connect(self.get_message)
        self.timer.start(250)


show(Start)
