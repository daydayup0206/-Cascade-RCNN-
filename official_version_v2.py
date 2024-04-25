import os
import shutil
import sys
import io
import threading
import re  # 导入正则表达式模块

from PyQt5.QtCore import QUrl
#import paddlex as pdx
from PyQt5.QtCore import QSize, QObject
from PyQt5.uic.properties import QtCore
from hdfs import InsecureClient
from matplotlib.figure import Figure
from pymongo import MongoClient

import config
from PaddleDetection.deploy.python.run_model_infer import load_model, detect_objects
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from PIL import Image
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFrame, QHeaderView, QAbstractItemView, QTableWidgetSelectionRange, QDialog, QMessageBox, \
    QTextEdit, QGridLayout, QSpacerItem, QSizePolicy, QComboBox
from PyQt5.QtWidgets import QLineEdit
from mongodb import DatabaseInitializer
import pymongo
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QHBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
import time
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt

import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket  # 使用websocket_client




class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("工业浸胶胶布缺陷检测分析系统")
        self.resize(400, 250)

        title_label = QLabel("工业浸胶胶布缺陷检测分析系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 18)
        title_font.setBold(True)
        title_label.setFont(title_font)

        self.username_label = QLabel("用户名:")
        self.username_edit = QLineEdit()

        self.password_label = QLabel("密码:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("登录")
        self.register_button = QPushButton("注册")

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

        self.login_success = False


    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        # 在这里执行登录逻辑，比如验证用户名和密码
        # 初始化数据库
        db_initializer = DatabaseInitializer()
        # 验证用户示例
        if db_initializer.verify_user(username, password):
            print("登录成功！")
            self.login_success = True
            self.username = username # 将用户名存储为 LoginDialog 实例的属性
            current_time_struct = time.localtime()
            # 格式化时间为字符串
            current_time_string = time.strftime("%Y-%m-%d %H:%M:%S", current_time_struct)

            self.login_time0 = current_time_string
            self.accept()  # 关闭对话框
        else:
            print("登录失败！")
            QMessageBox.warning(self, "登录失败", "用户名或密码错误！")

    def register(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        # 初始化数据库
        db_initializer = DatabaseInitializer()
        # 创建用户示例
        # 在这里执行注册逻辑，比如将用户名和密码保存到数据库
        db_initializer.create_user(username, password)

        QMessageBox.information(self, "注册成功", "注册成功！")
class ImageProcessor(QWidget):
    def __init__(self):
        self.ispass = "unpass"
        self.username = ""
        self.login_time = ""
        self.first_open = True  # 标记是否是第一次打开应用程序
        self.image_paths = []


        # 加载图片文件
        user_icon_path = "E:/new-learning/zhiwuquexianjianche/css_image/Snipaste_2024-04-08_20-41-44.jpg"
        self.user_icon = QPixmap(user_icon_path)
        super().__init__()
        self.show_login_dialog()


        self.selected_save_path = ""
        self.selected_save_path = ""
        # 清除图片缓存计数
        self.comein=0

        self.setWindowTitle("工业浸胶胶布缺陷检测分析系统-v1.1")
        self.resize(1500, 1000)


        # 创建容器1
        container1 = QFrame(self)
        container1.setGeometry(0, 0, 1500, 120)
        container1.setStyleSheet("background-color: #C0C0C0;")

        # 添加标题标签
        title_label = QLabel("工业浸胶胶布缺陷检测分析系统", container1)
        title_label.setGeometry(20, 35, 1000, 50)  # 根据需要调整位置和大小
        title_label.setStyleSheet("font-size: 40px; color: black; font-weight: bold; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);")  # 根据需要设置字体样式

        # 在容器1中添加用于显示当前登录用户的标签
        self.current_user_label = QLabel("当前用户: " + self.username, container1)
        self.current_user_label.setGeometry(1100, 35, 300, 50)
        self.current_user_label.setStyleSheet("font-size: 20px; color: black;")

        # 登录按钮
        self.login_button = QPushButton("登录", container1)
        self.login_button.setGeometry(1350, 35, 100, 50)
        self.login_button.setStyleSheet(
            "font-size: 20px; background-color: #EDECEA; color: black; border: none; border-radius: 5px;")

        container2 = QFrame(self)
        container2.setGeometry(0, 120, 200, 830)

        # 创建按钮列表和样式
        self.buttons_info = [('主页', 'background-color: #AAB4C4;', self.show_page1),
                   ('数据分析', 'background-color: #AAB4C4;', self.show_page2),
                   ('检测可视化', 'background-color: #AAB4C4;', lambda: self.show_page3(class_name="normal", score=0.0, output_file=r"E:\new-learning\zhiwuquexianjianche\output\2024-04-13\['area defects']\20240306185833799_defect_1.jpg")),  # 这里暂时没有指定参数
                   ('数据库', 'background-color: #AAB4C4;', lambda: (self.stacked_widget.setCurrentIndex(3), self.update_button_styles(3))),  # 这里暂时没有指定参数
                   ('我的', 'background-color: #AAB4C4;', lambda: self.show_page5())]  # 这里暂时没有指定参数
        button_layout = QVBoxLayout()


        # 为容器2添加按钮
        self.buttons = []
        for btn_text, style, callback in self.buttons_info:
            button = QPushButton(btn_text, self)
            button.setFixedSize(200, 166)
            button.setStyleSheet('''
        QPushButton{  
            font: 22pt "Microsoft SimSun"; 
            border: 1px solid #C0C0C0; 
            border-style: solid;  
            border-radius:0px;  
            padding: 10px;
            %s
        } 

        QPushButton:hover{    
            border: 1px solid #E3C46F;  
            background-color:##FFFFFF;  
            border-radius:2px;  
        }
        QPushButton:pressed{  
            background-color:#EAF0FF;  
            border: 1px solid #AAB4C4;  
            border-radius:1px;  
        } ''' % style)
            button.clicked.connect(callback)
            button_layout.addWidget(button)
            self.buttons.append(button)
        # 设置容器2的布局
        container2.setLayout(button_layout)


        # 创建QStackedWidget用于存放界面
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setGeometry(210, 120, 1290, 830)


        # 页面1: 选择文件夹和保存路径
        self.page1 = QWidget()
        # 创建第一个垂直布局器用于显示图片
        self.image_layout = QVBoxLayout()

        # 加载并显示图片（这里使用占位图片，请替换为您自己的图片路径）
        self.pixmap = QPixmap(r'E:\new-learning\zhiwuquexianjianche\css_image\main_page.jpg').scaled(1200, 1000, Qt.KeepAspectRatio)
        self.label_image = QLabel()
        self.label_image.setPixmap(self.pixmap)
        self.image_layout.addWidget(self.label_image)

        # 创建第二个垂直布局器用于显示文字
        self.text_layout = QVBoxLayout()
        self.label_text = QLabel('本系统旨在构律基干深度学习的自动化浸胶胶布缺略分析系统。通过提高浸肪胶布缺略检测的准确件和效率，实现生产过程中的质量控制和成木降低。')
        self.font = QFont()
        self.font.setFamily("Microsoft YaHei")  # 设置字体为微软雅黑
        self.font.setPointSize(10)  # 设置字体大小
        self.font.setBold(True)  # 设置字体加粗
        self.font.setItalic(True)
        self.label_text.setFont(self.font)
        self.text_layout.addWidget(self.label_text)

        self.buttons_layout = QVBoxLayout()
        self.button_layout1 = QHBoxLayout()
        self.folder_button = QPushButton('选择文件夹')
        self.folder_button.clicked.connect(self.select_folder_open)


        self.save_button = QPushButton('选择储存路径')
        self.save_button.clicked.connect(self.select_folder_save)

        self.button_layout1.addWidget(self.folder_button)
        self.button_layout1.addWidget(self.save_button)

        # 创建第二个子垂直布局器，里面包含另一个水平布局器用于设置按钮
        self.button_layout2 = QHBoxLayout()
        self.start_button = QPushButton('开始')
        self.start_button .clicked.connect((lambda: self.show_page3(class_name="nomal", score=0.0, output_file="")))
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setEnabled(False)

        #self.pdx_button = QPushButton('二次精细分类')
        #self.pdx_button.clicked.connect((lambda: self.run_pdx_model(folder_path=r"E:\new-learning\zhiwuquexianjianche\output\2024-04-13\['Point defects']", save_path=r"E:\new-learning\zhiwuquexianjianche\test_pdx")))
        #self.pdx_result.connect()


        self.end_button = QPushButton('结束')
        self.end_button.clicked.connect(self.stop_processing)
        self.button_layout2.addWidget(self.start_button)
        #self.button_layout2.addWidget(self.pdx_button)
        self.button_layout2.addWidget(self.end_button)

        # 将水平布局器添加到子垂直布局器中
        self.sub_layout1 = QVBoxLayout()
        self.sub_layout1.addLayout(self.button_layout1)

        self.sub_layout2 = QVBoxLayout()
        self.sub_layout2.addLayout(self.button_layout2)

        # 将子垂直布局器添加到主垂直布局器中
        self.buttons_layout.addLayout(self.sub_layout1)
        self.buttons_layout.addLayout(self.sub_layout2)

        # 将所有布局器添加到主窗口中
        self.page1.setLayout(QVBoxLayout())
        self.page1.layout().addLayout(self.image_layout)
        self.page1.layout().addLayout(self.text_layout)
        self.page1.layout().addLayout(self.buttons_layout)

        self.stacked_widget.addWidget(self.page1)

        self.show_page1()


        # 页面2: 可视化结果
        self.page2 = QWidget()
        self.page2_layout = QGridLayout(self.page2)
        self.stacked_widget.addWidget(self.page2)

        # 页面3: 展示图片和文本
        self.page3 = QWidget()
        self.page3_layout = QVBoxLayout(self.page3)

        font = QFont("Arial", 12)
        font.setBold(True)

        self.current_image_label = QLabel("当前检测图片：")
        self.current_image_label.setFont(font)
        self.page3_layout.addWidget(self.current_image_label)

        self.image_label = QLabel("Image Placeholder")
        self.page3_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        self.text_label = QLabel("Text Placeholder")
        self.page3_layout.addWidget(self.text_label, alignment=Qt.AlignCenter)

        # 添加结束按钮
        self.stop_button = QPushButton("结束")
        self.stop_button.clicked.connect(self.stop_processing)
        self.page3_layout.addWidget(self.stop_button, alignment=Qt.AlignCenter)

        self.stacked_widget.addWidget(self.page3)



        # 创建第四个界面
        self.fourthPage = QWidget()
        self.createFourthPageLayout(self.fourthPage)
        self.stacked_widget.addWidget(self.fourthPage)

        # 创建第5个界面
        self.page5 = QWidget()
        self.stacked_widget.addWidget(self.page5)
        # 显示用户信息和退出登录按钮
        self.display_user_info()

        # 创建main_widget并添加布局
        main_widget = QWidget(self)
        main_widget.setGeometry(0, 120, 1500, 830)
        main_layout = QHBoxLayout(main_widget)
        main_layout.addWidget(container2)
        main_layout.addWidget(self.stacked_widget, stretch=1)


        # 连接按钮信号和槽，以切换QStackedWidget的页面
        for index, button in enumerate(container2.findChildren(QPushButton)):
            button.clicked.connect(lambda _, i=index: self.stacked_widget.setCurrentIndex(i))

        if self.first_open:
            self.show_page1()  # 如果是第一次打开，显示主页

            self.first_open = False  # 设置标记为 False，以便下次不再执行这个操作

    def show_login_dialog(self):
        login_dialog = LoginDialog(self)
        login_dialog.exec_()
        if login_dialog.login_success:
            print("登录成功！可以执行相应操作")
            self.username = login_dialog.username
            self.login_time = login_dialog.login_time0
        else:
            print("登录取消或失败")
            sys.exit()
    def update_button_styles(self, current_index):
        # 更新按钮样式以反映当前选中的页面
        for index, button in enumerate(self.buttons):
            if index == current_index:
                button.setStyleSheet('''
                    QPushButton{  
                        font: 18pt "Microsoft SimSun"; 
                        border: 1px solid #C0C0C0; 
                        border-style: solid;  
                        border-radius:0px;  
                        padding: 10px;
                        background-color: #EDECEA;  /* 选中时的背景颜色 */
                        color: black;  /* 选中时的文字颜色 */
                    } 
                ''')
            else:
                button.setStyleSheet('''
                    QPushButton{  
                        font: 18pt "Microsoft SimSun"; 
                        border: 1px solid #C0C0C0; 
                        border-style: solid;  
                        border-radius:0px;  
                        padding: 10px;
                        background-color:#C0C0C0;  /* 非选中时的背景颜色 */
                        color:black;
                    } 
                ''')



    def select_folder_save(self):
        QTimer.singleShot(0, self.select_save_path)

    def select_folder_open(self):
        QTimer.singleShot(0, self.select_open_folder)
    def select_open_folder(self):
        # 创建 QFileDialog 对象
        dialog = QFileDialog()
        # 设置默认路径
        default_path = r"E:\new-learning\zhiwuquexianjianche\dataset"
        # 设置默认路径
        dialog.setDirectory(default_path)

        try:
            folder_path = QFileDialog.getExistingDirectory(self, "打开图片文件夹", default_path)
            if folder_path:
                self.selected_folder_path = folder_path
                self.check_paths()
            print("321")
        except Exception as e:
            print(e)
    def select_save_path(self):
        # 创建 QFileDialog 对象
        dialog = QFileDialog()
        # 设置默认路径
        default_path = r"E:\new-learning\zhiwuquexianjianche"
        # 设置默认路径
        dialog.setDirectory(default_path)
        save_path = QFileDialog.getExistingDirectory(self, "选择保存文件夹", default_path)
        if save_path:
            self.selected_save_path = save_path
            self.check_paths()

    def check_paths(self):
        # 检查路径是否都已经选择，如果是，则启用 "Start" 按钮
        if self.selected_folder_path and self.selected_save_path:
            self.start_button.setEnabled(True)

    def start_processing(self):
        # 确保按钮点击时路径已经选择
        if self.selected_folder_path and self.selected_save_path:
            # 创建线程来运行预测代码
            self.prediction_thread = PredictionThread(self.selected_folder_path, self.selected_save_path)
            self.prediction_thread.data_result.connect(self.show_page3)


            self.prediction_thread.predictionFinished.connect(self.show_page2)
            #self.prediction_thread.predictionFinished.connect(self.save_to_txt_and_upload_to_hdfs)
            self.prediction_thread.start()
        else:
            print("Please select both input folder and save path.")

    def start_processing2(self):
        # 确保按钮点击时路径已经选择
        if self.selected_folder_path and self.selected_save_path:
            # 创建线程来运行预测代码
            self.prediction_thread.data_result.connect(self.show_page3)
            self.prediction_thread = PredictionThread(self.selected_folder_path, self.selected_save_path)



            self.prediction_thread.predictionFinished.connect(self.show_page2)
            #self.prediction_thread.predictionFinished.connect(self.save_to_txt_and_upload_to_hdfs)
            self.prediction_thread.start()
        else:
            print("Please select both input folder and save path.")


    def stop_processing(self):
        # 发送信号给预测线程，要求停止

        if hasattr(self, 'prediction_thread'):
            self.prediction_thread.stop_requested = True

    # 在主线程中定义一个方法，用于处理信号




    def show_page1(self):
        self.stacked_widget.setCurrentIndex(0)
        self.update_button_styles(0)

    def show_page2(self):
        self.stacked_widget.setCurrentIndex(1)
        self.update_button_styles(1)

        # 清除之前添加的所有子部件
        self.clear_layout(self.page2_layout)
        # # 在适当的地方调用 visualize_image_count 方法，传入包含图像的文件夹的路径
        folder_path = r'E:\new-learning\zhiwuquexianjianche\output\2024-04-13'
        # # 获取指定路径下的所有文件和文件夹名称
        # contents = os.listdir(folder_path)
        # # 筛选出文件夹的名称并添加到batch列表中
        # batch = [item for item in contents if os.path.isdir(os.path.join(folder_path, item))]
        page_index = 0
        self.visualize_image_count(page_index,folder_path)
        # # print("进入成功")

    def select_batch(self):
        # 打开文件对话框以选择批次文件夹
        # 创建 QFileDialog 对象
        dialog = QFileDialog()
        # 设置默认路径
        default_path = r"E:\new-learning\zhiwuquexianjianche\output"
        # 设置默认路径
        dialog.setDirectory(default_path)

        folder_path = QFileDialog.getExistingDirectory(self, "选择对应的批次", default_path)
        if folder_path:
            page_index = 0
            # 更新 folder_path
            self.folder_path = folder_path
            # 执行可视化操作
            self.visualize_image_count(page_index, folder_path)
    def show_page3(self, class_name, score, output_file):

        self.stacked_widget.setCurrentIndex(2)
        self.update_button_styles(2)

        # 获取当前时间戳
        current_time_stamp = time.time()
        # 使用strftime方法将时间戳格式化为字符串
        current_time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time_stamp))
        #获取文件名
        name = os.path.basename(output_file)
        #获取批次
        batch = os.path.basename(os.path.dirname(os.path.dirname(output_file)))
        # print("展示图片路径"+output_file)
        db_initializer = DatabaseInitializer()
        user_collection = db_initializer.initialize_user_collection(self.username)
        db_initializer.insert_data(batch, name, output_file, class_name, self.username, current_time_string, self.ispass)

        # 设置文本属性
        font = QFont("Arial", 12, QFont.Bold)  # 使用 Arial 字体，12号字体大小，加粗
        self.text_label.setFont(font)  # 设置字体
        self.text_label.setAlignment(Qt.AlignCenter)  # 文本居中对齐

        text = f"类名: {class_name}, 得分: {score}"
        print("类名：", class_name, "得分：", score)

        self.text_label.setText(text)

        # 加载图像并展示

        pixmap = QPixmap(output_file)

        scaled_pixmap = pixmap.scaled(QSize(800, 500), Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)  # 图片居中显示
        self.text_label.setScaledContents(True)

        # 判断第几次进入，40次清楚图片缓存
        self.comein = self.comein + 1
        # print(self.comein)
        if self.comein == 40:
            self.image_label.clear()
            self.comein = 0
            print("图片缓存清理成功！")

    def createFourthPageLayout(self, widget):


        # 初始化数据库
        db_initializer = DatabaseInitializer()
        self.user_collection = db_initializer.initialize_user_collection(self.username)
        print(f"User '{self.username}' collection initialized.")

        # 垂直布局
        layout_4 = QVBoxLayout()

        # 查询输入框和按钮布局
        main_layout = QHBoxLayout()

        # 导出图片按钮
        self.import_button = QPushButton('导出图片')
        self.import_button.clicked.connect(self.import_images)

        self.query_input = QLineEdit()  # 输入框
        self.query_input.setMinimumWidth(200)  # 设置输入框的最小宽度为200像素
        self.query_input.setMaximumWidth(400)  # 设置输入框的最大宽度为400像素

        query_button = QPushButton('查询')  # 查询按钮
        query_button.setFixedSize(100, 25)
        query_button.clicked.connect(self.query_data)  # 连接查询按钮的点击事件

        # 删除按钮
        delete_button = QPushButton('删除')
        delete_button.setFixedSize(100, 25)
        delete_button.clicked.connect(self.delete_data)

        # 全选按钮
        select_all_button = QPushButton('全选')
        select_all_button.setFixedSize(100, 25)
        select_all_button.clicked.connect(self.select_all_rows)

        # 刷新按钮
        refresh_button = QPushButton('刷新')
        refresh_button.setFixedSize(100, 25)
        refresh_button.clicked.connect(self.refresh_table)

        # 打印表格按钮
        print_button = QPushButton('打印表格')
        print_button.setFixedSize(100, 25)
        print_button.clicked.connect(self.print_table)

        self.year_combo = QComboBox()
        self.month_combo = QComboBox()
        self.day_combo = QComboBox()

        # 填充年份下拉框
        current_year = datetime.now().year
        self.year_combo.addItem("选择年份", None)
        for year in range(current_year - 10, current_year + 1):
            self.year_combo.addItem(str(year), year)

        # 填充月份下拉框
        self.month_combo.addItem("选择月份", None)
        for month in range(1, 13):
            self.month_combo.addItem(str(month), month)

        # 填充天数下拉框
        self.day_combo.addItem("选择天数", None)
        for day in range(1, 32):  # 始终显示从1到31天
            self.day_combo.addItem(str(day), day)

        # 下拉框选择事件连接到更新函数
        self.year_combo.currentIndexChanged.connect(self.update_table_based_on_date)
        self.month_combo.currentIndexChanged.connect(self.update_table_based_on_date)

        # 连接信号与槽
        self.year_combo.currentIndexChanged.connect(self.update_table_based_on_date)
        self.month_combo.currentIndexChanged.connect(self.update_table_based_on_date)
        self.day_combo.currentIndexChanged.connect(self.update_table_based_on_date)


        # 将输入框和查询按钮添加到左边的水平布局中
        left_layout = QHBoxLayout()
        left_layout.addWidget(self.query_input)
        left_layout.addWidget(query_button)
        left_layout.addWidget(print_button)
        left_layout.addWidget(self.import_button)


        # 将删除按钮添加到右边的水平布局中
        right_layout = QHBoxLayout()
        right_layout.addStretch(1)  # 添加一个弹性空间，将删除按钮推到右边
        right_layout.addWidget(delete_button)
        right_layout.addWidget(select_all_button)
        right_layout.addWidget(refresh_button)

        # 将左右两个水平布局添加到主布局中
        main_layout.addLayout(left_layout)

        main_layout.addLayout(right_layout)

        # 将主布局添加到垂直布局中
        layout_4.addLayout(main_layout)

        # 表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(
            ['批次', '图片名称', '图片路径', '图片类别', '用户', '日期', '是否放行'])
        self.table_widget.setRowCount(20)  # 设置行数
        self.update_table(self.user_collection)  # 更新表格数据
        # 将表格添加到布局中
        layout_4.addWidget(self.table_widget)
        widget.setLayout(layout_4)

        date_layout = QHBoxLayout()
        date_layout.addWidget(self.year_combo)
        date_layout.addWidget(self.month_combo)
        date_layout.addWidget(self.day_combo)
        layout_4.insertLayout(1, date_layout)

    def update_table_based_on_date(self):
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()
        day = self.day_combo.currentData()
        query = {}
        if year and month and day:
            # 构建完整日期的正则表达式，假定日期格式是 yyyy-mm-dd
            query['time'] = {"$regex": f"^{year}-{month:02d}-{day:02d}"}
        elif year and month:
            # 只有年和月，构建只包含年月的正则表达式
            query['time'] = {"$regex": f"^{year}-{month:02d}-"}
        elif year:
            # 只有年，构建只包含年的正则表达式
            query['time'] = {"$regex": f"^{year}-"}

        # 使用查询条件更新表格数据
        self.update_table(self.user_collection.find(query))

    def refresh_table(self):
        # 清空表格数据
        self.table_widget.clearContents()
        # 重新获取数据并更新表格
        self.update_table(self.user_collection)

    def select_all_rows(self):
        # 获取表格的行数和列数
        row_count = self.table_widget.rowCount()
        column_count = self.table_widget.columnCount()

        # 设置整个范围的行为选中状态
        self.table_widget.setRangeSelected(QTableWidgetSelectionRange(0, 0, row_count - 1, column_count - 1), True)

    def update_table(self, results):
        self.table_widget.setRowCount(0)  # 清空表格
        row = 0
        if isinstance(results, pymongo.cursor.Cursor):
            for result in results:
                self.table_widget.insertRow(row)
                self.table_widget.setItem(row, 0, QTableWidgetItem(result.get('batch', '')))
                self.table_widget.setItem(row, 1, QTableWidgetItem(result.get('name', '')))
                self.table_widget.setItem(row, 2, QTableWidgetItem(result.get('path', '')))
                classes_value = result.get('classes', '')
                if isinstance(classes_value, list) and len(classes_value) == 1:
                    classes_str = classes_value[0]
                else:
                    classes_str = ', '.join(classes_value)
                self.table_widget.setItem(row, 3, QTableWidgetItem(classes_str))
                self.table_widget.setItem(row, 4, QTableWidgetItem(result.get('user', '')))
                self.table_widget.setItem(row, 5, QTableWidgetItem(result.get('time', '')))
                self.table_widget.setItem(row, 6, QTableWidgetItem(result.get('ispass', '')))
                row += 1
        elif isinstance(results, pymongo.collection.Collection):
            for result in results.find():
                self.table_widget.insertRow(row)
                self.table_widget.setItem(row, 0, QTableWidgetItem(result.get('batch', '')))
                self.table_widget.setItem(row, 1, QTableWidgetItem(result.get('name', '')))
                self.table_widget.setItem(row, 2, QTableWidgetItem(result.get('path', '')))
                classes_value = result.get('classes', '')
                if isinstance(classes_value, list) and len(classes_value) == 1:
                    classes_str = classes_value[0]
                else:
                    classes_str = ', '.join(classes_value)
                self.table_widget.setItem(row, 3, QTableWidgetItem(classes_str))
                self.table_widget.setItem(row, 4, QTableWidgetItem(result.get('user', '')))
                self.table_widget.setItem(row, 5, QTableWidgetItem(result.get('time', '')))
                self.table_widget.setItem(row, 6, QTableWidgetItem(result.get('ispass', '')))
                row += 1
        else:
            print("Invalid results type.")
    def query_data(self):
        query_text = self.query_input.text()
        if not query_text:
            self.query = {}
        else:
            self.query = {
                "$or": [  # 使用 "$or" 运算符指定多个条件
                    {"batch": {"$regex": query_text, "$options": "i"}},
                    {"name": {"$regex": query_text, "$options": "i"}},  # 在 "name" 字段中进行模糊搜索
                    {"path": {"$regex": query_text, "$options": "i"}},  # 在 "path" 字段中进行模糊搜索
                    {"classes": {"$regex": query_text, "$options": "i"}},  # 在 "classes" 字段中进行模糊搜索
                    {"user": {"$regex": query_text, "$options": "i"}},  # 在 "user" 字段中进行模糊搜索
                    {"time": {"$regex": query_text, "$options": "i"}},
                    {"ispass": {"$regex": query_text, "$options": "i"}}# 在 "time" 字段中进行模糊搜索
                ]
            }

        user_collection = self.user_collection
        results = user_collection.find(self.query)

        self.update_table(results)
        print("查询成功")

    def delete_data(self):
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if selected_rows:
            print("Selected rows:", selected_rows)
            for row in selected_rows:
                document_name = self.table_widget.item(row.row(), 1).text()
                print("Document name:", document_name)
                query = {"name": document_name}  # 根据需要设置删除条件
                self.user_collection.delete_one(query)

            self.query_data()  # 删除后重新查询更新表格数据
        else:
            print("No rows selected. Please select rows to delete.")

    def print_table(self):
        printer = QPrinter()
        printer.setPageSize(QPrinter.A4)  # 设置打印纸张大小为A4

        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            page_size = printer.pageRect(QPrinter.DevicePixel)  # 获取A4纸的像素矩形

            # 记录表格的原始大小
            self.original_table_size = self.table_widget.size()

            # 计算表格需要的大小，使其填满整个页面
            table_rect = QRectF(0, 0, page_size.width(), page_size.height())

            # 调整表格大小
            self.table_widget.resize(table_rect.size().toSize())

            # 更新表格内容以适应新的大小
            self.update_table(self.user_collection)
            self.table_widget.viewport().update()

            # 绘制表格
            self.table_widget.render(painter)

            painter.end()

            # 打印完成后恢复表格大小
            self.table_widget.resize(self.original_table_size)

    def import_images(self):
        QMessageBox.information(self, '提示', '保存成功！')
        for collection in self.user_collection.find(self.query):
            save_path = collection['path']
            file_class_name = self.extract_class_name(save_path)
            # 分割字符串，这里假设我们要找的部分前面有一个反斜杠
            print(save_path)
            target_folder = r"E:\new-learning\zhiwuquexianjianche\train_model_images"
            self.move_file_to_folder(save_path, target_folder, file_class_name)



    def extract_class_name(self, file_path):
        # 使用正则表达式匹配路径中的类名
        pattern = r"\[(.*?)\]"
        match = re.search(pattern, file_path)
        if match:
            class_name = match.group(1)  # 提取匹配到的类名
            return class_name
        else:
            return None

    def move_file_to_folder(self, file_path, target_folder, file_class_name):
        # 确保目标文件夹存在
        target_folder = os.path.join(target_folder, file_class_name)
        print(target_folder)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # 获取文件名
        file_name = os.path.basename(file_path)

        # 构造目标文件的完整路径
        target_file_path = os.path.join(target_folder, file_name)

        # 移动文件到目标文件夹
        shutil.move(file_path, target_file_path)
    def show_page5(self):
        self.stacked_widget.setCurrentIndex(4)
        self.update_button_styles(4)

    def display_user_info(self):
        layout = QVBoxLayout(self.page5)

        # 创建一个水平布局用于放置用户信息和系统参数设置
        info_layout = QHBoxLayout()

        # 添加用户图标和用户名以及登录时间
        user_info_layout = QVBoxLayout()
        user_info_layout.setAlignment(Qt.AlignLeft)

        # 如果有用户图标，展示用户图标
        user_icon_label = QLabel()
        user_icon_label.setPixmap(self.user_icon.scaledToWidth(280))  # 设置用户图标并调整大小
        user_icon_label.setAlignment(Qt.AlignCenter)  # 图片居中显示
        user_info_layout.addWidget(user_icon_label)

        # 展示用户名
        username_label = QLabel("用户名：{}".format(self.username))
        username_label.setAlignment(Qt.AlignCenter)  # 文字居中显示
        font = username_label.font()
        font.setBold(True)  # 设置字体加粗
        font.setPointSize(14)  # 设置字体大小
        username_label.setFont(font)
        user_info_layout.addWidget(username_label)

        # 展示登录时间
        login_time_label = QLabel("登录时间：{}".format(self.login_time))
        login_time_label.setAlignment(Qt.AlignCenter)  # 文字居中显示
        font = login_time_label.font()
        font.setBold(True)  # 设置字体加粗
        font.setPointSize(12)  # 设置字体大小
        login_time_label.setFont(font)
        user_info_layout.addWidget(login_time_label)

        # 添加退出登录按钮
        logout_button = QPushButton("退出登录")
        logout_button.clicked.connect(self.logout)
        logout_button.setFixedSize(100, 40)
        user_info_layout.addWidget(logout_button, alignment=Qt.AlignCenter)

        # 添加弹性空间，使左侧布局在水平方向上占据额外空间
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        user_info_layout.addItem(spacer)

        info_layout.addLayout(user_info_layout)

        # 创建一个垂直布局用于放置系统参数设置
        settings_layout = QVBoxLayout()
        settings_layout.setAlignment(Qt.AlignRight)

        font = QFont()
        font.setPointSize(16)  # 设置字体大小
        font.setBold(True)
        current_parameter_label = QLabel("系统参数及设置")
        current_parameter_label.setFont(font)
        settings_layout.addWidget(current_parameter_label, alignment=Qt.AlignCenter)

        font = QFont()
        font.setPointSize(14)  # 设置字体大小

        current_sys_version_label = QLabel("当前系统版本：工业浸胶胶布缺陷检测分析系统v1.1")
        current_sys_version_label.setFont(font)
        settings_layout.addWidget(current_sys_version_label)

        current_model_label = QLabel("当前模型：Cascade-RCNN-v3")
        current_model_label.setFont(font)
        settings_layout.addWidget(current_model_label)

        current_paddle_version_label = QLabel("当前paddlepaddle版本：PADDLEPADDLE 2.3.2")
        current_paddle_version_label.setFont(font)
        settings_layout.addWidget(current_paddle_version_label)

        current_CUDA_version_label = QLabel("当前CUDA版本：CUDA11.6")
        current_CUDA_version_label.setFont(font)
        settings_layout.addWidget(current_CUDA_version_label)

        current_platform_label = QLabel("当前计算平台：RTX3060 6G")
        current_platform_label.setFont(font)
        settings_layout.addWidget(current_platform_label)

        # 添加阈值设置部分
        self.threshold_input = QLineEdit()
        self.threshold_input.setPlaceholderText("当前模型阈值" + str(config.threshold))
        self.threshold_input.setFixedSize(515, 40)  # 设置输入框大小
        settings_layout.addWidget(self.threshold_input)

        # 添加修改阈值按钮
        self.update_threshold_button = QPushButton("更新疵点阈值")
        self.update_threshold_button.clicked.connect(self.update_threshold)
        self.update_threshold_button.setFixedSize(150, 40)  # 设置按钮大小
        settings_layout.addWidget(self.update_threshold_button, alignment=Qt.AlignCenter)  # 将按钮添加到布局时设置对齐方式为居中

        # 将右侧布局放置在框架内
        settings_frame = QFrame()
        settings_frame.setFrameShape(QFrame.Box)
        settings_frame.setLayout(settings_layout)

        info_layout.addWidget(settings_frame)

        layout.addLayout(info_layout)
    # 编写一个函数来更新阈值
    # 编写一个函数来更新阈值
    def update_threshold(self):
        new_threshold = self.threshold_input.text()
        # 将新的阈值写入 config.py 文件
        with open("config.py", "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open("config.py", "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("threshold"):
                    f.write(f"threshold = {new_threshold}\n")
                else:
                    f.write(line)
        # 提示用户更新成功
        QMessageBox.information(self, "Success", "模型阈值更新成功！")

    def logout(self):
        # 在此处执行退出登录的逻辑
        # 例如，关闭当前窗口并返回登录页面
        self.show_login_dialog()
        # 显示登录对话框或返回到登录页面的其他操作

    def visualize_image_count(self,page_index, folder_path):
        #answer = ""  # 在函数内部定义 answer 变量
        self.clear_layout(self.page2_layout)
        image_counts = {}
        max_images_count = 0

        self.current_page = page_index
        self.current_page %= 4
        for class_folder in os.listdir(folder_path):
            if os.path.isdir(os.path.join(folder_path, class_folder)):
                image_count = len(os.listdir(os.path.join(folder_path, class_folder)))
                image_counts[class_folder] = image_count
                if image_count > max_images_count:
                    max_images_count = image_count
                    max_images_folder = class_folder
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)  # 设置为只读
        #获取批次名
        folder_name = os.path.basename(folder_path)

        def create_pie_chart(counts):
            fig = Figure(figsize=(4, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%', startangle=140)
            ax.set_title(folder_name + "batch defects(pie)")
            return fig
        def create_bar_chart(counts):
            fig = Figure(figsize=(4, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.bar(counts.keys(), counts.values())
            ax.set_title(folder_name + "batch defects(bar)")
            return fig


        pie_chart_canvas = FigureCanvas(create_pie_chart(image_counts))
        bar_chart_canvas = FigureCanvas(create_bar_chart(image_counts))

        # 创建Matplotlib图表
        def create_combined_chart(counts):
            fig = Figure(figsize=(8, 6), dpi=100)
            ax1 = fig.add_subplot(211)
            ax2 = fig.add_subplot(212)

            # 绘制饼图
            ax1.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%', startangle=140)
            ax1.set_title('Defect distribution of impregnated tape')

            # 绘制柱状图
            ax2.bar(counts.keys(), counts.values())
            ax2.set_title('Defect distribution of impregnated tape')

            return fig

        # 创建两个图表
        combined_chart = create_combined_chart(image_counts)

        # 创建一个内存缓冲区
        buffer = io.BytesIO()
        # 将画布保存为图像数据到内存缓冲区
        FigureCanvas(combined_chart).print_png(buffer)
        # 从内存缓冲区获取图像数据
        imagedata = buffer.getvalue()

        self.worker = Worker()
        self.worker.finished.connect(self.on_model_finished)
        self.worker.answers.connect(self.on_model_transmit)

        # 开始运行大模型
        self.run_model(imagedata)

#---------------------------------------------------------------------------------------------------------------------------------

        self.select_batch_button = QPushButton("选择需要分析的批次")
        self.select_batch_button.clicked.connect(self.select_batch)
        # 初始化数据库
        db_initializer = DatabaseInitializer()
        self.user_collection = db_initializer.initialize_user_collection(self.username)


        self.updateispass_button = QPushButton("同意放行")
        self.updateispass_button.clicked.connect(lambda: db_initializer.update_ispassdata(folder_name))


        row = 0
        self.page2_layout.addWidget(self.select_batch_button, row, 1)
        self.page2_layout.addWidget(self.updateispass_button, row, 2)
        # 创建 QLabel 用于显示当前批次重要疵点
        self.batch_label = QLabel("当前批次重要疵点：")
        self.page2_layout.addWidget(self.batch_label, row, 4, alignment=Qt.AlignCenter)  # 将文字居中显示
        row += 1

        subfolder_name = "['area defects']"
        complete_path = os.path.join(folder_path, subfolder_name)
        # 获取文件夹中的所有图像文件路径
        image_files = [file for file in os.listdir(complete_path) if file.endswith(('.jpg', '.png', '.jpeg'))]
        self.image_paths = [os.path.join(complete_path, file) for file in image_files]

        def show_image(image_path):

            pixmap = QPixmap(image_path)
            # 调整图像大小以适应 QLabel 的大小
            scaled_pixmap = pixmap.scaled(self.image_label2.size(), aspectRatioMode=Qt.KeepAspectRatio)
            self.image_label2.setPixmap(scaled_pixmap)
            self.image_label2.setAlignment(Qt.AlignCenter)  # 图像居中显示



        def show_previous_image():
            # 显示前一张图像
            self.current_image_index -= 1
            if self.current_image_index < 0:
                self.current_image_index = len(self.image_paths) - 1
            show_image(self.image_paths[self.current_image_index])

        def show_next_image():
            # 显示后一张图像
            self.current_image_index += 1
            if self.current_image_index >= len(self.image_paths):
                self.current_image_index = 0
            show_image(self.image_paths[self.current_image_index])

        # 创建 QLabel 用于显示图像
        self.image_label2 = QLabel()
        self.image_label2.setFixedSize(320, 395)  # 设置图像大小

        # 创建用于切换图像的按钮
        self.prev_button = QPushButton("<")
        self.next_button = QPushButton(">")
        # 为按钮绑定点击事件
        self.prev_button.clicked.connect(show_previous_image)
        self.next_button.clicked.connect(show_next_image)



        # 在界面上显示第一张图像
        if self.image_paths:
            self.current_image_index = 0
            show_image(self.image_paths[self.current_image_index])


        self.page2_layout.addWidget(pie_chart_canvas, row, 1)  # 扇形图在第一列
        self.page2_layout.addWidget(bar_chart_canvas, row, 2)  # 条形图在第二列
        self.page2_layout.addWidget(self.prev_button, row, 3)
        self.page2_layout.addWidget(self.image_label2, row, 4)
        self.page2_layout.addWidget(self.next_button, row, 5)

        row += 1
        self.page2_layout.addWidget(self.text_edit, row, 1, 1, 5)   # 文本编辑器占据一行5列

        # 设置 text_edit 的最大尺寸
        self.text_edit.setMaximumSize(QSize(1115, 200))



    def prev_page(self):
        # 显示前一页内容
        self.visualize_image_count(self.current_page - 1,r'E:\new-learning\zhiwuquexianjianche\output')

    def next_page(self):
        # 显示后一页内容
        self.visualize_image_count(self.current_page + 1,r'E:\new-learning\zhiwuquexianjianche\output')

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())


    def save_to_txt_and_upload_to_hdfs(self):
        # 连接到 MongoDB
        client_mongodb = MongoClient('mongodb://localhost:27017/')
        db = client_mongodb['zhiwu']
        # 替换为您的数据库名称
        collection = db[self.username]  # 替换为您的集合名称

        # 连接到 HDFS
        client_hdfs = InsecureClient('http://localhost:9870', user='hadoop')

        # 获取当前已上传的文件数
        uploaded_files = len(client_hdfs.list('/data'))

        # 查询集合中的所有文档
        documents = collection.find()

        # 定义要保存数据的文件路径
        output_file = f'batch{uploaded_files + 1}.txt'

        # 将文档数据写入文本文件
        with open(output_file, 'w') as file:
            for document in documents:
                # 将文档转换为字符串，并写入文件
                file.write(str(document) + '\n')

        print("数据已保存到文件:", output_file)

        # 上传本地文件到HDFS
        client_hdfs.upload(f'/data/{output_file}', output_file)


    def run_model(self,imagedata):
        thread = threading.Thread(target=self.worker.run_bigmodel, args=(imagedata,))
        thread.start()

    # def run_pdx_model(self, folder_path, save_path):
    #     pdx_instance = Pdx_model(folder_path, save_path)
    #     thread = threading.Thread(target=pdx_instance.run)
    #     thread.start()

    def on_model_transmit(self, assistant_content):
        # 将模型输出显示在文本框中
        self.text_edit.setText(assistant_content)

    def on_model_finished(self, assistant_content):
        # 将模型输出显示在文本框中
        global answer
        answer = ""
class PredictionThread(QThread):
    data_result = pyqtSignal(list, float, str)


    predictionFinished = pyqtSignal()

    def __init__(self, folder_path, save_path):
        super().__init__()

        self.folder_path = folder_path
        self.save_path = save_path

        self.stop_requested = False  # 添加停止标志属性

    def run(self):

        model_dir = "./inference_model/inference_model/cascade_rcnn_r50_vd_fpn_ssld_2x_coco"
        detector = load_model(model_dir)
        # predictor = pdx.deploy.Predictor(
        #     r'E:\new-learning\zhiwuquexianjianche\model\point\P0010-T0017_export_model\inference_model\inference_model')
        print("-----------------------模型载入成功-----------------------")

        for filename in os.listdir(self.folder_path):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_file = os.path.join(self.folder_path, filename)
                image_file = r'' + image_file  # 原始字符串
                # image_file = image_file.replace('\\', '\\\\')  # 将路径中的反斜杠替换为双反斜杠

                # QApplication.processEvents()  # 更新界面
                print("-----------------------分割线-----------------------")
                if self.stop_requested:  # 检查停止标志
                    break  # 如果停止被请求，退出循环
                # time.sleep(0.5)
                try:
                    results, class_name, score, im, frame = detect_objects(detector, image_file)
                    # result = predictor.predict(img_file=image_file)
                    # print(result)
                    #self.pdx_result.emit(result)

                    # 假设预测结果为一个字符串值 class_name
                    prediction_value = class_name  # 这里仅做示例，实际应根据预测结果设置值
                    # 检查对应值的文件夹是否存在，不存在则创建
                    # 获取当前日期并格式化为字符串（年-月-日）
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    # 将当前日期赋值给batch
                    batch = current_date
                    output_folder = os.path.join(str(self.save_path), batch, str(prediction_value))
                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)
                    # 将图片移动到对应的文件夹中

                    output_file = os.path.join(output_folder, filename)


                    # time.sleep(1.2)

                    ##这个是将原文件移动到对应文件夹
                    # os.rename(image_file, output_file)

                    ##这个是直接保存标注图片到对应文件夹
                    if isinstance(im, np.ndarray):
                        # 如果是 NumPy 数组，则转换为 Image 对象并保存
                        im = Image.fromarray(im)
                        im.save(output_file)
                    else:
                        # 如果不是 NumPy 数组，则直接保存
                        im.save(output_file)
                    # 传数据到主线程
                    self.data_result.emit(class_name, score, output_file)

                    # ##这个是直接保存标注图片到对应文件夹
                    # if isinstance(frame, np.ndarray):
                    #     # 如果是 NumPy 数组，则转换为 Image 对象并保存
                    #     frame = Image.fromarray(frame)
                    #     frame.save(output_file)
                    # else:
                    #     # 如果不是 NumPy 数组，则直接保存
                    #     frame.save(output_file)
                    # # 传数据到主线程
                    # self.data_result.emit(class_name, score, output_file)

                except Exception as e:
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    # 将当前日期赋值给batch123
                    batch = current_date

                    output_folder = os.path.join(str(self.save_path), batch, "['normal']")
                    if not os.path.exists(output_folder):
                        os.makedirs(output_folder)

                    # 将图片移动到对应的文件夹中
                    output_file = os.path.join(output_folder, filename)

                    ##这个是将原文件移动到对应文件夹
                    #os.rename(image_file, output_file)
                    print(f"Error: {e}")
                    ##这个是直接保存标注图片到对应文件夹

                    if isinstance(im, np.ndarray):
                        # 如果是 NumPy 数组，则转换为 Image 对象并保存
                        im = Image.fromarray(im)
                        im.save(output_file)
                    else:
                        # 如果不是 NumPy 数组，则直接保存
                        im.save(output_file)
                    # 传数据到主线程
                    self.data_result.emit(class_name, score, output_file)

                    # if isinstance(frame, np.ndarray):
                    #     # 如果是 NumPy 数组，则转换为 Image 对象并保存
                    #     frame = Image.fromarray(frame)
                    #     frame.save(output_file)
                    # else:
                    #     # 如果不是 NumPy 数组，则直接保存
                    #     frame.save(output_file)
                    # # 传数据到主线程
                    # self.data_result.emit(class_name, score, output_file)

        print("-----------------------结束-----------------------")
        self.predictionFinished.emit()

class Worker(QObject):
    finished = pyqtSignal(str)
    answers = pyqtSignal(str)

    def run_bigmodel(self,imagedata):
        # 模拟大模型运行

        appid = "a39d2ed6"  # 填写控制台中获取的 APPID 信息
        api_secret = "ZDkzODYzYmFkYTUyOGE0ZGQzNjdmOTI5"  # 填写控制台中获取的 APISecret 信息
        api_key = "4b6e5242e0a5ddaa9bf7545c6bb53df1"  # 填写控制台中获取的 APIKey 信息
        #imagedata = open("image2.jpg", 'rb').read()

        imageunderstanding_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"  # 云端环境的服务地址
        text = [{"role": "user", "content": str(base64.b64encode(imagedata), 'utf-8'), "content_type": "image"}]

        class Ws_Param(object):
            # 初始化
            def __init__(self, APPID, APIKey, APISecret, imageunderstanding_url):
                self.APPID = APPID
                self.APIKey = APIKey
                self.APISecret = APISecret
                self.host = urlparse(imageunderstanding_url).netloc
                self.path = urlparse(imageunderstanding_url).path
                self.ImageUnderstanding_url = imageunderstanding_url

            # 生成url
            def create_url(self):
                # 生成RFC1123格式的时间戳
                now = datetime.now()
                date = format_date_time(mktime(now.timetuple()))

                # 拼接字符串
                signature_origin = "host: " + self.host + "\n"
                signature_origin += "date: " + date + "\n"
                signature_origin += "GET " + self.path + " HTTP/1.1"

                # 进行hmac-sha256进行加密
                signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                         digestmod=hashlib.sha256).digest()

                signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

                authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

                authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

                # 将请求的鉴权参数组合为字典
                v = {
                    "authorization": authorization,
                    "date": date,
                    "host": self.host
                }
                # 拼接鉴权参数，生成url
                url = self.ImageUnderstanding_url + '?' + urlencode(v)
                # print(url)
                # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
                return url

        # 收到websocket错误的处理
        def on_error(ws, error):
            print("### error:", error)

        # 收到websocket关闭的处理
        def on_close(ws, one, two):
            print(" ")

        # 收到websocket连接建立的处理
        def on_open(ws):
            thread.start_new_thread(run, (ws,))

        def run(ws, *args):
            data = json.dumps(gen_params(appid=ws.appid, question=ws.question))
            ws.send(data)

        # 收到websocket消息的处理
        def on_message(ws, message):
            # print(message)
            data = json.loads(message)
            code = data['header']['code']
            if code != 0:
                print(f'请求错误: {code}, {data}')
                ws.close()
            else:
                choices = data["payload"]["choices"]
                status = choices["status"]
                content = choices["text"][0]["content"]
                print(content, end="")
                global answer
                answer += content
                self.answers.emit(answer)
                # print(1)
                if status == 2:
                    ws.close()

        def gen_params(appid, question):
            """
            通过appid和用户的提问来生成请参数
            """

            data = {
                "header": {
                    "app_id": appid
                },
                "parameter": {
                    "chat": {
                        "domain": "image",
                        "temperature": 0.5,
                        "top_k": 4,
                        "max_tokens": 2028,
                        "auditing": "default"
                    }
                },
                "payload": {
                    "message": {
                        "text": question
                    }
                }
            }

            return data

        def getText(role, content):
            jsoncon = {}
            jsoncon["role"] = role
            jsoncon["content"] = content
            text.append(jsoncon)
            return text

        def getlength(text):
            length = 0
            for content in text:
                temp = content["content"]
                leng = len(temp)
                length += leng
            return length

        def checklen(text):
            # print("text-content-tokens:", getlength(text[1:]))
            while (getlength(text[1:]) > 8000):
                del text[1]
            return text

        def main(appid, api_key, api_secret, imageunderstanding_url, question):

            wsParam = Ws_Param(appid, api_key, api_secret, imageunderstanding_url)
            websocket.enableTrace(False)
            wsUrl = wsParam.create_url()
            ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close,
                                        on_open=on_open)
            ws.appid = appid
            # ws.imagedata = imagedata
            ws.question = question
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        # text.clear
        # Input = input("\n" +"问:")
        Input = "这是浸胶胶布的缺陷分布图，请根据缺陷的类别，缺陷的多少，回答浸胶胶布出现缺陷的原因，以及解决办法，并且预测未来缺陷数量的走向，内容不超过100字。"
        question = checklen(getText("user", Input))

        print("答:", end="")
        main(appid, api_key, api_secret, imageunderstanding_url, question)
        # getText("assistant", answer)
        # assistant_message = text[3]  # 获取助手消息
        # assistant_content = assistant_message['content']  # 助手消息内容
        #print(str(assistant_content))


        self.finished.emit("assistant_content")



# class Pdx_model(QObject):
#     pdx_result = pyqtSignal(list)
#
#     def __init__(self, folder_path, save_path):
#         super().__init__()
#         self.folder_path = folder_path
#         self.save_path = save_path
#         self.stop_requested = False
#
#     def run(self):
#         predictor = pdx.deploy.Predictor(
#             r'E:\new-learning\zhiwuquexianjianche\model\point\P0010-T0017_export_model\inference_model\inference_model')
#         print("-----------------------模型载入成功-----------------------")
#
#         # 遍历文件夹中的所有图片
#         for root, dirs, files in os.walk(self.folder_path):
#             for file in files:
#                 if file.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
#                     img_path = os.path.join(root, file)
#                     result = predictor.predict(img_file=img_path)
#                     if self.stop_requested:  # 检查停止标志
#                         break  # 如果停止被请求，退出循环
#                     # 将预测结果发送给信号
#                     self.pdx_result.emit(result)



def QDialogButton(param, self):
    pass



if __name__ == "__main__":
    answer = ""
    app = QApplication([])
    window = ImageProcessor()

    window.show()


    app.exec_()
