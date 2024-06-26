import os
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
                               QLineEdit, QLabel, QFileDialog, QGridLayout, QDialog, QFormLayout, QListWidgetItem,
                               QMessageBox)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame


class AddDirectoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Directory")
        self.layout = QFormLayout(self)

        self.aliasLineEdit = QLineEdit()
        self.selectDirectoryButton = QPushButton("Select Directory")
        self.selectDirectoryButton.clicked.connect(self.select_directory)

        self.layout.addRow("Alias:", self.aliasLineEdit)
        self.layout.addRow("Directory:", self.selectDirectoryButton)

        self.acceptButton = QPushButton("Add")
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)

        self.layout.addRow(self.acceptButton, self.cancelButton)
        self.directory_path = ""

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory_path = directory
            self.selectDirectoryButton.setText(f"Selected: {os.path.basename(directory)}")

    def get_values(self):
        return self.aliasLineEdit.text(), self.directory_path


class ImageSearchApp(QWidget):
    def __init__(self):
        super().__init__()

        # Layout setup
        self.mainLayout = QHBoxLayout()
        self.leftPanel = QVBoxLayout()
        self.rightPanel = QVBoxLayout()

        # Left panel directory search setup
        self.leftSearchBox = QLineEdit()
        self.leftSearchBox.setPlaceholderText("Search directories...")
        self.leftSearchBox.returnPressed.connect(self.filter_directories)
        self.clearLeftSearchButton = QPushButton("Clear")
        self.clearLeftSearchButton.clicked.connect(self.clear_left_search)
        self.leftPanel.addWidget(self.leftSearchBox)
        self.leftPanel.addWidget(self.clearLeftSearchButton)

        # Directory list setup
        self.dirList = QListWidget()
        self.dirList.itemDoubleClicked.connect(self.on_directory_selected)
        self.addButton = QPushButton("Add Directory")
        self.addButton.clicked.connect(self.show_add_directory_dialog)
        self.leftPanel.addWidget(self.dirList)
        self.leftPanel.addWidget(self.addButton)

        # Right panel setup
        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("Search for images...")
        self.searchBox.returnPressed.connect(self.update_display)
        self.clearRightSearchButton = QPushButton("Clear")
        self.clearRightSearchButton.clicked.connect(self.clear_right_search)
        self.rightPanel.addWidget(self.searchBox)
        self.rightPanel.addWidget(self.clearRightSearchButton)

        self.showImagesOnlyCheckbox = QPushButton("Show Images Only", checked=True)
        self.showImagesOnlyCheckbox.setCheckable(True)
        self.showImagesOnlyCheckbox.toggled.connect(self.update_display)
        self.rightPanel.addWidget(self.showImagesOnlyCheckbox)

        self.imageDisplay = QListWidget()
        self.imageDisplay.setResizeMode(QListWidget.Adjust)
        self.imageDisplay.setViewMode(QListWidget.IconMode)
        self.imageDisplay.setSpacing(10)  # Adjust spacing between items as needed
        self.rightPanel.addWidget(self.imageDisplay)

        # Main layout assembly
        self.mainLayout.addLayout(self.leftPanel, 1)
        self.mainLayout.addLayout(self.rightPanel, 3)
        self.setLayout(self.mainLayout)

        self.directories = {}
        self.files = []
        self.current_directory = None

    def show_add_directory_dialog(self):
        dialog = AddDirectoryDialog(self)
        if dialog.exec():
            alias, directory = dialog.get_values()
            if alias and directory:
                self.directories[alias] = directory
                self.dirList.addItem(alias)

    def on_directory_selected(self, item):
        alias = item.text()
        if alias in self.directories:
            self.current_directory = self.directories[alias]
            self.index_files(self.current_directory)

    def index_files(self, path):
        self.files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                if full_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    self.files.append(full_path)
                else:
                    self.files.append(None)
        self.update_display()

    def update_display(self):
        search_term = self.searchBox.text().lower()
        self.clear_display()

        for file_path in self.files:
            if file_path and ((self.showImagesOnlyCheckbox.isChecked() and file_path.lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.gif', '.bmp'))) or not self.showImagesOnlyCheckbox.isChecked()):
                if search_term in file_path.lower():
                    # Frame for each image and its filename
                    frame = QFrame()
                    frameLayout = QVBoxLayout(frame)
                    frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

                    label = QLabel(os.path.basename(file_path))
                    label.setAlignment(Qt.AlignCenter)  # Center-align the filename

                    pixmap = QPixmap(file_path)
                    pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)  # Adjust size as needed
                    imageLabel = QLabel()
                    imageLabel.setPixmap(pixmap)
                    imageLabel.setAlignment(Qt.AlignCenter)  # Center-align the image within its label

                    frameLayout.addWidget(imageLabel)
                    frameLayout.addWidget(label)

                    # Create QListWidgetItem and set its widget to frame
                    item = QListWidgetItem(self.imageDisplay)
                    item.setSizeHint(frame.sizeHint())  # Ensure the list respects the size of the frame
                    self.imageDisplay.addItem(item)
                    self.imageDisplay.setItemWidget(item, frame)

    def clear_display(self):
        self.imageDisplay.clear()

    def filter_directories(self):
        filter_text = self.leftSearchBox.text().lower()
        self.dirList.clear()
        for alias, path in self.directories.items():
            if filter_text in alias.lower() or filter_text in path.lower():
                self.dirList.addItem(alias)

    def clear_left_search(self):
        self.leftSearchBox.clear()
        self.dirList.clear()
        for alias in self.directories:
            self.dirList.addItem(alias)

    def clear_right_search(self):
        self.searchBox.clear()
        self.update_display()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSearchApp()
    window.setWindowTitle('Image Search App')
    window.show()
    sys.exit(app.exec())
