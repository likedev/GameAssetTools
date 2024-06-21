import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLineEdit, QListWidget, QLabel, QListWidgetItem,
                             QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QMenu, QAction, QDialog, QVBoxLayout,
                             QLineEdit, QDialogButtonBox, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
import os
import subprocess
import game_assets_dao
import search


class AssetManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QtGui.QIcon(r"C:\Users\Administrator\Pictures\icon.png"))

        # 创建搜索栏
        self.searchBar = QLineEdit(self)
        self.searchBar.returnPressed.connect(self.onSearch)

        # 创建搜索按钮
        self.searchButton = QPushButton("搜索", self)
        self.searchButton.clicked.connect(self.onSearch)

        # 创建标签搜索项
        self.tags = ["模型", "贴图", "材质"]
        self.checkboxes = [QCheckBox(tag, self) for tag in self.tags]

        # 添加展示模式切换按钮
        self.listViewButton = QPushButton('展示', self)
        self.listViewButton.clicked.connect(lambda: self.toggleDisplayMode())

        # 创建搜索结果列表
        self.resultList = QListWidget(self)
        self.resultList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.resultList.customContextMenuRequested.connect(self.openMenu)
        self.resultList.setIconSize(QSize(100, 100))
        # 禁用拖放功能
        self.resultList.setDragEnabled(False)
        self.resultList.setAcceptDrops(False)
        self.resultList.setDropIndicatorShown(False)
        self.resultList.setDragDropMode(QListWidget.NoDragDrop)
        self.resultList.setSelectionMode(QListWidget.NoSelection)
        self.resultList.clicked.connect(self.onResultClick)
        self.toggleDisplayMode()

        self.createDetailSection()

        # 布局
        topLayout = QHBoxLayout()
        topLayout.addWidget(self.searchBar)
        topLayout.addWidget(self.searchButton)

        # 将展示模式按钮添加到布局
        topLayout.addWidget(self.listViewButton)

        tagLayout = QHBoxLayout()
        for checkbox in self.checkboxes:
            tagLayout.addWidget(checkbox)

        leftLayout = QVBoxLayout()
        leftLayout.addLayout(topLayout)
        leftLayout.addLayout(tagLayout)
        leftLayout.addWidget(self.resultList)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(leftLayout, 2)
        mainLayout.addWidget(self.scrollArea, 1)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        self.setGeometry(300, 300, 2800, 1800)
        self.setWindowTitle('夏天资产管理器')
        self.show()

    # 详情区域
    def createDetailSection(self):
        # 创建详情展示区
        self.detailLabel = QLabel("资产详情：", self)
        self.detailLabel.setStyleSheet("font-size: 14pt;")
        self.detailLabel.setWordWrap(True)
        self.detailLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.detailLabel.setTextFormat(Qt.RichText)

        # 创建用于显示预览图的标签
        self.previewLabel = QLabel(self)
        self.previewLabel.setAlignment(Qt.AlignCenter)  # 图像居中显示

        # 详情布局，包括预览图和文本
        self.detailLayout = QVBoxLayout()
        self.detailLayout.addWidget(self.previewLabel)
        self.detailLayout.addWidget(self.detailLabel)

        # 创建一个新的布局用于图片
        self.picsLayout = QVBoxLayout()
        # 添加这个新布局到 detailLayout
        self.detailLayout.addLayout(self.picsLayout)

        # 创建一个滚动区域
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)  # 允许内容调整大小

        # 创建一个容器部件并将您的 detailLayout 设置到这个部件上
        self.detailContainer = QWidget()
        self.detailContainer.setLayout(self.detailLayout)

        # 将容器部件设置为滚动区域的子部件
        self.scrollArea.setWidget(self.detailContainer)

    def onSearch(self):
        self.resultList.clear()
        search_text = self.searchBar.text().strip()
        if not search_text:
            search_text = ""
        param = {
            'text': search_text
        }
        print("search_text:", search_text)
        data = search.search_game_assets_any_match_title_note(param)
        print("搜索数目", len(data))
        for item in data:
            listItem = QListWidgetItem(QIcon(item['preview']), item['title'])
            listItem.setData(Qt.UserRole, item)  # 存储整个字典
            listItem.setFlags(listItem.flags() & ~Qt.ItemIsEditable)
            self.resultList.addItem(listItem)

    def onResultClick(self, index):
        item = self.resultList.item(index.row())
        if item:
            item_data = item.data(Qt.UserRole)
            if item_data:
                # 加载并显示预览图
                preview_path = item_data.get('preview', '')
                if os.path.exists(preview_path):
                    pixmap = QPixmap(preview_path)
                    self.previewLabel.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatioByExpanding))  # 调整尺寸
                # 显示其他详情
                web_url = item_data.get('web_url', '#')
                details = f"<br><span style='color:red;'>title:</span>{item_data.get('title', '无')}" \
                          f"<br><span style='color:red;'>物理路径：</span>{item_data.get('file_path', '无')}" \
                          f"<br><span style='color:red;'>web_url:</span>{web_url}" \
                          f"<br><span style='color:red;'>标签</span>：{', '.join(item_data.get('tag', []))}" \
                          f"<br><span style='color:red;'>Note：</span>{item_data.get('note', '无').strip()}"
                self.detailLabel.setText(f"{details}")

                # 清除旧的图片
                while self.picsLayout.count():
                    item = self.picsLayout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                # 动态添加新的图片
                pics_local = item_data.get('pics_local', [])
                pic_local_idx = 0
                for pic_path in pics_local:
                    if pic_local_idx == 0:
                        pic_local_idx += 1
                        continue
                    if os.path.exists(pic_path):
                        pic_label = QLabel(self)
                        pixmap = QPixmap(pic_path)
                        pic_label.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatioByExpanding))  # 调整尺寸
                        self.picsLayout.addWidget(pic_label)

        else:
            self.detailLabel.setText("资产详情：无可用信息")
            self.previewLabel.clear()

    def openMenu(self, position):
        menu = QMenu()
        editAction = menu.addAction("编辑")
        openAction = menu.addAction("打开文件位置")

        action = menu.exec_(self.resultList.viewport().mapToGlobal(position))

        if action == editAction:
            self.editItem()
        elif action == openAction:
            self.openFileLocation()

    def openFileLocation(self):
        # 获取当前选中项的文件路径
        current_item = self.resultList.currentItem()
        if current_item:
            item_data = current_item.data(Qt.UserRole)
            if 'path' in item_data:
                file_path = item_data['path']  # 获取存储的文件路径
                folder = os.path.dirname(file_path)
                # os.startfile(folder)
                subprocess.Popen(f'explorer "{folder}"')
            else:
                QMessageBox.warning(self, "path 不存在")
        else:
            QMessageBox.warning(self, "未选中")

    def editItem(self):
        dialog = EditDialog(self)
        if dialog.exec_():
            print("保存编辑")  # 这里应该是保存编辑的逻辑

    def toggleDisplayMode(self):
        view_mode = self.resultList.viewMode()

        if view_mode == QListWidget.IconMode:
            # 实现列表展示模式
            self.resultList.setViewMode(QListWidget.ListMode)
            self.resultList.setIconSize(QSize(100, 100))
            self.resultList.setGridSize(QSize(100, 100))  # 调整网格大小
        else:
            # 实现大方块图展示模式
            self.resultList.setViewMode(QListWidget.IconMode)
            self.resultList.setIconSize(QSize(500, 500))  # 可以根据需要调整图标大小
            self.resultList.setGridSize(QSize(500, 500))  # 调整网格大小
            self.resultList.verticalScrollBar().setSingleStep(40)


class EditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("编辑资产")

        # 创建编辑表单
        self.pathEdit = QLineEdit(self)
        self.descriptionEdit = QLineEdit(self)
        self.typeEdit = QLineEdit(self)
        self.tagEdit = QLineEdit(self)

        # 创建按钮
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        # 布局
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("物理路径"))
        layout.addWidget(self.pathEdit)
        layout.addWidget(QLabel("描述"))
        layout.addWidget(self.descriptionEdit)
        layout.addWidget(QLabel("类型"))
        layout.addWidget(self.typeEdit)
        layout.addWidget(QLabel("标签"))
        layout.addWidget(self.tagEdit)
        layout.addWidget(self.buttons)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AssetManager()
    sys.exit(app.exec_())
