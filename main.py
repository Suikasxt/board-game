import sys
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QLineEdit, QTextEdit, QLabel, QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread, Qt

class QLabelCenter(QLabel):
    def __init__(self, text = ''):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)

class Grid(QWidget):
    pushSign = pyqtSignal(int, int)
    def __init__(self, parent, index_x, index_y, size):
        super().__init__(parent)
        self.index_x = index_x
        self.index_y = index_y
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabelCenter('+'))
        self.setFixedSize(size, size)
    def mousePressEvent(self, QMouseEvent):
        self.pushSign.emit(self.index_x, self.index_y)


class Chessboard(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.myWidget = []

    def reset(self, width, height):
        for w in self.myWidget:
            if w:
                w.setParent(None)
        self.myWidget = []
        for i in range(height):
            for j in range(width):
                gird = Grid(self, i, j, 100)
                self.grid_layout.addWidget(gird, *(i,j))
                self.myWidget.append(gird)
        
class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        board = Chessboard(self)
        self.setCentralWidget(board)
        board.reset(5, 5)
        #file = open('main.qss', 'r')
        #self.setStyleSheet(file.read())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    w = mainWindow()
    w.show()
    sys.exit(app.exec_())