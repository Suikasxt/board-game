import sys
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QListView, QPushButton, QComboBox, QGridLayout, QHBoxLayout, QVBoxLayout, QApplication, QLineEdit, QTextEdit, QLabel, QMessageBox
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QPixmap
from proxy import ClientProxy

class QLabelCenter(QLabel):
    def __init__(self, text = ''):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)

class MyEdit(QWidget):
    def __init__(self, label, text):
        super().__init__()

        hlayout = QHBoxLayout()
        self.setLayout(hlayout)

        self.label = QLabelCenter(label)
        self.edit = QLineEdit(text)
        hlayout.addWidget(self.label, 1)
        hlayout.addWidget(self.edit, 3)

class Grid(QWidget):
    pushSign = pyqtSignal(int, int)
    def __init__(self, parent, coord_x, coord_y, grid_size):
        super().__init__(parent)
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.grid_size = grid_size
        
        self.setFixedSize(grid_size, grid_size)
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        self.label = QLabelCenter()
        self.layout.addWidget(self.label)
        self.setState(-1)
    
    def setState(self, state):
        GridPix = QPixmap('../img/grid.png')
        WhitePiecePix = QPixmap('../img/white_piece.png')
        BlackPiecePix = QPixmap('../img/black_piece.png')
        if state == -1:
            pix = GridPix
        elif state == 0:
            pix = WhitePiecePix
        elif state == 1:
            pix = BlackPiecePix
        
        self.label.setPixmap(pix.scaled(self.grid_size, self.grid_size))
        
    def mousePressEvent(self, QMouseEvent):
        self.pushSign.emit(self.coord_x, self.coord_y)


class Chessboard(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.setLayout(self.grid_layout)
        self.myGrid = {}

    def reset(self, height, width):
        for i in range(self.grid_layout.count()):
            self.grid_layout.itemAt(i).widget().deleteLater()
        self.myGrid = {}
        
        self.height = height
        self.width = width
        grid_size = 50
        self.setFixedSize(grid_size*width, grid_size*height)
        
        for i in range(height):
            for j in range(width):
                gird = Grid(self, i, j, grid_size)
                gird.pushSign.connect(self.parent().client.step)
                self.grid_layout.addWidget(gird, *(i,j))
                self.myGrid[(i, j)] = gird
                
    def setState(self, state):
        for i in range(self.height):
            for j in range(self.width):
                self.myGrid[(i, j)].setState(state[i][j])

class Menu(QWidget):
    gameStartSign = pyqtSignal(str, int, int)
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()
	
    def initUI(self):
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)
        
        self.widthEdit = MyEdit('Width', '8')
        self.heightEdit = MyEdit('Height', '8')
        self.gameTypeBox = QComboBox(self)
        self.gameTypeBox.setView(QListView())
        self.gameTypeBox.addItem("GoBang")
        self.gameTypeBox.addItem("Go")
        self.gameTypeBox.addItem("Reversi")
        self.startButton = QPushButton('Start')
        self.startButton.clicked.connect(self.gameStart)
        
        vlayout.addWidget(self.widthEdit)
        vlayout.addWidget(self.heightEdit)
        vlayout.addWidget(self.gameTypeBox)
        vlayout.addWidget(self.startButton)
    
    def gameStart(self):
        gameType = self.gameTypeBox.currentText()
        height = int(self.heightEdit.edit.text())
        width = int(self.widthEdit.edit.text())
        self.gameStartSign.emit(gameType, height, width)
    
class GameClient(QThread):
    setGameInfoSign = pyqtSignal(str, int, int)
    setStateSign = pyqtSignal(object, int)
    messageSign = pyqtSignal(str)
    def __init__(self, player_id):
        self.player_id = player_id
        self.state = None
        self.turn = None
        self.proxy = ClientProxy(player_id)
        super(GameClient, self).__init__()
        
    def step(self, coord_x, coord_y):
        self.proxy.sendStep(coord_x, coord_y)
    
    def gameStart(self, gameType, height, width):
        data = {
            'gameType': gameType,
            'height': height,
            'width': width
        }
        self.proxy.sendGameInfo(data)
  
    def run(self):
        self.proxy.connect()
        while True:
            order = self.proxy.recv()
            if order['type'] == 'start':
                info = order['info']
                self.setGameInfoSign.emit(info['gameType'], info['height'], info['width'])
            elif order['type'] == 'state':
                self.setStateSign.emit(info['state'], info['turn'])
            elif order['type'] == 'message':
                self.messageSign.emit(info['message'])
        
        
class MainWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.client.setGameInfoSign.connect(self.setGameInfo)
        self.client.setStateSign.connect(self.setState)
        self.client.messageSign.connect(self.showMessage)
        self.initUI()
	
    def initUI(self):
        main_widget = QWidget(self)
        h_layout = QHBoxLayout()
        main_widget.setLayout(h_layout)
        self.board = Chessboard(self)
        self.board.reset(8, 8)
        self.menu = Menu(self)
        self.menu.gameStartSign.connect(self.client.gameStart)
        h_layout.addWidget(self.board)
        h_layout.addWidget(self.menu)
        
        self.setCentralWidget(main_widget)
        file = open('./client.qss', 'r')
        self.setStyleSheet(file.read())
    
    def setGameInfo(self, gameType, height, width):
        self.board.reset(height, width)
        
    def setState(self, state, turn):
        self.board.setState(state)
    
    def showMessage(self, message):
        print("****Show Message", message)
        pass
        
        
        
if __name__ == '__main__':
    app = QApplication([])
    
    client = GameClient(int(sys.argv[1]))
    w = MainWindow(client)
    w.show()
    client.start()
    sys.exit(app.exec_())