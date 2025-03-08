import re
import sqlite3
import sys
from datetime import datetime
import webbrowser
from time import sleep

from PyQt6.QtCore import QPoint, Qt, QDate
from PyQt6.QtGui import QPixmap, QIcon, QImage, QTextCursor
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QLineEdit, QMessageBox, QFileDialog, QMenu, QInputDialog, QTreeWidgetItem, \
    QListWidgetItem, QProgressBar

from PyQt6 import uic


class MainWindow:
    def __init__(self, qq_number, password):
        self.main_window = uic.loadUi("main_window.ui")
        self.main_window.setWindowTitle("QQ")

        # 从数据库中读取的QQ号和密码
        self.__QQ_number = qq_number
        self.__password = password
        # 用户头像路径
        self.head_portrait_file_path = ""
        # 发消息时所选的图片的路径
        self.image_paths = []
        # 所选好友昵称
        self.name = ""
        # 聊天项列表
        self.chat_item = []
        # 聊天列表项与对应QQ号\群号的字典
        self.chat_list = {}
        # 当前所选聊天项
        self.selected_chat_item = None
        # 好友列表项与对应QQ号的字典
        self.friend_list = {}
        # 当前所选好友项
        self.selected_friend_item = None
        # 群聊列表项与对应群号的字典
        self.chatroom_list = {}
        # 当前所选群聊项
        self.selected_chatroom_item = None
        # 星期对照表
        self.weekday = {
            "1": "周一",
            "2": "周二",
            "3": "周三",
            "4": "周四",
            "5": "周五",
            "6": "周六",
            "0": "周日"
        }
        # 创建群聊时所选好友个数
        self.item_count = 0
        # 创建群聊时已被选中的好友项与选中列表的对应字典
        self.selected_item = {}
        # 搜索添加新好友时所显示的搜索结果列表与QQ号的对应字典
        self.add_friend_list_QQ = {}
        # 搜索添加新好友时所显示的搜索结果列表与头像的对应字典
        self.add_friend_list_portrait = {}
        # 用户/函数修改好友备注框的标记
        self.tra_friend_remark_flag = True
        # 用户/函数修改好友分组的标记
        self.tra_friend_grouping_flag = True
        # 用户/函数修改群备注的标记
        self.tra_chatroom_remark_flag = True
        # 用户/函数修改我的群昵称标记
        self.tra_chatroom_myself_name = True

        # 头像
        self.main_window.head_portrait.clicked.connect(self.head_portrait_page)
        # 聊天
        self.main_window.chat_box.clicked.connect(self.chat_page)
        # 联系人
        self.main_window.linkman.clicked.connect(self.linkman_page)
        # 聊天项
        self.main_window.chat_list.itemClicked.connect(self.chat_edit)
        # 文件管理
        self.main_window.file.clicked.connect(self.head_portrait_page)
        # 设置
        self.main_window.set.clicked.connect(self.show_set_menu)
        # 聊天列表菜单
        self.main_window.chat_list.customContextMenuRequested.connect(self.show_chat_list_menu)
        # 好友列表菜单
        self.main_window.friend_list.customContextMenuRequested.connect(self.show_friend_list_menu)
        # 个人资料
        # self.main_window.edit_button.clicked.connect(self.show_identify_infor_window)
        # 加好友/群按钮
        self.main_window.add_button.clicked.connect(self.show_add_menu)
        # 好友个人资料
        self.main_window.friend_list.itemClicked.connect(self.update_friend_infor)
        # 给好友点赞
        self.main_window.like_button.clicked.connect(self.give_like_to_friend)
        # 设置好友分组
        self.main_window.grouping.currentIndexChanged.connect(self.set_friend_grouping)
        # 设置好友备注
        self.main_window.remark_edit.textChanged.connect(self.set_friend_remark_name)
        # 给好友发消息
        self.main_window.send_message.clicked.connect(self.add_chat_item)
        # 群资料
        self.main_window.chatroom_list.itemClicked.connect(self.update_chatroom_infor)
        # 搜索框开始输入
        self.main_window.search_box.textEdited.connect(self.start_input)
        # 搜索好友/群聊
        self.main_window.search_box.textChanged.connect(self.search_added_friend_chatroom)
        # 添加搜索出的好友/群聊到聊天列表
        self.main_window.search_list.itemClicked.connect(self.add_searched_item)
        # 选择图片
        self.main_window.tupian.clicked.connect(self.choose_picture)
        # 发送按钮
        self.main_window.send_button.clicked.connect(self.send_context)

    def show_main_window(self):
        self.main_window.show()
        print(1)
        sleep(3)
        # 连接数据库读取个人资料数据
        conn = sqlite3.connect("user_account.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM ACCOUNT_INFOR WHERE QQ_number={self.__QQ_number}")
        tables = cursor.fetchall()
        conn.close()
        table = tables[0]
        user_image_pixmap = QPixmap(f"{table[3]}")
        new_user_image_pixmap = user_image_pixmap.scaled(50, 50,
                                                         Qt.AspectRatioMode.KeepAspectRatio,
                                                         Qt.TransformationMode.SmoothTransformation)
        icon = QIcon(new_user_image_pixmap)
        # 设置头像
        self.main_window.head_portrait.setIcon(icon)
        self.main_window.head_portrait.setIconSize(new_user_image_pixmap.size())
        sleep(3)
        # 设置按钮贴图
        self.main_window.chat_box.setIcon(QIcon(r"贴图/liaotian_pressed.png"))
        sleep(3)
        # 加载聊天列表
        self.update_chat_list()
        sleep(3)
        print(2)

    def update_identify_infor(self):
        # 个人资料
        # 连接数据库读取个人资料数据
        conn = sqlite3.connect("user_account.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM ACCOUNT_INFOR WHERE QQ_number={self.__QQ_number}")
        tables = cursor.fetchall()
        conn.close()
        table = tables[0]
        user_image_pixmap = QPixmap(f"{table[3]}")
        new_user_image_pixmap = user_image_pixmap.scaled(50, 50,
                                                         Qt.AspectRatioMode.KeepAspectRatio,
                                                         Qt.TransformationMode.SmoothTransformation)
        self.main_window.head_label.setPixmap(new_user_image_pixmap)
        self.main_window.name.setText(table[4])
        self.main_window.qq_number.setText("QQ "+table[0])
        self.main_window.sex.setText(table[5])
        self.main_window.age.setText(table[6])
        self.main_window.birthday.setText(table[7])
        self.main_window.address.setText(table[8])
        self.main_window.signature.setText(table[9])

    def update_chat_list(self):
        # 初始化
        # 清空聊天列表
        self.main_window.chat_list.clear()
        # 清空聊天列表对应的字典
        self.chat_list.clear()

        # 加载聊天列表
        conn = sqlite3.connect("chat_list.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT QQ_number, name, remark_name, portrait FROM _{self.__QQ_number} ORDER BY `index` ASC")
        tables = cursor.fetchall()
        conn.close()
        try:
            for i in range(len(tables)):
                infor = tables[i]
                qq_number = infor[0]
                name = infor[1]
                remark_name = infor[2]
                portrait = infor[3]
                chat_item = QListWidgetItem()
                if remark_name:
                    chat_item.setText(remark_name)
                else:
                    chat_item.setText(name)
                chat_item.setIcon(QIcon(portrait))
                self.main_window.chat_list.addItem(chat_item)
                self.chat_item.append(qq_number)
                self.chat_list[f"{chat_item}"] = qq_number
        except IndexError:
            pass

    def update_friend_list(self):
        # 初始化
        # 清空好友列表
        self.main_window.friend_list.clear()
        # 清空好友列表对应字典
        self.friend_list.clear()

        # 加载好友列表
        # #分组
        conn = sqlite3.connect("user_account.db")
        cursor = conn.cursor()
        cursor.execute("SELECT friend_groups FROM ACCOUNT_INFOR WHERE QQ_number=?", (self.__QQ_number,))
        tables = cursor.fetchall()
        conn.close()
        table = tables[0]
        friend_groups = table[0].split(",")
        for group in friend_groups:
            item = QTreeWidgetItem()
            # 设置分组名称
            item.setText(0, group)
            # 设置分组子项个数
            item.setText(1, "0")
            self.main_window.friend_list.addTopLevelItem(item)
        # #列表项
        for i in range(self.main_window.friend_list.topLevelItemCount()):
            text = self.main_window.friend_list.topLevelItem(i).text(0)
            conn = sqlite3.connect("friend_list.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT QQ_number, name, remark_name, portrait FROM _{self.__QQ_number} WHERE grouping=?",
                           (text, ))
            tables = cursor.fetchall()
            conn.close()
            for table in tables:
                friend_item = QTreeWidgetItem()
                # 判断是否有好友备注
                if table[2] is not None and table[2] != "":
                    friend_item.setText(0, f"{table[2]}({table[1]})")
                else:
                    friend_item.setText(0, table[1])
                # 设置好友头像
                friend_item.setIcon(0, QIcon(table[3]))
                self.main_window.friend_list.topLevelItem(i).addChild(friend_item)
                self.main_window.friend_list.topLevelItem(i).setText(1, str(len(tables)))
                self.friend_list[f"{friend_item}"] = table[0]

    def update_chatroom_list(self):
        # 初始化
        # 清空群聊列表
        for i in range(self.main_window.chatroom_list.topLevelItemCount()):
            for e in range(self.main_window.chatroom_list.topLevelItem(i).childCount()):
                self.main_window.chatroom_list.topLevelItem(i).takeChild(e)
        # 清空群聊列表对应字典
        self.chatroom_list.clear()

        # 加载群聊列表
        for i in range(self.main_window.chatroom_list.topLevelItemCount()):
            text = self.main_window.chatroom_list.topLevelItem(i).text(0)
            conn = sqlite3.connect("chatroom_list.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT chatroom_number, chatroom_name, remark_name, portrait FROM _{self.__QQ_number}"
                           f" WHERE grouping=?", (text,))
            tables = cursor.fetchall()
            conn.close()
            for table in tables:
                chatroom_item = QTreeWidgetItem()
                if table[2] is not None and table[2] != "":
                    chatroom_item.setText(0, f"{table[2]}")
                else:
                    chatroom_item.setText(0, table[1])
                chatroom_item.setIcon(0, QIcon(table[3]))
                self.main_window.chatroom_list.topLevelItem(i).addChild(chatroom_item)
                self.main_window.chatroom_list.topLevelItem(i).setText(1, str(len(tables)))
                self.chatroom_list[f"{chatroom_item}"] = table[0]

    def update_friend_infor(self, item):
        # 定义所选好友项
        self.selected_friend_item = item
        # 定义好友列表的顶层项的列表
        toplevel_item = [self.main_window.friend_list.topLevelItem(i)
                         for i in range(self.main_window.friend_list.topLevelItemCount())]
        if item not in toplevel_item:
            # 将主界面右侧翻到好友信息显示页面
            self.main_window.right_page.setCurrentIndex(3)
            # 连接数据库获取好友信息
            conn = sqlite3.connect("user_account.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT friend_groups FROM ACCOUNT_INFOR WHERE QQ_number=?", (self.__QQ_number,))
            tables = cursor.fetchall()
            conn.close()
            table = tables[0]
            friend_groups = table[0].split(",")
            qq_number = self.friend_list[f"{item}"]
            conn = sqlite3.connect("user_account.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM ACCOUNT_INFOR WHERE QQ_number=?", (qq_number,))
            tables = cursor.fetchall()
            conn.close()
            table = tables[0]
            user_image_pixmap = QPixmap(f"{table[3]}")
            new_user_image_pixmap = user_image_pixmap.scaled(100, 100,
                                                             Qt.AspectRatioMode.KeepAspectRatio,
                                                             Qt.TransformationMode.SmoothTransformation)
            # 设置头像，昵称，QQ号，点赞数，性别，年龄，生日，所在地，个性签名
            self.main_window.friend_portrait.setPixmap(new_user_image_pixmap)           # 头像
            self.main_window.friend_name.setText(table[4])                              # 昵称
            self.main_window.friend_qq_number.setText("QQ " + table[0])                 # QQ号
            self.main_window.like_number.setText(str(table[19]))                        # 获赞数
            self.main_window.friend_sex.setText(table[5])                               # 性别
            self.main_window.friend_age.setText(table[6])                               # 年龄
            self.main_window.friend_birthday.setText(table[7])                          # 生日
            self.main_window.friend_address.setText(table[8])                           # 所在地
            self.main_window.friend_signature.setText(table[9])                         # 个性签名
            # 设置分组项
            conn = sqlite3.connect("friend_list.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT grouping FROM _{self.__QQ_number} WHERE QQ_number=?", (qq_number,))
            tables = cursor.fetchall()
            grouping = tables[0][0]
            conn.close()
            items = friend_groups[1:]
            self.tra_friend_grouping_flag = False
            if self.main_window.grouping.count() == 0:
                self.main_window.grouping.addItems(items)
            # 设置好友分组
            if grouping in friend_groups:
                current_index = friend_groups.index(grouping)-1
            else:
                current_index = 0
            self.main_window.grouping.setCurrentIndex(current_index)
            self.tra_friend_grouping_flag = True
            # 设置好友备注
            conn = sqlite3.connect("chat_list.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT remark_name FROM _{self.__QQ_number} WHERE QQ_number=?", (qq_number,))
            tables = cursor.fetchall()
            conn.close()
            self.tra_friend_remark_flag = False
            if tables:
                remark_name = tables[0][0]
                self.main_window.remark_edit.setText(remark_name)
            else:
                self.main_window.remark_edit.clear()
            self.tra_friend_remark_flag = True

    def update_chatroom_infor(self, item):
        # 定义所选群聊项
        self.selected_chatroom_item = item
        # 定义群聊列表的顶层项的列表
        toplevel_item = [self.main_window.chatroom_list.topLevelItem(i)
                         for i in range(self.main_window.chatroom_list.topLevelItemCount())]
        # 定义群号
        chatroom_number = self.chatroom_list[f"{item}"]
        if item not in toplevel_item:
            # 将主界面右侧翻到群聊信息显示页面
            self.main_window.right_page.setCurrentIndex(4)
            # 连接数据库获取群聊信息
            conn = sqlite3.connect("chatroom_list.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT remark_name,myself_name FROM _{self.__QQ_number} WHERE chatroom_number=?",
                           (chatroom_number,))
            tables = cursor.fetchall()
            conn.close()
            table = tables[0]
            # 设置群备注
            self.tra_chatroom_remark_flag = False
            if table[0]:
                remark_name = table[0]
                self.main_window.chatroom_remark_name.setText(remark_name)
            else:
                self.main_window.chatroom_remark_name.clear()
            self.tra_chatroom_remark_flag = True
            # 设置我的本群昵称
            self.tra_chatroom_myself_name = False
            if table[1]:
                myself_name = table[1]
                self.main_window.myself_name.setText(myself_name)
            else:
                self.main_window.myself_name.clear()
            self.tra_chatroom_myself_name = True
            conn = sqlite3.connect("chatroom.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM CHATROOM WHERE chatroom_number=?", (chatroom_number,))
            tables = cursor.fetchall()
            conn.close()
            table = tables[0]
            user_image_pixmap = QPixmap(f"{table[2]}")
            new_user_image_pixmap = user_image_pixmap.scaled(100, 100,
                                                             Qt.AspectRatioMode.KeepAspectRatio,
                                                             Qt.TransformationMode.SmoothTransformation)
            # 设置群头像，群名称，群号，群介绍，群公告
            self.main_window.chatroom_portrait.setPixmap(new_user_image_pixmap)  # 群头像
            self.main_window.chatroom_name.setText(table[1])  # 群名称
            self.main_window.chatroom_number.setText("群号 " + table[0])  # 群号
            self.main_window.introduce.setText(table[4])    # 群介绍
            # self.main_window.advice.
            # 设置群成员

    def update_chat_records(self):
        now_time = datetime.now()
        # 清空聊天记录
        self.main_window.output_textbox.clear()
        # 聊天记录显示
        try:
            # 连接数据库读取数据
            conn = sqlite3.connect("chatting_records.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM _{self.__QQ_number} WHERE QQ_number=? ORDER BY time ASC",
                           (self.chat_list[f"{self.selected_chat_item}"],))
            tables = cursor.fetchall()
            # 遍历每一条聊天记录并加载
            last_time = None
            for table in tables:
                time = datetime.fromtimestamp(table[2])
                day = (now_time - time).days
                hour = int(time.strftime("%H"))
                minute = int(time.strftime("%M"))
                second = int(time.strftime("%S"))
                weekday_1 = now_time.strftime("%w")
                weekday_2 = time.strftime("%w")
                year_1 = now_time.strftime("%Y")
                year_2 = time.strftime("%Y")
                # 时间显示模块
                # 今天
                if int(now_time.strftime("%m")) == int(time.strftime("%m")) and\
                        int(now_time.strftime("%d")) - int(time.strftime("%d")) == 0:
                    if (0 < hour < 5) or (hour == 5 and minute == 0 and second == 0):
                        time_text = time.strftime("凌晨%H:%M")
                    elif (hour == 5 and (minute != 0 or second != 0)) or (5 < hour < 11) or\
                            (hour == 11 and minute == 0 and second == 0):
                        time_text = time.strftime("上午%H:%M")
                    elif (hour == 11 and (minute != 0 or second != 0)) or (11 < hour < 13) or\
                            (hour == 13 and minute == 0 and second == 0):
                        time_text = time.strftime("中午%H:%M")
                    elif (hour == 13 and (minute != 0 or second != 0)) or (13 < hour < 18) or\
                            (hour == 18 and minute == 0 and second == 0):
                        time_text = time.strftime("下午%H:%M")
                    elif (hour == 18 and (minute != 0 or second != 0)) or (18 < hour < 24):
                        time_text = time.strftime("晚上%H:%M")
                # 昨天
                elif int(now_time.strftime("%m")) == int(time.strftime("%m")) and\
                        int(now_time.strftime("%d")) - int(time.strftime("%d")) == 1:
                    if (0 < hour < 5) or (hour == 5 and minute == 0 and second == 0):
                        time_text = time.strftime("昨天 凌晨%H:%M")
                    elif (hour == 5 and (minute != 0 or second != 0)) or (5 < hour < 11) or \
                            (hour == 11 and minute == 0 and second == 0):
                        time_text = time.strftime("昨天 上午%H:%M")
                    elif (hour == 11 and (minute != 0 or second != 0)) or (11 < hour < 13) or \
                            (hour == 13 and minute == 0 and second == 0):
                        time_text = time.strftime("昨天 中午%H:%M")
                    elif (hour == 13 and (minute != 0 or second != 0)) or (13 < hour < 18) or \
                            (hour == 18 and minute == 0 and second == 0):
                        time_text = time.strftime("昨天 下午%H:%M")
                    elif (hour == 18 and (minute != 0 or second != 0)) or (18 < hour < 24):
                        time_text = time.strftime("昨天 晚上%H:%M")
                # 同一周
                elif int(now_time.strftime("%m")) == int(time.strftime("%m")) and\
                        int(now_time.strftime("%d")) - int(time.strftime("%d")) <= 6 and weekday_2 > weekday_1:
                    if (0 < hour < 5) or (hour == 5 and minute == 0 and second == 0):
                        time_text = time.strftime(f"{self.weekday[weekday_2]} 凌晨%H:%M")
                    elif (hour == 5 and (minute != 0 or second != 0)) or (5 < hour < 11) or\
                            (hour == 11 and minute == 0 and second == 0):
                        time_text = time.strftime(f"{self.weekday[weekday_2]} 上午%H:%M")
                    elif (hour == 11 and (minute != 0 or second != 0)) or (11 < hour < 13) or\
                            (hour == 13 and minute == 0 and second == 0):
                        time_text = time.strftime(f"{self.weekday[weekday_2]} 中午%H:%M")
                    elif (hour == 13 and (minute != 0 or second != 0)) or (13 < hour < 18) or\
                            (hour == 18 and minute == 0 and second == 0):
                        time_text = time.strftime(f"{self.weekday[weekday_2]} 下午%H:%M")
                    elif (hour == 18 and (minute != 0 or second != 0)) or (18 < hour < 24):
                        time_text = time.strftime(f"{self.weekday[weekday_2]} 晚上%H:%M")
                # 一年内1
                elif day < 365 and int(year_1) - int(year_2) > 0:
                    if (0 < hour < 5) or (hour == 5 and minute == 0 and second == 0):
                        time_text = time.strftime("%m月%d日 凌晨%H:%M")
                    elif (hour == 5 and (minute != 0 or second != 0)) or (5 < hour < 11) or \
                            (hour == 11 and minute == 0 and second == 0):
                        time_text = time.strftime("%m月%d日 上午%H:%M")
                    elif (hour == 11 and (minute != 0 or second != 0)) or (11 < hour < 13) or \
                            (hour == 13 and minute == 0 and second == 0):
                        time_text = time.strftime("%m月%d日 中午%H:%M")
                    elif (hour == 13 and (minute != 0 or second != 0)) or (13 < hour < 18) or \
                            (hour == 18 and minute == 0 and second == 0):
                        time_text = time.strftime("%m月%d日 下午%H:%M")
                    elif (hour == 18 and (minute != 0 or second != 0)) or (18 < hour < 24):
                        time_text = time.strftime("%m月%d日 晚上%H:%M")
                # 一年以上
                elif day >= 365 or int(year_1) - int(year_2) > 0:
                    if (0 < hour < 5) or (hour == 5 and minute == 0 and second == 0):
                        time_text = time.strftime("%Y年%m月%d日 凌晨%H:%M")
                    elif (hour == 5 and (minute != 0 or second != 0)) or (5 < hour < 11) or \
                            (hour == 11 and minute == 0 and second == 0):
                        time_text = time.strftime("%Y年%m月%d日 上午%H:%M")
                    elif (hour == 11 and (minute != 0 or second != 0)) or (11 < hour < 13) or \
                            (hour == 13 and minute == 0 and second == 0):
                        time_text = time.strftime("%Y年%m月%d日 中午%H:%M")
                    elif (hour == 13 and (minute != 0 or second != 0)) or (13 < hour < 18) or \
                            (hour == 18 and minute == 0 and second == 0):
                        time_text = time.strftime("%Y年%m月%d日 下午%H:%M")
                    elif (hour == 18 and (minute != 0 or second != 0)) or (18 < hour < 24):
                        time_text = time.strftime("%Y年%m月%d日 晚上%H:%M")
                message = table[3]
                image_path = table[4]
                if last_time is None:
                    self.main_window.output_textbox.append(f"                                                          "
                                                           f"            {time_text}")
                    last_time = time
                elif last_time is not None and (time - last_time).seconds / 60 > 5:
                    self.main_window.output_textbox.append(f"                                                          "
                                                           f"            {time_text}")
                    last_time = time
                if image_path:
                    pixmap = QPixmap(image_path)
                    scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                    new_pixmap = QImage(scaled_pixmap)
                    if message != "":
                        self.main_window.output_textbox.append(f"我: ")
                        cursor = self.main_window.output_textbox.textCursor()
                        cursor.insertImage(new_pixmap)
                        message = "      " + message.replace("\n", "\n")
                        self.main_window.output_textbox.append(f"{message}\n")
                        self.main_window.input_textbox.clear()
                        self.image_paths = None
                    else:
                        cursor = self.main_window.output_textbox.textCursor()
                        self.main_window.output_textbox.append(f"我: ")
                        cursor.insertImage(new_pixmap)
                        self.main_window.input_textbox.clear()
                        self.image_paths = None
                else:
                    if message != "":
                        self.main_window.output_textbox.append(f"我: {message}\n")
                        self.main_window.input_textbox.clear()
                    else:
                        pass
            # 关闭数据库连接
            conn.close()
            # 将光标移动到聊天记录结尾
            text_cursor = self.main_window.output_textbox.textCursor()
            text_cursor.movePosition(QTextCursor.MoveOperation.End)
            self.main_window.output_textbox.ensureCursorVisible()
        except Exception:
            pass

    """界面切换函数"""
    def head_portrait_page(self):
        self.main_window.right_page.setCurrentIndex(2)
        self.update_identify_infor()

    def chat_page(self):
        self.main_window.left_page.setCurrentIndex(1)
        self.main_window.right_page.setCurrentIndex(0)
        self.main_window.chat_box.setIcon(QIcon(r"贴图/liaotian_pressed.png"))
        self.main_window.linkman.setIcon(QIcon(r"贴图\qqlianxiren.png"))

    def linkman_page(self):
        # 左侧翻到好友列表页面
        self.main_window.left_page.setCurrentIndex(0)
        # 右侧翻到初始页面
        self.main_window.right_page.setCurrentIndex(0)
        # 加载好友列表
        self.update_friend_list()
        # 加载群聊列表
        self.update_chatroom_list()
        # 更换按下按钮的贴图
        self.main_window.linkman.setIcon(QIcon(r"贴图\qqlianxiren_pressed.png"))
        self.main_window.chat_box.setIcon(QIcon(r"贴图\liaotian.png"))

    def chat_edit(self, item):
        # 定义被选中的聊天项
        self.selected_chat_item = item
        # 定义所选聊天项的名字
        self.name = item.text()
        # 设置窗口标题
        self.main_window.title_label.setText(self.name)
        # 翻到聊天页面
        self.main_window.right_page.setCurrentIndex(1)
        # 加载聊天记录
        self.update_chat_records()

    """功能函数"""
    def show_set_menu(self):
        set_menu = QMenu()
        set_menu.setStyleSheet("""QMenu{
                                    background-color:white;color:black;
                                  }
                                  QMenu::item:hover{
                                    background-color:gray;color:black;
                                  }
                                                                    """)
        option1 = set_menu.addAction(QIcon("daoru.png"), "导入历史消息")
        option2 = set_menu.addAction(QIcon("jilubeifen.png"), "聊天记录备份与恢复")
        option3 = set_menu.addAction(QIcon("gengxin.png"), "检查更新")
        option4 = set_menu.addAction(QIcon("bangzhu.png"), "帮助")
        option5 = set_menu.addAction(QIcon("suoding.png"), "锁定")
        option6 = set_menu.addAction(QIcon("shezhi1.png"), "设置")
        option7 = set_menu.addAction(QIcon("guanyu.png"), "关于")
        option8 = set_menu.addAction(QIcon("tuichu.png"), "退出账号")
        action = set_menu.exec(QPoint(int(self.main_window.frameGeometry().x()+self.main_window.set.pos().x())+50,
                                      int(self.main_window.frameGeometry().y()+self.main_window.set.pos().y())-100))
        # 导入历史消息
        if action == option1:
            reply = QMessageBox.question(self.main_window, '提示',
                                         "功能开发中，敬请期待！", QMessageBox.StandardButton.Yes |
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                pass
            else:
                pass
        # 聊天记录备份与恢复
        elif action == option2:
            reply = QMessageBox.question(self.main_window, '提示',
                                         "功能开发中，敬请期待！", QMessageBox.StandardButton.Yes |
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                pass
            else:
                pass
        # 检查更新
        elif action == option3:
            reply = QMessageBox.question(self.main_window, '提示',
                                         "当前为最新版本！", QMessageBox.StandardButton.Yes |
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                pass
            else:
                pass
        # 帮助
        elif action == option4:
            webbrowser.open("help_center.html")
        # 锁定
        elif action == option5:
            reply = QMessageBox.question(self.main_window, '提示',
                                         "功能开发中，敬请期待！", QMessageBox.StandardButton.Yes |
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                pass
            else:
                pass
        # 设置
        elif action == option6:
            reply = QMessageBox.question(self.main_window, '提示',
                                         "功能开发中，敬请期待！", QMessageBox.StandardButton.Yes |
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                pass
            else:
                pass
        # 关于
        elif action == option7:
            self.about_window.show()
        # 退出账号
        elif action == option8:
            reply = QMessageBox.question(self.main_window, '提示',
                                         "你确定要退出当前账号吗?", QMessageBox.StandardButton.Yes |
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.main_window.close()
                self.login_interface_window.show()
            else:
                pass

    def show_chat_list_menu(self, position):
        conn = sqlite3.connect("chat_list.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT `index` FROM _{self.__QQ_number}")
        tables = cursor.fetchall()
        item = self.main_window.chat_list.itemAt(position)
        index = self.main_window.chat_list.row(item)
        if item:
            right_click_menu = QMenu()
            right_click_menu.setStyleSheet("""QMenu{
                                                background-color:white;color:black;
                                              }
                                              QMenu::item:hover{
                                                background-color:gray;color:black;
                                              }
                                                                                """)
            option1 = right_click_menu.addAction(QIcon("zhiding.png"), "置顶")
            option2 = right_click_menu.addAction(QIcon("dakaidulichuangkou.png"), "打开独立聊天窗口")
            option3 = right_click_menu.addAction(QIcon("yichu.png"), "从消息列表中移除")
            action = right_click_menu.exec(self.main_window.chat_list.mapToGlobal(position))
            if action == option1:
                pass
                # 先移除后插入到第1列
                # self.main_window.chat_list.takeItem(self.main_window.chat_list.row(item))
                # self.main_window.chat_list.insertItem(0, item)
            elif action == option2:
                self.show_independent_chat_window(item)
            elif action == option3:
                cursor.execute(f"DELETE FROM _{self.__QQ_number} WHERE `index`=?",
                               (self.main_window.chat_list.row(item), ))
                for i in range(self.main_window.chat_list.row(item) + 1, len(tables)):
                    cursor.execute(f"UPDATE _{self.__QQ_number} SET `index`=? WHERE `index`=?", (i-1, i))
                conn.commit()
                conn.close()
                conn = sqlite3.connect("chatting_records.db")
                cursor = conn.cursor()
                cursor.execute(f"UPDATE _{self.__QQ_number} SET `index`=? WHERE `index`=?", ("", index))
                for i in range(index+1, len(tables)):
                    cursor.execute(f"UPDATE _{self.__QQ_number} SET `index`=? WHERE `index`=?", (i-1, i))
                conn.commit()
                conn.close()
                # 动态加载
                self.update_chat_list()
                # 获取项在列表中的矩形区域
                rect = self.main_window.chat_list.visualItemRect(self.main_window.chat_list.item(index))
                # 计算点击位置，这里点击项的中心位置
                click_pos = QPoint(rect.center())
                # 模拟鼠标左键点击
                QTest.mouseClick(self.main_window.chat_list.viewport(), Qt.MouseButton.LeftButton,
                                 Qt.KeyboardModifier.NoModifier, click_pos)

    def show_friend_list_menu(self, position):
        item = self.main_window.friend_list.itemAt(position)
        conn = sqlite3.connect("user_account.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT friend_groups FROM ACCOUNT_INFOR WHERE QQ_number=?", (self.__QQ_number,))
        tables = cursor.fetchall()
        table = tables[0]
        if item:
            right_click_menu = QMenu()
            right_click_menu.setStyleSheet("""QMenu{
                                                background-color:white;color:black;
                                              }
                                              QMenu::item:hover{
                                                background-color:gray;color:black;
                                              }
                                                                                """)
            if item.text(0) == "特别关心" or item.text(0) == "我的好友":
                option1 = right_click_menu.addAction(QIcon("tianjia.png"), "添加分组")
                action = right_click_menu.exec(self.main_window.friend_list.mapToGlobal(position))
                if action == option1:
                    new_friend_item = QTreeWidgetItem(self.main_window.friend_list)
                    item_name, ok = QInputDialog.getText(self.main_window, "添加分组", "请输入名称：")
                    if ok:
                        new_friend_item.setText(0, item_name)
                        new_friend_item.setText(1, "0")
                        friend_groups = table[0]+","+item_name
                        conn.execute("UPDATE ACCOUNT_INFOR SET friend_groups=? WHERE QQ_number=?",
                                     (friend_groups, self.__QQ_number))
                        conn.close()
                        # 动态加载
                        self.update_friend_list()
            else:
                option1 = right_click_menu.addAction(QIcon("tianjia.png"), "添加分组")
                option2 = right_click_menu.addAction(QIcon("chongmingming.png"), "重命名分组")
                option3 = right_click_menu.addAction(QIcon("yichu.png"), "删除分组")
                action = right_click_menu.exec(self.main_window.friend_list.mapToGlobal(position))
                if action == option1:
                    new_friend_item = QTreeWidgetItem(self.main_window.friend_list)
                    item_name, ok = QInputDialog.getText(self.main_window, "添加分组", "请输入名称：")
                    if ok:
                        new_friend_item.setText(0, item_name)
                        new_friend_item.setText(1, "0")
                        friend_groups = table[0] + "," + item_name
                        conn.execute("UPDATE ACCOUNT_INFOR SET friend_groups=? WHERE QQ_number=?",
                                     (friend_groups, self.__QQ_number))
                        conn.commit()
                        conn.close()
                        # 动态加载
                        self.update_friend_list()
                elif action == option2:
                    new_item_name, ok = QInputDialog.getText(self.main_window, "重命名", "请输入名称：")
                    if ok:
                        friend_groups = table[0].split(",")
                        friend_groups[friend_groups.index(item.text(0))] = new_item_name
                        new_friend_groups = ""
                        for i in range(len(friend_groups)):
                            new_friend_groups = new_friend_groups+friend_groups[i]+","
                        if new_friend_groups:
                            new_friend_groups = new_friend_groups[:-1]
                            conn.execute("UPDATE ACCOUNT_INFOR SET friend_groups=? WHERE QQ_number=?",
                                         (new_friend_groups, self.__QQ_number))
                            conn.commit()
                            conn.close()
                            # 动态加载
                            self.update_friend_list()
                elif action == option3:
                    reply = QMessageBox.question(self.main_window, '删除分组',
                                                 "你确定要删除该分组吗?", QMessageBox.StandardButton.Yes |
                                                 QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        self.main_window.friend_list.takeTopLevelItem(self.main_window.friend_list.
                                                                      indexOfTopLevelItem(item))
                        friend_groups = table[0].split(",")
                        new_friend_groups = ""
                        for i in range(len(friend_groups)):
                            new_friend_groups = new_friend_groups+friend_groups[i]+","
                        if new_friend_groups:
                            new_friend_groups = new_friend_groups[:-1]
                            conn.execute("UPDATE ACCOUNT_INFOR SET friend_groups=? WHERE QQ_number=?",
                                         (new_friend_groups, self.__QQ_number))
                            conn.commit()
                            conn.close()
                            # 动态加载
                            self.update_friend_list()
                    else:
                        pass

    def show_add_menu(self):
        add_menu = QMenu()
        add_menu.setStyleSheet("""QMenu{
                                    background-color:white;color:black;
                                  }
                                  QMenu::item:hover{
                                    background-color:gray;color:black;
                                  }
                                                                    """)
        option1 = add_menu.addAction(QIcon("faqiqunliao.png"), "发起群聊")
        option2 = add_menu.addAction(QIcon("jiahaoyouhuoqun.png"), "加好友/群")
        action = add_menu.exec(self.main_window.chatroom_list.mapToGlobal
                               (QPoint((int(self.main_window.add_button.pos().x())+5),
                                       int(self.main_window.add_button.pos().y())-22)))
        if action == option1:
            self.show_make_group_window()
        elif action == option2:
            self.show_search_window()

    def give_like_to_friend(self):
        qq_number = self.friend_list[f"{self.selected_friend_item}"]
        conn = sqlite3.connect("user_account.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT like_number FROM ACCOUNT_INFOR WHERE QQ_number=?", (qq_number,))
        tables = cursor.fetchall()
        like_number = tables[0][0]
        new_like_number = like_number + 1
        cursor.execute(f"UPDATE ACCOUNT_INFOR SET like_number=? WHERE QQ_number=?", (new_like_number, qq_number))
        conn.commit()
        conn.close()
        self.main_window.like_number.setText(str(new_like_number))

    def set_friend_grouping(self, index):
        if self.tra_friend_grouping_flag:
            grouping = self.main_window.grouping.itemText(index)
            conn = sqlite3.connect("friend_list.db")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE _{self.__QQ_number} SET grouping=? WHERE QQ_number=?",
                           (grouping, self.friend_list[f"{self.selected_friend_item}"]))
            conn.commit()
            conn.close()
            # 获取需要模拟点击的分组的索引
            clicked_index = self.main_window.friend_list.indexOfTopLevelItem(self.selected_friend_item.parent())
            # 获取点击的好友项的索引
            clicked_index_1 = self.main_window.friend_list.topLevelItem(clicked_index).indexOfChild(
                self.selected_friend_item)
            # 更新好友列表
            self.update_friend_list()
            # 获取项在列表中的矩形区域
            rect = self.main_window.friend_list.visualItemRect(self.main_window.friend_list.topLevelItem(clicked_index))
            # 调整点击坐标
            adjusted_position = rect.center() - QPoint(152, 0)
            # 模拟鼠标左键点击
            QTest.mouseClick(self.main_window.friend_list.viewport(), Qt.MouseButton.LeftButton,
                             Qt.KeyboardModifier.NoModifier, adjusted_position)
            self.selected_friend_item = self.main_window.friend_list.topLevelItem(clicked_index).child(clicked_index_1)

    def set_friend_remark_name(self):
        if self.tra_friend_remark_flag:
            # 更新聊天列表数据库
            conn = sqlite3.connect("chat_list.db")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE _{self.__QQ_number} SET remark_name=? WHERE QQ_number=?",
                           (self.main_window.remark_edit.text(), self.friend_list[f"{self.selected_friend_item}"]))
            conn.commit()
            conn.close()
            # 更新好友列表数据库
            conn = sqlite3.connect("friend_list.db")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE _{self.__QQ_number} SET remark_name=? WHERE QQ_number=?",
                           (self.main_window.remark_edit.text(), self.friend_list[f"{self.selected_friend_item}"]))
            conn.commit()
            conn.close()
            # 更新聊天列表
            self.update_chat_list()
            # 获取需要模拟点击的分组的索引
            clicked_index = self.main_window.friend_list.indexOfTopLevelItem(self.selected_friend_item.parent())
            # 获取点击的好友项的索引
            clicked_index_1 = self.main_window.friend_list.topLevelItem(clicked_index).indexOfChild(
                self.selected_friend_item)
            # 更新好友列表
            self.update_friend_list()
            # 获取项在列表中的矩形区域
            rect = self.main_window.friend_list.visualItemRect(self.main_window.friend_list.topLevelItem(clicked_index))
            # 调整点击坐标
            adjusted_position = rect.center() - QPoint(152, 0)
            # 模拟鼠标左键点击
            QTest.mouseClick(self.main_window.friend_list.viewport(), Qt.MouseButton.LeftButton,
                             Qt.KeyboardModifier.NoModifier, adjusted_position)
            self.selected_friend_item = self.main_window.friend_list.topLevelItem(clicked_index).child(clicked_index_1)

    def add_chat_item(self):
        if self.friend_list[f"{self.selected_friend_item}"] not in self.chat_item:
            conn = sqlite3.connect("user_account.db")
            cursor = conn.cursor()
            cursor.execute("SELECT portrait FROM ACCOUNT_INFOR WHERE QQ_number=?",
                           (self.friend_list[f"{self.selected_friend_item}"],))
            tables = cursor.fetchall()
            conn.close()
            friend_portrait = tables[0][0]
            conn = sqlite3.connect("chat_list.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT `index` FROM _{self.__QQ_number}")
            tables_1 = cursor.fetchall()
            for i in range(len(tables_1)-1, -1, -1):
                cursor.execute(f"UPDATE _{self.__QQ_number} SET `index`=? WHERE `index`=?", (i+1, i))
            cursor.execute(f"INSERT INTO _{self.__QQ_number} (QQ_number, name, remark_name, portrait, `index`)"
                           f" VALUES (?,?,?,?,?)", (self.friend_list[f"{self.selected_friend_item}"],
                                                    self.main_window.friend_name.text(),
                                                    self.main_window.remark_edit.text(), friend_portrait, 0))
            conn.commit()
            conn.close()
            conn = sqlite3.connect("chatting_records.db")
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM _{self.__QQ_number} WHERE QQ_number=?",
                           (self.friend_list[f"{self.selected_friend_item}"],))
            tables_2 = cursor.fetchall()
            for i in range(len(tables_1) - 1, -1, -1):
                cursor.execute(f"UPDATE _{self.__QQ_number} SET `index`=? WHERE `index`=?", (i+1, i))
            if tables_2:
                cursor.execute(f"UPDATE _{self.__QQ_number} SET `index`=? WHERE QQ_number=?",
                               (0, self.friend_list[f"{self.selected_friend_item}"]))
            conn.commit()
            conn.close()
            self.main_window.left_page.setCurrentIndex(1)
            self.main_window.right_page.setCurrentIndex(1)
            chat_item = QListWidgetItem()
            if self.main_window.remark_edit.text():
                chat_item.setText(self.main_window.remark_edit.text())
            else:
                chat_item.setText(self.main_window.friend_name.text())
            chat_item.setIcon(QIcon(self.main_window.friend_portrait.pixmap()))
            self.main_window.chat_list.insertItem(0, chat_item)
            self.chat_item.insert(0, self.friend_list[f"{self.selected_friend_item}"])
            # 获取项在列表中的矩形区域
            rect = self.main_window.chat_list.visualItemRect(chat_item)
            # 计算点击位置，这里点击项的中心位置
            click_pos = QPoint(rect.center())
            # 模拟鼠标左键点击
            QTest.mouseClick(self.main_window.chat_list.viewport(), Qt.MouseButton.LeftButton,
                             Qt.KeyboardModifier.NoModifier, click_pos)
        else:
            row = self.chat_item.index(self.friend_list[f"{self.selected_friend_item}"])
            chat_item = self.main_window.chat_list.item(row)
            self.chat_item.insert(0, self.friend_list[f"{self.selected_friend_item}"])
            self.main_window.left_page.setCurrentIndex(1)
            # 获取项在列表中的矩形区域
            rect = self.main_window.chat_list.visualItemRect(chat_item)
            # 计算点击位置，这里点击项的中心位置
            click_pos = QPoint(rect.center())
            # 模拟鼠标左键点击
            QTest.mouseClick(self.main_window.chat_list.viewport(), Qt.MouseButton.LeftButton,
                             Qt.KeyboardModifier.NoModifier, click_pos)
        # 按钮
        self.main_window.chat_box.setIcon(QIcon(r"贴图/liaotian_pressed.png"))
        self.main_window.linkman.setIcon(QIcon(r"贴图/qqlianxiren.png"))

    def start_input(self):
        self.main_window.left_page.setCurrentIndex(2)

    def search_added_friend_chatroom(self):
        self.main_window.search_list.clear()
        input_text = self.main_window.search_box.text()
        if input_text:
            conn = sqlite3.connect("user_account.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM ACCOUNT_INFOR")
            tables_1 = cursor.fetchall()
            tables_1 = set(tables_1)
            for table_1 in tables_1:
                name = table_1[0]
                if input_text in name:
                    cursor.execute("SELECT QQ_number FROM ACCOUNT_INFOR WHERE name=?", (name,))
                    tables_2 = cursor.fetchall()
                    for table_2 in tables_2:
                        qq_number = table_2[0]
                        cursor.execute("SELECT portrait FROM ACCOUNT_INFOR WHERE QQ_number=?", (qq_number,))
                        tables_3 = cursor.fetchall()
                        table_3 = tables_3[0]
                        for portrait in table_3:
                            item = QListWidgetItem(name)
                            icon = QIcon(portrait)
                            item.setIcon(icon)
                            self.main_window.search_list.addItem(item)
            conn.close()

    def add_searched_item(self, item):
        item_name = item.text()
        new_item = QListWidgetItem(item_name)
        new_item.setIcon(item.icon())
        self.main_window.chat_list.insertItem(0, new_item)
        self.main_window.search_box.clear()
        self.main_window.left_page.setCurrentIndex(1)
        self.main_window.right_page.setCurrentIndex(1)
        self.main_window.title_label.setText(item_name)

    def choose_picture(self):
        image_paths, _ = QFileDialog.getOpenFileNames(self.main_window, "选择图片",
                                                      r"C:\PythonProject\pythonProject1",
                                                      "Images (*.png *.jpg *.jpeg)")
        if image_paths:
            for image_path in image_paths:
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                new_pixmap = QImage(scaled_pixmap)
                cursor = self.main_window.input_textbox.textCursor()
                cursor.insertImage(new_pixmap)
            self.image_paths = image_paths

    def send_context(self):
        time = datetime.now().timestamp()
        message = self.main_window.input_textbox.toPlainText()
        conn = sqlite3.connect("chatting_records.db")
        cursors = conn.cursor()
        if self.image_paths:
            for i in range(len(self.image_paths)):
                image_path = self.image_paths[i]
                cursors.execute(f"INSERT INTO _{self.__QQ_number} (QQ_number, name, time, picture) VALUES"
                                f" (?,?,?,?)", (self.chat_list[f"{self.selected_chat_item}"], self.name, time,
                                                image_path))
            if message != "":
                cursors.execute(f"UPDATE _{self.__QQ_number} SET text=? WHERE time=?", (message, time))
                # 更新聊天记录
                self.update_chat_records()
                # 清空输入框
                self.main_window.input_textbox.clear()
                # 清空图片路径变量
                self.image_paths.clear()
            else:
                # 更新聊天记录
                self.update_chat_records()
                # 清空输入框
                self.main_window.input_textbox.clear()
                # 清空图片路径变量
                self.image_paths.clear()
        else:
            if message != "":
                cursors.execute(f"INSERT INTO _{self.__QQ_number} (QQ_number, name, time, text) VALUES (?,?,?,?)",
                                (self.chat_list[f"{self.selected_chat_item}"], self.name, time, message))
                # 更新聊天记录
                self.update_chat_records()
                # 清空输入框
                self.main_window.input_textbox.clear()
            else:
                pass
        conn.commit()
        conn.close()
        # 更新聊天项的顺序
        if self.selected_chat_item != 0:
            # 聊天列表数据库更新
            conn = sqlite3.connect("chat_list.db")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE _{self.__QQ_number} SET `index`=? WHERE `index`=?",
                           (-1, self.main_window.chat_list.indexFromItem(self.selected_chat_item).row()))
            # 更改数据库中其它聊天项的索引
            for e in range(self.main_window.chat_list.indexFromItem(self.selected_chat_item).row() - 1, -1, -1):
                cursor.execute(f"UPDATE _{self.__QQ_number} SET `index`=? WHERE `index`=?", (e + 1, e))
            # 更新数据库中该聊天项的索引
            cursor.execute(f"UPDATE _{self.__QQ_number} SET `index`=? WHERE `index`=?", (0, -1))
            conn.commit()
            conn.close()
            # 更新聊天列表
            self.update_chat_list()
            # 获取项在列表中的矩形区域
            rect = self.main_window.chat_list.visualItemRect(self.main_window.chat_list.item(0))
            # 计算点击位置，这里点击项的中心位置
            click_pos = QPoint(rect.center())
            # 模拟鼠标左键点击
            QTest.mouseClick(self.main_window.chat_list.viewport(), Qt.MouseButton.LeftButton,
                             Qt.KeyboardModifier.NoModifier, click_pos)