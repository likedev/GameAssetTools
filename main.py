import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget,
                               QSizePolicy, QHBoxLayout)
from PySide6.QtCore import Qt

from widgets.asset_manager import AssetManager
from widgets.dir_manager import DirectoryManager


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon("./assets/find.svg"))
        # Main widget
        mainWidget = QWidget()

        # Create the button column layout
        buttonLayout = QVBoxLayout()
        buttonLayout.setSizeConstraint(QVBoxLayout.SetFixedSize)  # Make button layout fixed size

        # Buttons that switch the views in the stacked widget
        self.buttons = [
            QPushButton(f"搜索"),
            QPushButton(f"目录"),
            QPushButton(f"TODO"),
            QPushButton(f"TODO"),
        ]
        for button in self.buttons:
            button.clicked.connect(self.switchView)
            buttonLayout.addWidget(button)
            button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)  # Make buttons expand equally

        # Stacked widget for displaying different views
        self.stackedWidget = QStackedWidget()

        # AssetManager will be the first view
        self.stackedWidget.addWidget(AssetManager())  # Assuming AssetManager is a QWidget

        # 在这个添加 panel
        self.stackedWidget.addWidget(DirectoryManager())
        # Placeholder widgets for the other functions
        for i in range(2):
            placeholder = QWidget()
            layout = QVBoxLayout()
            placeholder.setLayout(layout)
            layout.addWidget(QPushButton(f"Placeholder Content {i + 2}"))
            self.stackedWidget.addWidget(placeholder)

        # Horizontal layout to combine buttons and stacked widget
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addLayout(buttonLayout, 1)  # Buttons take up a smaller fixed portion of the layout
        horizontalLayout.addWidget(self.stackedWidget, 11)  # Stacked widget takes up the remaining space

        # Set the main widget's layout to the horizontal layout
        mainWidget.setLayout(horizontalLayout)

        self.setCentralWidget(mainWidget)
        # Set geometry and title of the main window
        self.setGeometry(100, 100, 1600, 900)
        self.setWindowTitle('Main Application Interface')
        self.show()
        print("Main Application Interface")

    def switchView(self):
        # Set the current index of the stacked widget based on the button clicked
        index = self.buttons.index(self.sender())
        self.stackedWidget.setCurrentIndex(index)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainApplication()
    mainWindow.show()
    sys.exit(app.exec())
