from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        button = QPushButton("Press Me!")
        
        self.setFixedSize(QSize(400,300))

        self.setCentralWidget(button)

app = QApplication(sys.argv)

# window = QPushButton("Push me")
window = MainWindow()

window.show()

app.exec()