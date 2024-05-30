from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QCheckBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
import chess
from engine.playing import Engine
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from gui.chessboard import ChessBoard, get_piece_img


class SearchStats(QWidget):
    def __init__(self):
        super().__init__()
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=1.)
        self.figure, self.axs = plt.subplots(2, 1, sharex=True)
        self.canvas = FigureCanvas(self.figure)
        self.axs[0].title.set_text("Value")
        self.axs[1].title.set_text("Depth")
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.setFixedSize(QSize(400, 300))

    def reset(self):
        self.value_data = [[], []]
        self.depth_data = [[], []]
        self.axs[0].clear()
        self.axs[1].clear()
        self.axs[0].title.set_text("Value")
        self.axs[1].title.set_text("Depth")
        self.canvas.draw()

    def add_stats(self, move, value, depth=None):
        self.value_data[0].append(move)
        self.value_data[1].append(value)
        if depth is not None:
            self.depth_data[0].append(move)
            self.depth_data[1].append(depth)
        self.axs[0].clear()
        self.axs[1].clear()
        self.axs[0].plot(self.value_data[0], self.value_data[1])
        self.axs[1].plot(self.depth_data[0], self.depth_data[1])
        self.axs[0].title.set_text("Value")
        self.axs[1].title.set_text("Depth")
        self.canvas.draw()


class Controls(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.search_stats = SearchStats()
        self.start_fen_text = QLineEdit("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.white = QCheckBox() 
        self.time_limit = QLineEdit("1")
        self.q_search_depth = QLineEdit("3")
        self.transp_table_size = QLineEdit("1e5")
        self.form_layout = QFormLayout()
        self.form_layout.addRow(QLabel("FEN"), self.start_fen_text)
        self.form_layout.addRow(QLabel("Engine White"), self.white)
        self.form_layout.addRow(QLabel("Move Time Limit (sec.)"), self.time_limit)
        self.form_layout.addRow(QLabel("Quiesc. Search Depth"), self.q_search_depth)
        self.form_layout.addRow(QLabel("Transp. Table Size"), self.transp_table_size)
        self.start_btn = QPushButton("Start")
        self.start_btn.setFixedSize(QSize(100, 70))
        self.start_btn.clicked.connect(self.start_match)
        self.resign_btn = QPushButton("Resign")
        self.resign_btn.setFixedSize(QSize(100, 70))
        self.resign_btn.clicked.connect(self.resign)
        self.resign_btn.setEnabled(False)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.search_stats)
        layout.addLayout(self.form_layout)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.resign_btn)
        self.setLayout(layout)

    def start_match(self):
        black = False
        if self.white.isChecked():
            black = True
        try:
            self.app.board.reset(fen=self.start_fen_text.text(), mirror=black)
            time_limit = float(self.time_limit.text())
            q_search_depth = int(self.q_search_depth.text())
            transp_table_size = int(float(self.transp_table_size.text()))
            self.app.engine = Engine(time_limit, q_search_depth, transp_table_size)
        except:
            QMessageBox.critical(self, "Error", "Invalid settings!")
            return None
        self.start_btn.setEnabled(False)
        self.resign_btn.setEnabled(True)
        self.search_stats.reset()
        if self.app.engine is not None and self.app.board.mirror:
            move, value, depth = self.app.engine.play(self.app.board.board)
            if self.app.board.board.is_capture(move) or self.app.board.board.is_en_passant(move):
                if not self.app.board.board.is_en_passant(move):
                    cpt_piece = self.app.board.board.piece_at(move.to_square)
                else:
                    cpt_color = not self.app.board.board.turn
                    cpt_piece = chess.Piece(chess.PAWN, cpt_color)
                if cpt_piece.color:
                    self.app.captures_1.add_piece(cpt_piece)
                else:
                    self.app.captures_2.add_piece(cpt_piece)
            self.app.board.board.push(move)
            self.app.board.render()

    def resign(self):
        if self.app.board.mirror:
            winner = "White"
        else:
            winner = "Black"
        QMessageBox.about(self, "Winner", winner)
        self.app.engine = None
        self.start_btn.setEnabled(True)
        self.resign_btn.setEnabled(False)


class Captures(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(80*8, 80))
        self.h_layout = QHBoxLayout()
        self.h_layout.setAlignment(Qt.AlignLeft)
        self.h_layout.setSpacing(0)
        self.setLayout(self.h_layout)

    def reset(self, white):
        self.white = white
        self.pieces = {chess.PAWN: 0, chess.ROOK: 0, chess.KNIGHT: 0, chess.BISHOP: 0, chess.QUEEN: 0}
        self.render()
    
    def add_piece(self, piece):
        self.pieces[piece.piece_type] += 1
        self.render()

    def render(self):
        for i in reversed(range(self.h_layout.count())): 
            self.h_layout.itemAt(i).widget().setParent(None)
        for piece_type in self.pieces.keys():
            piece = chess.Piece(piece_type, not self.white)
            for _ in range(self.pieces[piece_type]):                   
                img = get_piece_img(piece)
                label = QLabel()
                pixmap = QPixmap(img)
                pixmap = pixmap.scaled(40, 40)
                label.setPixmap(pixmap)
                self.h_layout.addWidget(label)


class ChessApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chassy")

        self.captures_1 = Captures()
        self.captures_2 = Captures()
        self.board = ChessBoard(self)
        self.controls = Controls(self)

        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        self.v_layout.addWidget(self.captures_1)
        self.v_layout.addWidget(self.board)
        self.v_layout.addWidget(self.captures_2)
        self.h_layout.addLayout(self.v_layout)
        self.h_layout.addWidget(self.controls)
        self.setLayout(self.h_layout)

        self.engine = None
