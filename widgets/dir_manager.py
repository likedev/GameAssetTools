import os
import subprocess
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
                               QListWidget, QListWidgetItem, QScrollArea, QFileDialog, QDialog, QFormLayout,
                               QMessageBox, QMenu, QDialogButtonBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QAction, QFont
from util import *
from db.file_manager_dao import *


class DirectoryManager(QWidget):
    def __init__(self):
        super().__init__()
        # //这是数据
        self.tags = []
        self.files = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        tagFileLayout = QHBoxLayout()
        tagLayout = QVBoxLayout()  # For tag-related widgets
        fileLayout = QVBoxLayout()  # For file-related widgets

        # Tag management area setup
        self.tagSearch = QLineEdit(self)
        self.tagSearch.setMinimumHeight(50)
        self.tagSearch.setPlaceholderText("Search tags...")
        self.tagSearch.returnPressed.connect(self.filterTags)

        def createClearBtn(callback):
            # 清空tag搜索
            clearTagBtn = QPushButton()
            clearTagBtn.setIcon(QIcon('./assets/icon/clear.svg'))
            clearTagBtn.setIconSize(QSize(30, 30))
            clearTagBtn.setMinimumHeight(50)
            clearTagBtn.setMinimumWidth(50)
            clearTagBtn.clicked.connect(callback)
            return clearTagBtn

        clearTagBtn = createClearBtn(self.clearTagSearchAndRefresh)
        self.tagFirstLine = QHBoxLayout()
        self.tagFirstLine.addWidget(clearTagBtn)
        self.tagFirstLine.addWidget(self.tagSearch)

        self.tagList = QListWidget(self)
        self.tagList.setIconSize(QSize(40, 40))
        self.tagList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tagList.customContextMenuRequested.connect(self.tagContextMenu)
        self.tagList.itemDoubleClicked.connect(self.tagDoubleClicked)
        addTagButton = QPushButton("Add Tag", self)
        addTagButton.setMinimumHeight(40)
        addTagButton.clicked.connect(self.showAddTagDialog)

        # File/Directory listing area setup
        self.fileSearch = QLineEdit(self)
        self.fileSearch.setMinimumHeight(50)
        self.fileSearch.setPlaceholderText("Search files...")
        self.fileSearch.returnPressed.connect(self.filterFiles)
        self.fileList = QListWidget(self)
        self.fileList.setIconSize(QSize(40, 40))

        self.fileList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fileList.customContextMenuRequested.connect(self.fileContextMenu)

        addFileButton = QPushButton("Add File/Directory", self)
        addFileButton.setMinimumHeight(40)
        addFileButton.clicked.connect(self.showAddFileDialog)

        fileClearBtn = createClearBtn(self.clearFileSearchAndRefresh)
        self.fileFirstLine = QHBoxLayout()
        self.fileFirstLine.addWidget(fileClearBtn)
        self.fileFirstLine.addWidget(self.fileSearch)

        # Assembling the layout
        tagLayout.addLayout(self.tagFirstLine)
        tagLayout.addWidget(self.tagList)
        tagLayout.addWidget(addTagButton)

        fileLayout.addLayout(self.fileFirstLine)
        fileLayout.addWidget(self.fileList)
        fileLayout.addWidget(addFileButton)

        tagFileLayout.addLayout(tagLayout, 30)
        tagFileLayout.addLayout(fileLayout, 70)
        layout.addLayout(tagFileLayout)

        self.updateTagDisplay()
        self.updateFileDisplay()

    def tagDoubleClicked(self, item):
        self.fileSearch.setText(";" + item.text() + ";")
        self.filterFiles()

    def updateTagDisplay(self):
        self.tagList.clear()
        self.tags = get_tags()

        # print("所有的tag 数据", self.tags)

        visible_tags = [tag for tag in self.tags if self.tagSearch.text().lower() in tag['name'].lower()]
        for tag in visible_tags:
            item = QListWidgetItem(tag['name'])
            item.setSizeHint(QSize(50, 50))
            item.setFont(QFont('Arial', 15))
            if tag['icon']:
                q_icon = QIcon(tag['icon'])
            else:
                q_icon = QIcon()
            item.setIcon(q_icon)
            set_item_data(item, tag)
            self.tagList.addItem(item)

    def clearTagSearchAndRefresh(self):
        self.tagSearch.clear()
        self.updateTagDisplay()

    def tagContextMenu(self, position):
        if not self.tagList.currentItem():
            return
        menu = QMenu()
        editAction = menu.addAction("Edit")

        item_data = get_item_data(self.tagList.currentItem())
        print("tag data", item_data)
        editAction.triggered.connect(lambda: self.editTagDialog(item_data))

        delAction = menu.addAction("Delete")
        delAction.triggered.connect(lambda: self.del_tag(item_data))

        menu.exec_(self.tagList.mapToGlobal(position))

    def del_tag(self, item_data):
        reply = QMessageBox.question(
            self,
            "确认删除",
            "你确定要删除这个文件吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            delete_fm_tag(item_data['id'])
            self.updateTagDisplay()

    def clearFileSearchAndRefresh(self):
        self.fileSearch.clear()
        self.updateFileDisplay()

    def fileContextMenu(self, position):
        if not self.fileList.currentItem():
            return
        f = self.fileList.currentItem()
        menu = QMenu()

        item_data = get_item_data(f)

        is_file = os.path.isfile(item_data['path'])

        openFeAction = menu.addAction("Open In Folder Expoler")
        openFeAction.setIcon(QIcon("./assets/icon/file_exp.png"))
        openFeAction.triggered.connect(lambda: self.OpenInExplorer(item_data))

        openVscAction = menu.addAction("vscode")
        openVscAction.setIcon(QIcon("./assets/icon/vscode.svg"))
        openVscAction.triggered.connect(lambda: self.openInVsc(item_data))

        if is_file:
            exeAction = menu.addAction("start")
            exeAction.setIcon(QIcon("./assets/icon/start.svg"))
            exeAction.triggered.connect(lambda: self.start_file(item_data))

        menu.addSeparator()

        editAction = menu.addAction("Edit File Config")
        editAction.setIcon(QIcon("./assets/icon/edit.svg"))
        editAction.triggered.connect(lambda: self.showAddFileDialog(item_data))

        # //删除按钮
        delAction = menu.addAction("Delete")
        delAction.setIcon(QIcon("./assets/icon/del.svg"))
        delAction.triggered.connect(lambda: self.del_file(item_data))

        menu.exec_(self.fileList.mapToGlobal(position))

    def start_file(self, item_data):
        project_path = item_data['path']
        if os.path.isfile(project_path):
            os.startfile(project_path)

    def openInVsc(self, item_data):
        # 获取 VS Code 的安装路径，如果 VS Code 已添加到系统 PATH 中，可以直接使用 'code'
        vscode_path = 'D:\\apps\\Microsoft VS Code\\Code.exe'
        path = item_data['path']
        # 如果路径是一个目录
        if os.path.isdir(path):
            subprocess.run([vscode_path, path])
        # 如果路径是一个文件
        elif os.path.isfile(path):
            subprocess.run([vscode_path, '-r', path])
        else:
            print(f"路径 {path} 不存在或不是一个文件/目录")

    def del_file(self, item_data):
        reply = QMessageBox.question(
            self,
            "确认删除",
            "你确定要删除这个文件吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            delete_fm_file(item_data['id'])
            self.updateFileDisplay()

    def OpenInExplorer(self, file_data):
        path = file_data['path']

        if os.path.exists(path):
            if os.path.isdir(path):
                # 如果是目录，直接打开这个目录
                subprocess.run(['explorer', os.path.normpath(path)])
            else:
                # 如果是文件，打开文件所在目录并选中这个文件
                subprocess.run(['explorer', '/select,', os.path.normpath(path)])
        else:
            QMessageBox.warning(self, "Warning", "File or directory does not exist: " + path)

    def editTagDialog(self, tag_data=None):
        dialog = QDialog(self)
        dialog.setMinimumWidth(600)
        layout = QFormLayout(dialog)
        name = QLineEdit(dialog)

        icon_label = QLabel(dialog)

        icon = QPushButton("Select Icon", dialog)
        icon.clicked.connect(lambda: self.selectIcon(icon_label))
        layout.addRow("Name:", name)
        layout.addRow("Icon:", icon)
        layout.addRow("Preview:", icon_label)

        if tag_data:
            icon_label.setPixmap(QPixmap(tag_data['icon']).scaled(64, 64, Qt.KeepAspectRatio))
            icon_label.setToolTip(tag_data['icon'])
            name.setText(tag_data['name'])

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        if dialog.exec() == QDialog.Accepted:
            new_name = name.text().strip()
            if tag_data:
                # existing_tag.update({'name': new_name, 'icon': icon_label.toolTip()})
                update_tag_db(tag_data['id'], new_name, icon_label.toolTip())
            else:
                insert_tag(new_name, icon_label.toolTip())
            self.updateTagDisplay()

    def selectIcon(self, label):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.jpg *.jpeg *.bmp *.svg)")
        if file_name:
            label.setPixmap(QPixmap(file_name).scaled(64, 64, Qt.KeepAspectRatio))
            label.setToolTip(file_name)

    def updateFileDisplay(self):
        self.fileList.clear()
        self.files = get_files()

        def match_search_single(s_text, file):
            if s_text.lower() in file['tags'].lower():
                return True
            if s_text.lower() in file['alias'].lower():
                return True
            if s_text.lower() in file['path'].lower():
                return True
            return False

        def match_search(full_text, file):
            full_text = full_text.lower().strip()
            full_text_arr = full_text.split(" ")
            for word in full_text_arr:
                if not word:
                    continue
                if not match_search_single(word, file):
                    return False
            return True

        search_text = self.fileSearch.text().lower()
        if search_text.strip():
            visible_files = [file for file in self.files
                             if match_search(search_text, file)]
        else:
            visible_files = self.files
        for file in visible_files:
            item = QListWidgetItem(f"{file['alias']} [{file['tags']}]")
            item.setFont(QFont('Arial', 15))
            set_item_data(item, file)

            item_icon = get_icon_by_extension(file['path'])
            item.setIcon(item_icon)

            self.fileList.addItem(item)

    def showAddFileDialog(self, file_data=None):
        dialog = QDialog(self)
        dialog.setMinimumWidth(800)
        layout = QFormLayout(dialog)
        alias = QLineEdit(dialog)
        path = QLineEdit(dialog)

        radio_file = QRadioButton("file", self)
        radio_dir = QRadioButton("dir", self)
        radio_file.setChecked(True)  # 默认选择文件

        self.radio_file = radio_file
        self.radio_dir = radio_dir

        button_group = QButtonGroup(self)
        button_group.addButton(radio_file)
        button_group.addButton(radio_dir)

        browse = QPushButton("Browse", dialog)
        browse.clicked.connect(lambda: self.browsePath(path))
        tags = QLineEdit(dialog)

        layout.addRow("Alias:", alias)
        layout.addRow("文件类型:", self.radio_file)
        layout.addRow("目录类型:", self.radio_dir)
        layout.addRow("Path:", path)
        layout.addRow(browse)
        layout.addRow("Tags (comma-separated):", tags)

        if file_data:
            alias.setText(file_data['alias'])
            path.setText(file_data['path'])
            tags.setText(file_data['tags'])

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() == QDialog.Accepted:
            if file_data:
                update_file_db(file_data['id'], file_data['path'], alias.text(), tags.text())
            else:
                insert_file(path.text(), alias.text(), tags.text())
            self.updateFileDisplay()

    def browsePath(self, pathLineEdit):
        dialog = QFileDialog(self, "Select File or Folder")
        if self.radio_file.isChecked():
            dialog.setFileMode(QFileDialog.ExistingFile)  # 选择文件
        elif self.radio_dir.isChecked():
            dialog.setFileMode(QFileDialog.Directory)  # 选择文件夹

        if dialog.exec() == QFileDialog.Accepted:
            selected_path = dialog.selectedFiles()[0]  # 获取选中的路径
            pathLineEdit.setText(selected_path)

    def filterTags(self):
        self.updateTagDisplay()

    def showAddTagDialog(self):
        self.editTagDialog()

    def filterFiles(self):
        self.updateFileDisplay()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dm = DirectoryManager()
    dm.show()
    sys.exit(app.exec())
