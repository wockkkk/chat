import sys
from socket import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import main_ui
import signin_ui
import signon_ui
import start_ui
import json

from socket import gethostname

setdefaulttimeout(20)
s = socket()
ip = ''
user = ''
password = ''
port = 8080
account_id = 0
connect = False
message_index = 0
localhost = ['localhost', '127.0.0.1']


def show(ui_class):
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui_class().setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())


class Signon(signon_ui.Ui_MainWindow):
    def signon(self, main_window):
        global ip, user, password, port, account_id, s, connect
        ip = self.lineEdit.text()
        if ip in localhost:
            ip = gethostname()
        user = self.lineEdit_2.text()
        password = self.lineEdit_3.text()
        print(ip, user, password, port)
        try:
            if not connect:
                s.connect((ip, port))
                connect = True
            s.sendall(json.dumps(['signon', user, password]).encode())
            data = json.loads(s.recv(1024))
            if data[0] == 'r':
                account_id = int(data[1])
                MainUi().setupUi(main_window)
                main_window.show()
            else:
                QtWidgets.QMessageBox.warning(self.centralwidget, 'wrong user', 'wrong user')
            print(ip, user, password, port, account_id)
        except OSError:
            QtWidgets.QMessageBox.critical(self.centralwidget, 'Error', 'Server not found')
            connect = False

    def st(self, main_window):
        Start().setupUi(main_window)
        main_window.show()

    def show(self):
        if self.checkBox.isChecked():
            self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Password)

    def retranslateUi(self, main_window):
        super().retranslateUi(main_window)
        self.pushButton.clicked.connect(lambda: self.signon(main_window))
        self.pushButton_2.clicked.connect(lambda: self.st(main_window))
        self.checkBox.stateChanged.connect(self.show)


class Signin(signin_ui.Ui_MainWindow):
    def signin(self, main_window):
        global ip, user, password, port, account_id, s, connect
        if self.lineEdit_3.text() == self.lineEdit_4.text():
            ip = self.lineEdit.text()
            if ip in localhost:
                ip = gethostname()
            user = self.lineEdit_2.text()
            password = self.lineEdit_3.text()
            print(ip, user, password, port)
            try:
                if not connect:
                    s.connect((ip, port))
                    connect = True
                s.sendall(json.dumps(['signin', user, password]).encode())
                data = json.loads(s.recv(1024))
                if data[0] == 'r':
                    account_id = int(data[1])
                    MainUi().setupUi(main_window)
                    main_window.show()
                elif data[0] == 'name error':
                    QtWidgets.QMessageBox.warning(self.centralwidget, 'wrong user', 'name error')
                else:
                    QtWidgets.QMessageBox.warning(self.centralwidget, 'wrong user', 'wrong user')
                print(ip, user, password, port, account_id)
            except OSError:
                QtWidgets.QMessageBox.critical(self.centralwidget, 'Error', 'Server not found')
                connect = False
        else:
            QtWidgets.QMessageBox.warning(self.centralwidget, 'wrong user', 'wrong user')

    def st(self, main_window):
        Start().setupUi(main_window)
        main_window.show()

    def show(self):
        if self.checkBox.isChecked():
            self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Password)
            self.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Password)

    def retranslateUi(self, main_window):
        super().retranslateUi(main_window)
        self.pushButton.clicked.connect(lambda: self.signin(main_window))
        self.pushButton_2.clicked.connect(lambda: self.st(main_window))
        self.checkBox.stateChanged.connect(self.show)


class Start(start_ui.Ui_MainWindow):
    def setupUi(self, main_window: QtWidgets.QMainWindow):
        m = main_window.findChild(QtWidgets.QMenuBar, 'menubar')
        if m is not None:
            m.deleteLater()
        super().setupUi(main_window)

    def combo_box(self, main_window):
        print(self.comboBox.currentIndex())
        if self.comboBox.currentIndex() == 0:
            Signon().setupUi(main_window)
            main_window.show()
        else:
            Signin().setupUi(main_window)
            main_window.show()

    def retranslateUi(self, main_window):
        super().retranslateUi(main_window)
        self.pushButton.clicked.connect(lambda: self.combo_box(main_window))


class MainUi(main_ui.Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.member_model = QStandardItemModel()  # 创建数据模型
        self.MemberView.setModel(self.member_model)  # 绑定到 QListView
    def signout(self, main_window):
        global account_id, ip, user, password, message_index
        account_id, ip, user, password, message_index = 0, '', '', '', 0
        Start().setupUi(main_window)
        main_window.show()

    def send_message(self):
        global s
        s.sendall(json.dumps(['send_message', self.textEdit.toPlainText(), account_id]).encode())
        self.textEdit.clear()

    def send_command(self):
        global s
        s.sendall(json.dumps(['command', self.textEdit.toPlainText(), account_id]).encode())
        self.textEdit.clear()

    def get_message(self):
        global s, message_index
        s.sendall(json.dumps(['get_message']).encode())
        data = s.recv(1024)
        print(data)
        data = json.loads(data)
        self.messageWidget.clear()
        self.messageWidget.addItems(data)

    def update_member_view(self, users):
        self.member_model.clear()  # 通过模型清空内容
        for name, perm in users:
            item = QStandardItem()
            item.setText(f"{name} [{'管理员' if perm >=1 else '用户'}]")
            self.member_model.appendRow(item)  # 通过模型添加项

    def get_online_users(self):
        global s
        s.sendall(json.dumps(['get_online_users']).encode())
        data = json.loads(s.recv(4096))
        self.update_member_view(data)

    def check(self):
        if self.typeBox.currentIndex() == 0:
            try:
                self.sendButton.clicked.disconnect()
            except TypeError:
                pass
            self.sendButton.clicked.connect(self.send_message)
        elif self.typeBox.currentIndex() == 1:
            try:
                self.sendButton.clicked.disconnect()
            except TypeError:
                pass
            self.sendButton.clicked.connect(self.send_command)

    def at_someone(self):
        pass

    def retranslateUi(self, main_window: QtWidgets.QMainWindow):
        super().retranslateUi(main_window)
        self.actionexit.triggered.connect(lambda: main_window.close())
        self.actionsignout.triggered.connect(lambda: self.signout(main_window))
        self.message_timer = QTimer()
        self.users_timer = QTimer()
        # noinspection PyUnresolvedReferences
        self.message_timer.timeout.connect(self.get_message)
        # noinspection PyUnresolvedReferences
        self.users_timer.timeout.connect(self.get_online_users)
        self.message_timer.start(50)
        self.users_timer.start(1000)
        self.MemberView.doubleClicked.connect(self.at_someone)
        self.typeBox.activated.connect(self.check)
        self.check()


show(Start)
