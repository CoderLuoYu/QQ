import re
import sqlite3
import sys
from datetime import datetime
import webbrowser
from time import sleep
from main_window import MainWindow

from PyQt6.QtCore import QPoint, Qt, QDate
from PyQt6.QtGui import QPixmap, QIcon, QImage, QTextCursor
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QLineEdit, QMessageBox, QFileDialog, QMenu, QInputDialog, QTreeWidgetItem, \
    QListWidgetItem, QProgressBar

from PyQt6 import uic


class LoginInterfaceWindow:
    def __init__(self):
        # 加载ui文件
        self.login_interface_window = uic.loadUi("login_interface_window.ui")
        self.login_interface_window.setWindowTitle("用户登录界面")

        # 登录按钮
        self.login_interface_window.login_button.clicked.connect(self.on_login)
        # 重置按钮
        self.login_interface_window.reset_button.clicked.connect(self.on_reset)
        # 注册按钮
        # self.login_interface_window.register_button.clicked.connect(self.show_register_window)
        # 密码显示模式
        self.login_interface_window.showpass_box.stateChanged.connect(self.toggle_login_password_visibility)
        # 修改密码
        # self.login_interface_window.reset_password.mousePressEvent = self.show_reset_password_window

    def show_login_window(self):
        self.login_interface_window.show()

    def close_login_window(self):
        self.login_interface_window.close()

    def on_login(self):
        # 获取用户名和密码
        self.__QQ_number = self.login_interface_window.QQ_number_edit.text()
        self.__password = self.login_interface_window.pass_edit.text()
        # 获取数据库中的账户
        try:
            conn = sqlite3.connect('user_account.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT QQ_number, password, init_flag FROM ACCOUNT_INFOR"
                           f" WHERE QQ_number={self.__QQ_number}")
            tables = cursor.fetchall()
            conn.close()
            table = tables[0]
        except IndexError:
            QMessageBox.critical(self.login_interface_window, "提示", "登录失败，用户名或密码不正确")
        else:
            # 检查用户名和密码是否正确
            if self.__QQ_number == table[0] and self.__password == table[1]:
                QMessageBox.information(self.login_interface_window, "提示", "登录成功")
                self.on_reset()
                if table[2] == 1:
                    # 隐藏登录界面的所有组件
                    # while self.login_interface_window.Layout_1.count():
                    #     item = self.login_interface_window.Layout_1.takeA0t(0)
                    #     widget = item.widget()
                    #     if widget:
                    #         widget.hide()
                    # while self.login_interface_window.Layout_2.count():
                    #     item = self.login_interface_window.Layout_2.takeAt(0)
                    #     widget = item.widget()
                    #     if widget:
                    #         widget.hide()
                    # while self.login_interface_window.Layout_3.count():
                    #     item = self.login_interface_window.Layout_3.takeAt(0)
                    #     widget = item.widget()
                    #     if widget:
                    #         widget.hide()
                    # while self.login_interface_window.Layout_4.count():
                    #     item = self.login_interface_window.Layout_4.takeAt(0)
                    #     widget = item.widget()
                    #     if widget:
                    #         widget.hide()
                    # # 进度条
                    # login_progressbar = QProgressBar(self.login_interface_window)
                    # login_progressbar.resize(300, 30)
                    # login_progressbar.move(80, 100)
                    # login_progressbar.setRange(0, 10)
                    # login_progressbar.show()
                    # for i in range(1, 11):
                    #     sleep(1)
                    #     login_progressbar.setValue(i)
                    # # 打开主窗口
                    # sleep(1)
                    login_window.close_login_window()
                    window = MainWindow(self.__QQ_number, self.__password)
                    window.show_main_window()
                else:
                    pass
                    # self.show_init_identify_infor_window()
                self.login_interface_window.close()
            else:
                QMessageBox.critical(self.login_interface_window, "提示", "登录失败，用户名或密码不正确")
                self.on_reset()

    def on_reset(self):
        # 清空用户名和密码输入框
        self.login_interface_window.QQ_number_edit.clear()
        self.login_interface_window.pass_edit.clear()

    def toggle_login_password_visibility(self, state):
        if state == Qt.CheckState.Checked.value:
            self.login_interface_window.pass_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.login_interface_window.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)


app = QApplication([])
login_window = LoginInterfaceWindow()
login_window.show_login_window()
sys.exit(app.exec())

