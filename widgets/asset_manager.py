import sys
import os
import subprocess

from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLineEdit, QListWidget, QLabel, QListWidgetItem,
                               QVBoxLayout, QHBoxLayout, QWidget, QCheckBox, QMenu, QDialog, QDialogButtonBox,
                               QMessageBox, QScrollArea)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon

import game_assets_dao
import search
from util import open_file_or_dir_in_explorer


class AssetManager(QWidget):
    def __init__(self):
        super().__init__()
        self.search_layout_height = 40
        self.initUI()

    def initUI(self):

        self.clearSearchButton = QPushButton(self)
        self.clearSearchButton.setIcon(QIcon("./assets/icon/clear.svg"))
        self.clearSearchButton.setFixedSize(QSize(self.search_layout_height, self.search_layout_height))
        self.clearSearchButton.clicked.connect(self.clearSearch)

        self.searchBar = QLineEdit(self)
        self.searchBar.setFixedHeight(self.search_layout_height)
        self.searchBar.returnPressed.connect(self.onSearch)

        self.searchButton = QPushButton(self)
        self.searchButton.setIcon(QIcon("./assets/icon/search.svg"))
        self.searchButton.setFixedSize(QSize(self.search_layout_height, self.search_layout_height))
        self.searchButton.clicked.connect(self.onSearch)

        self.listViewButton = QPushButton(self)
        self.listViewButton.setFixedSize(QSize(self.search_layout_height, self.search_layout_height))
        self.listViewButton.setIcon(QIcon("./assets/icon/displaymode.svg"))
        self.listViewButton.clicked.connect(lambda: self.toggleDisplayMode())

        self.tags = ["模型", "贴图", "材质"]
        self.checkboxes = [QCheckBox(tag, self) for tag in self.tags]

        self.resultList = QListWidget(self)
        self.resultList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.resultList.customContextMenuRequested.connect(self.openMenu)
        self.resultList.setIconSize(QSize(100, 100))
        self.resultList.setDragEnabled(False)
        self.resultList.setAcceptDrops(False)
        self.resultList.setDropIndicatorShown(False)
        self.resultList.setDragDropMode(QListWidget.DragDropMode.NoDragDrop)
        self.resultList.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.resultList.clicked.connect(self.onResultClick)
        self.toggleDisplayMode()

        self.createDetailSection()

        topLayout = QHBoxLayout()
        topLayout.addWidget(self.clearSearchButton)
        topLayout.addWidget(self.searchBar)
        topLayout.addWidget(self.searchButton)
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

        self.setLayout(mainLayout)
        self.show()

    def clearSearch(self):
        self.searchBar.clear()
        self.resultList.clear()
        self.onSearch()

    def createDetailSection(self):
        self.detailLabel = QLabel("资产详情：", self)
        self.detailLabel.setStyleSheet("font-size: 10pt;")
        self.detailLabel.setWordWrap(True)
        self.detailLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.detailLabel.setTextFormat(Qt.TextFormat.RichText)

        self.previewLabel = QLabel(self)
        self.previewLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.detailLayout = QVBoxLayout()
        self.detailLayout.addWidget(self.previewLabel)
        self.detailLayout.addWidget(self.detailLabel)

        self.picsLayout = QVBoxLayout()
        self.detailLayout.addLayout(self.picsLayout)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        self.detailContainer = QWidget()
        self.detailContainer.setLayout(self.detailLayout)

        self.scrollArea.setWidget(self.detailContainer)

    def onSearch(self):
        self.resultList.clear()
        search_text = self.searchBar.text().strip()
        param = {'text': search_text}
        print("search_text:", search_text)
        data = search.search_game_assets_any_match_title_note(param)
        print("搜索数目", len(data))
        for item in data:
            listItem = QListWidgetItem(QIcon(item['preview']), item['title'])
            listItem.setData(Qt.ItemDataRole.UserRole, item)
            listItem.setFlags(listItem.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.resultList.addItem(listItem)

    def onResultClick(self, index):
        item = self.resultList.item(index.row())
        if item:
            item_data = item.data(Qt.ItemDataRole.UserRole)
            if item_data:
                preview_path = item_data.get('preview', '')
                if os.path.exists(preview_path):
                    pixmap = QPixmap(preview_path)
                    self.previewLabel.setPixmap(pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding))
                web_url = item_data.get('web_url', '#')
                details = f"<br><span style='color:red;'>title:</span>{item_data.get('title', '无')}" \
                          f"<br><span style='color:red;'>物理路径：</span>{item_data.get('file_path', '无')}" \
                          f"<br><span style='color:red;'>web_url:</span>{web_url}" \
                          f"<br><span style='color:red;'>标签</span>：{', '.join(item_data.get('tag', []))}" \
                          f"<br><span style='color:red;'>Note：</span>{item_data.get('note', '无').strip()}"
                self.detailLabel.setText(details)

                while self.picsLayout.count():
                    item = self.picsLayout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                pics_local = item_data.get('pics_local', [])
                for pic_path in pics_local:
                    if os.path.exists(pic_path):
                        pic_label = QLabel(self)
                        pixmap = QPixmap(pic_path)
                        pic_label.setPixmap(pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding))
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
        current_item = self.resultList.currentItem()
        if current_item:
            item_data = current_item.data(Qt.ItemDataRole.UserRole)
            print("item_data", item_data)
            if 'file_path' in item_data:
                file_path = item_data['file_path']
                if not open_file_or_dir_in_explorer(file_path):
                    QMessageBox.warning(self, "失败", "目录不存在")
            else:
                QMessageBox.warning(self, "path 不存在")
        else:
            QMessageBox.warning(self, "未选中")

    def editItem(self):
        dialog = AssetEditDialog(self)
        if dialog.exec():
            print("保存编辑")

    def toggleDisplayMode(self):
        view_mode = self.resultList.viewMode()
        if view_mode == QListWidget.ViewMode.IconMode:
            self.resultList.setViewMode(QListWidget.ViewMode.ListMode)
            self.resultList.setIconSize(QSize(100, 100))
            self.resultList.setGridSize(QSize(100, 100))
        else:
            self.resultList.setViewMode(QListWidget.ViewMode.IconMode)
            self.resultList.setIconSize(QSize(290, 300))
            self.resultList.setGridSize(QSize(300, 330))
            self.resultList.verticalScrollBar().setSingleStep(40)


class AssetEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("编辑资产")
        self.pathEdit = QLineEdit(self)
        self.descriptionEdit = QLineEdit(self)
        self.typeEdit = QLineEdit(self)
        self.tagEdit = QLineEdit(self)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                                        self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

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
