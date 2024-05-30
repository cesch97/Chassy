from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QLabel, QMessageBox, QWidget, QGridLayout
from PyQt5.QtGui import QPixmap
import chess


def get_piece_img(piece):
    if piece is not None:
        color = "w" if piece.color else "b"
        symbol = piece.symbol().upper()
        return f"imgs/{color}{symbol}.png"
    return "imgs/empty.png"


class Square(QLabel):
    def __init__(self, board, sq_id, bg_color, piece):
        super().__init__()
        self.board = board
        self.sq_id = sq_id
        self.bg_color = bg_color
        self.setStyleSheet(f"background-color : {bg_color};")
        self.highlighted = False
        self.set_piece(piece)
        self.move = None
    
    def set_piece(self, piece):
        img = get_piece_img(piece)
        self.pixmap = QPixmap(img)
        self.setPixmap(self.pixmap)

    def mousePressEvent(self, event):
        if self.move is None:
            self.board.show_legal_moves(self.sq_id)
        else:
            if self.board.board.is_capture(self.move) or self.board.board.is_en_passant(self.move):
                if not self.board.board.is_en_passant(self.move):
                    cpt_piece = self.board.board.piece_at(self.move.to_square)
                else:
                    cpt_color = not self.board.board.turn
                    cpt_piece = chess.Piece(chess.PAWN, cpt_color)
                if cpt_piece.color:
                    self.board.app.captures_1.add_piece(cpt_piece)
                else:
                    self.board.app.captures_2.add_piece(cpt_piece)

            rank_from = chess.square_rank(self.move.from_square)
            if rank_from == 6 or rank_from == 1:
                piece = self.board.board.piece_at(self.move.from_square)
                rank_to = chess.square_rank(self.move.to_square)
                if piece.piece_type == chess.PAWN:
                    if (rank_from == 6 and rank_to == 7) or (rank_from == 1 and rank_to == 0):
                        self.move.promotion = chess.QUEEN

            self.board.board.push(self.move)
            self.board.render()
            self.board.repaint()
            if self.board.board.is_game_over():
                winner = "Draw"
                if self.board.board.outcome():
                    if self.board.board.outcome().winner is not None:
                        if not self.board.mirror:
                            winner = 'White'
                        else:
                            winner = 'Black'
                msg = QMessageBox(0, "Winner", winner, QMessageBox.Ok)
                msg.exec()
                self.board.app.controls.start_btn.setEnabled(True)
                self.board.app.controls.resign_btn.setEnabled(False)
                return None
            if self.board.app.engine is not None:
                move, value, depth = self.board.app.engine.play(self.board.board)
                if move is not None:
                    if self.board.board.is_capture(move) or self.board.board.is_en_passant(move):
                        if not self.board.board.is_en_passant(move):
                            cpt_piece = self.board.board.piece_at(move.to_square)
                        else:
                            cpt_color = not self.board.board.turn
                            cpt_piece = chess.Piece(chess.PAWN, cpt_color)
                        if cpt_piece.color:
                            self.board.app.captures_1.add_piece(cpt_piece)
                        else:
                            self.board.app.captures_2.add_piece(cpt_piece)
                    self.board.board.push(move)
                    self.board.render()
                    num_moves = len(self.board.board.move_stack)
                    self.board.app.controls.search_stats.add_stats(num_moves, value, depth)
                if self.board.board.is_game_over():
                    winner = "Draw"
                    if self.board.board.outcome():
                        if self.board.board.outcome().winner is not None:
                            if not self.board.mirror:
                                winner = 'Black'
                            else:
                                winner = 'White'
                    msg = QMessageBox(0, "Winner", winner, QMessageBox.Ok)
                    msg.exec()
                    self.board.app.controls.start_btn.setEnabled(True)
                    self.board.app.controls.resign_btn.setEnabled(False)
                
    def highlight_1(self, move=None):
        self.setStyleSheet(f"background-color : {self.bg_color}; background-image: url('imgs/selection.png')")
        self.highlighted = True
        self.move = move
    
    def highlight_2(self, move=None):
        self.setStyleSheet("background-color : rgba(245, 230, 75, 0.8)")
        self.highlighted = True
        self.move = move
    
    def downlight(self):
        self.setStyleSheet(f"background-color : {self.bg_color};")
        self.highlighted = False
        self.move = None


class ChessBoard(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.setLayout(self.grid_layout)
        self.setFixedSize(QSize(80*8, 80*8))
        self.reset(mirror=False)

    def reset(self, fen=None, mirror=None):
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        self.squares = []
        if mirror is not None:
            self.mirror = mirror
        self.app.captures_1.reset(not self.mirror)
        self.app.captures_2.reset(self.mirror)
        self.board = chess.Board()
        if fen is not None:
            self.board.set_fen(fen)
        # if self.mirror:
        #     self.board = self.board.mirror()
        piece_map = self.board.piece_map()
        for i in range(64):
            row = abs(8 - i // 8)
            col =  i - i // 8 * 8
            bg_color = "white" if ((row % 2 == 0) and (col % 2 != 0)) or ((row % 2 != 0) and (col % 2 == 0)) else "rgba(102, 204, 0, 90)"
            # if self.mirror:
            #     bg_color = "rgba(102, 204, 0, 90)" if ((row % 2 == 0) and (col % 2 != 0)) or ((row % 2 != 0) and (col % 2 == 0)) else "white"
            # else:
            #     bg_color = "white" if ((row % 2 == 0) and (col % 2 != 0)) or ((row % 2 != 0) and (col % 2 == 0)) else "rgba(102, 204, 0, 90)"
            if i in piece_map.keys():
                piece = piece_map[i]
                # if self.mirror:
                #     piece.color = not piece.color
            else:
                piece = None
            square = Square(self, i, bg_color, piece)
            self.squares.append(square)
            self.grid_layout.addWidget(square, row, col)

    def render(self):
        piece_map = self.board.piece_map()
        for i in range(64):
            if i in piece_map.keys():
                piece = piece_map[i]
                # if self.mirror:
                #     piece.color = not piece.color
            else:
                piece = None
            square = self.squares[i]
            if square.highlighted:
                square.downlight()
            square.set_piece(piece)
        if len(self.board.move_stack) > 0:
            last_move = self.board.move_stack[-1]
            sq_from = last_move.from_square
            from_sq_id = chess.SQUARES.index(sq_from)
            to_sq = last_move.to_square
            to_sq_id = chess.SQUARES.index(to_sq)
            self.squares[from_sq_id].highlight_2()
            self.squares[to_sq_id].highlight_2()
    
    def show_legal_moves(self, sq_id):
        self.render()
        moves_from_sq = {}
        for move in self.board.legal_moves:
            sq_from = move.from_square
            from_sq_id = chess.SQUARES.index(sq_from)
            to_sq = move.to_square
            to_sq_id = chess.SQUARES.index(to_sq)
            if from_sq_id in moves_from_sq.keys():
                moves_from_sq[from_sq_id].append(to_sq_id)
            else:
                moves_from_sq[from_sq_id] = [to_sq_id]
        if sq_id in moves_from_sq.keys():
            self.squares[sq_id].highlight_2()
            for sq in moves_from_sq[sq_id]:
                self.squares[sq].highlight_1(move=chess.Move.from_uci(f"{chess.SQUARE_NAMES[sq_id]}{chess.SQUARE_NAMES[sq]}"))


