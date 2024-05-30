import chess
from chess.polyglot import zobrist_hash
from engine.evaluation import evaluate_board, evaluate_move, is_endgame
import numpy as np
from collections import deque, namedtuple
import time


TranspTableRes = namedtuple('TranspTableRes', ('value', 'flag', 'depth', 'best_move'))


class TranspTable(object):
    def __init__(self, max_size: int):
        self.entry = deque(maxlen=max_size)
        self.value = deque(maxlen=max_size)
        self.flag = deque(maxlen=max_size)
        self.depth = deque(maxlen=max_size)
        self.best_move = deque(maxlen=max_size)

    def store(self, board: chess.Board, value: float, flag: str, depth: int, best_move: chess.Move):
        z_hash = zobrist_hash(board)
        if z_hash not in self.entry:
            self.entry.append(z_hash)
            self.value.append(value)
            self.flag.append(flag)
            self.depth.append(depth)
            self.best_move.append(best_move)
        else:
            pos_index = self.entry.index(z_hash)
            if depth > self.depth[pos_index]:
                self.value[pos_index] = value
                self.flag[pos_index] = flag
                self.depth[pos_index] = depth
                self.best_move[pos_index] = best_move

    def lookup(self, board: chess.Board):
        z_hash = zobrist_hash(board)
        if z_hash in self.entry:
            pos_index = self.entry.index(z_hash)
            return TranspTableRes(self.value[pos_index], self.flag[pos_index], self.depth[pos_index], self.best_move[pos_index])
        return None


def search(board: chess.Board, max_player: bool, transp_table: TranspTable, q_search_depth: int, time_limit: float):
    start_time = time.time()
    depth = 1
    best_move = None
    while True:
        search_res = negamax(board.copy(stack=False), depth, max_player, root=True,
                             transp_table=transp_table, q_search_depth=q_search_depth,
                             start_time=start_time, time_limit=time_limit)
        if search_res is not None:
            best_move = chess.Move.from_uci(search_res.uci())
        else:
            break
        depth += 1
    value = evaluate_board(board)
    if not max_player:
        value *= -1
    return best_move, value, depth - 1


def negamax(board: chess.Board, depth, max_player: bool, root: bool,
            transp_table: TranspTable, q_search_depth: int,
            start_time: float, time_limit: float,
            alpha: float=-float('Inf'), beta: float=float('Inf')):
    alpha_orig = alpha

    transp_tab_res = transp_table.lookup(board)
    if (transp_tab_res is not None) and (transp_tab_res.depth >= depth):
        if transp_tab_res.flag == 'EXACT':
            return transp_tab_res.value if not root else transp_tab_res.best_move
        elif transp_tab_res.flag == 'LOWERBOUND':
            alpha = max(alpha, transp_tab_res.value)
        elif transp_tab_res.flag == 'UPPERBOUND':
            beta = min(beta, transp_tab_res.value)
        if alpha >= beta:
            return transp_tab_res.value if not root else transp_tab_res.best_move

    if depth == 0 or board.is_game_over():
        board_value = evaluate_board(board) if max_player else -evaluate_board(board)
        if not board.is_game_over():
            q_search_res = quiet_search(board.copy(stack=False), max_player, q_search_depth, alpha, beta, transp_table,
                                        start_time, time_limit)
            if q_search_res is not None:
                if max_player and (q_search_res < board_value):
                    return q_search_res
                elif not max_player and (q_search_res > board_value):
                    return q_search_res
        return board_value

    piece_map = board.piece_map()
    end_game = is_endgame(board)
    legal_moves = []
    moves_score = []
    not_sort_legal_moves = list(board.legal_moves)
    if len(not_sort_legal_moves) > 1:
        if transp_tab_res is not None:
            not_sort_legal_moves.remove(transp_tab_res.best_move)
        for move in not_sort_legal_moves:
            legal_moves.append(move)
            moves_score.append(evaluate_move(board, piece_map, end_game, move))
        legal_moves = np.array(legal_moves)[np.array(moves_score).argsort()]
        if max_player:
            legal_moves = legal_moves[::-1]
        if transp_tab_res is not None:
            legal_moves = np.insert(legal_moves, 0, transp_tab_res.best_move)
    else:
        legal_moves = not_sort_legal_moves

    value = -float('Inf')
    best_move = -1
    for i, move in enumerate(legal_moves):
        board.push(move)
        if time.time() - start_time > time_limit:
            return None
        move_value = negamax(board.copy(stack=False), depth - 1, not max_player, False,
                             transp_table, q_search_depth, start_time, time_limit,
                             -beta, -alpha)
        if move_value is None:
            return None
        move_value *= -1
        board.pop()
        if move_value > value:
            value = move_value
            best_move = i
        alpha = max(alpha, value)
        if alpha >= beta:
            break

    if value <= alpha_orig:
        flag = 'UPPERBOUND'
    elif value >= beta:
        flag = 'LOWERBOUND'
    else:
        flag = 'EXACT'
    transp_table.store(board, value, flag, depth, legal_moves[best_move])

    if not root:
        return value
    return legal_moves[best_move]


def quiet_search(board: chess.Board, max_player: bool, depth: int, alpha: float, beta: float, transp_table: TranspTable,
                 start_time: float, time_limit: float):
    value = evaluate_board(board) if max_player else -evaluate_board(board)
    if value >= beta:
        return beta
    alpha = max(alpha, value)

    if depth == 0 or board.is_game_over():
        return value

    piece_map = board.piece_map()
    end_game = is_endgame(board)
    danger_moves = []
    moves_score = []
    for move in board.legal_moves:
        if board.is_capture(move) or board.gives_check(move):
            danger_moves.append(move)
            moves_score.append(evaluate_move(board, piece_map, end_game, move))
    transp_tab_res = transp_table.lookup(board)
    if (transp_tab_res is not None) and (len(danger_moves) > 1) and (transp_tab_res.best_move in danger_moves):
        best_move_idx = danger_moves.index(transp_tab_res.best_move)
        danger_moves.remove(transp_tab_res.best_move)
        moves_score.remove(moves_score[best_move_idx])
        danger_moves = np.array(danger_moves)[np.array(moves_score).argsort()]
        if max_player:
            danger_moves = danger_moves[::-1]
        danger_moves = np.insert(danger_moves, 0, transp_tab_res.best_move)
    else:
        danger_moves = np.array(danger_moves)[np.array(moves_score).argsort()]
        if max_player:
            danger_moves = danger_moves[::-1]

    for move in danger_moves:
        board.push(move)
        if time.time() - start_time > time_limit:
            return None
        value = quiet_search(board.copy(stack=False), not max_player, depth - 1, -beta, -alpha, transp_table,
                             start_time, time_limit)
        if value is None:
            return None
        value *= -1
        board.pop()
        if value >= beta:
            return beta
        alpha = max(alpha, value)
    return alpha












































