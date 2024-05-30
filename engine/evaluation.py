import chess


piece_values = {
    chess.PAWN: 100,
    chess.ROOK: 500,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.QUEEN: 900,
    chess.KING: 20000
}

pawnEvalWhite = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, -20, -20, 10, 10,  5,
    5, -5, -10,  0,  0, -10, -5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0
]
pawnEvalBlack = list(reversed(pawnEvalWhite))

knightEval = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

bishopEvalWhite = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]
bishopEvalBlack = list(reversed(bishopEvalWhite))

rookEvalWhite = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]
rookEvalBlack = list(reversed(rookEvalWhite))

queenEval = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

kingEvalWhite = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]
kingEvalBlack = list(reversed(kingEvalWhite))

kingEvalEndGameWhite = [
    50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30,  0,  0,  0,  0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10,  0,  0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50
]
kingEvalEndGameBlack = list(reversed(kingEvalEndGameWhite))


white_queen = chess.Piece.from_symbol('Q')
black_queen = chess.Piece.from_symbol('q')
white_knight = chess.Piece.from_symbol('N')
black_knight = chess.Piece.from_symbol('n')
white_bishop = chess.Piece.from_symbol('B')
black_bishop = chess.Piece.from_symbol('b')


def is_endgame(board: chess.Board):
    piece_map = board.piece_map()
    pieces = piece_map.values()
    end_game = False
    if (not white_queen in pieces) and (not black_queen in pieces):
        end_game = True
    else:
        white_minors = 0
        if white_knight in pieces:
            white_minors += 1
        if white_bishop in pieces:
            white_minors += 1
        black_minors = 0
        if black_knight in pieces:
            black_minors += 1
        if black_bishop in pieces:
            black_minors += 1
        if ((white_queen in pieces) and (white_minors < 2)) or ((black_queen in pieces) and (black_minors < 2)):
            end_game = True
    return end_game


def evaluate_piece_square(piece: chess.Piece, square: chess.Square, end_game: bool):
    piece_type = piece.piece_type
    if piece.color == chess.WHITE:
        if not piece_type == chess.KING:
            if piece_type == chess.PAWN:
                return pawnEvalWhite[square]
            elif piece_type == chess.KNIGHT:
                return knightEval[square]
            elif piece_type == chess.BISHOP:
                return bishopEvalWhite[square]
            else:
                return rookEvalWhite[square]
        else:
            if not end_game:
                return kingEvalWhite[square]
            else:
                return kingEvalEndGameWhite[square]
    else:
        if not piece_type == chess.KING:
            if piece_type == chess.PAWN:
                return -pawnEvalBlack[square]
            elif piece_type == chess.KNIGHT:
                return -knightEval[square]
            elif piece_type == chess.BISHOP:
                return -bishopEvalBlack[square]
            else:
                return -rookEvalBlack[square]
        else:
            if not end_game:
                return -kingEvalBlack[square]
            else:
                return -kingEvalEndGameBlack[square]


def evaluate_board(board: chess.Board):
    if not board.is_game_over():
        material_value = 0
        piece_square_value = 0
        piece_map = board.piece_map()
        # checking end-game
        end_game = is_endgame(board)
        # calculating board_value
        for square in piece_map.keys():
            piece = piece_map[square]
            piece_type = piece.piece_type
            if piece.color == chess.WHITE:
                material_value += piece_values[piece_type]
            else:
                material_value -= piece_values[piece_type]
            piece_square_value += evaluate_piece_square(piece, square, end_game)
        board_value = material_value + piece_square_value
        return board_value
    else:
        winner = board.outcome().winner
        if winner is not None:
            if winner:
                return float('Inf')
            return -float('Inf')
        return 0


def evaluate_move(board: chess.Board, piece_map: dict, end_game: bool, move: chess.Move):
    from_quare = move.from_square
    to_square = move.to_square
    piece = piece_map[from_quare]
    if move.promotion is not None:
        if piece.color == chess.WHITE:
            return piece_values[move.promotion]
        return -piece_values[move.promotion]
    else:
        from_piece_square = evaluate_piece_square(piece, from_quare, end_game)
        to_piece_square = evaluate_piece_square(piece, to_square, end_game)
        move_value = to_piece_square - from_piece_square
        if board.is_capture(move):
            if board.is_en_passant(move):
                return piece_values[chess.PAWN] + move_value
            _to = board.piece_at(move.to_square)
            _from = board.piece_at(move.from_square)
            move_value += (piece_values[_to.piece_type] - piece_values[_from.piece_type])
        return move_value


