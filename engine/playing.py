import chess
import chess.engine
from engine.search import search, TranspTable
from IPython.display import display, HTML, clear_output
from collections import namedtuple
import time


class Engine():
    def __init__(self, time_limit, q_search_depth, transp_table_size):
        super().__init__()
        self.time_limit = time_limit
        self.q_search_depth = q_search_depth
        self.transp_table = TranspTable(transp_table_size)
    
    def play(self, board):
        move, value, depth = search(board, board.turn, self.transp_table, self.q_search_depth, self.time_limit)
        return move, value, depth


Sf_conf = namedtuple('sf_config', ['sf', 'sf_elo', 'sf_tl', 'sf_skill', 'sf_num_cpus'])


def configure_sf(sf_loc: str, sf_elo=None, sf_tl: float = 0.75, sf_skill: int = 20, sf_num_cpus: int = 1):
    sf = chess.engine.SimpleEngine.popen_uci(sf_loc)
    if sf_elo is None:
        sf.configure({'Threads': sf_num_cpus, 'Skill Level': sf_skill})
    else:
        sf.configure({'Threads': 4, 'UCI_LimitStrength': True, 'UCI_Elo': sf_elo})
    return Sf_conf(sf, sf_elo, sf_tl, sf_skill, sf_num_cpus)


def display_board(board: chess.Board, winner=None):
    turn = 'White' if board.turn else 'Black'
    html = f"<div><b>Move: {len(board.move_stack)}, Turn: {turn}"
    if winner is not None:
        html += f", Winner: {winner}"
    html += "</b></div>"
    html += f'<div>{board._repr_svg_()}</div>'
    clear_output(wait=True)
    display(HTML(html))
    time.sleep(0.1)


def play_engine_vs_engine(engine_1_white: bool, search_args_1: dict, search_args_2: dict, time_limit: float,
                          visual: bool=False):
    board = chess.Board()
    transp_table_1 = TranspTable(search_args_1['transp_tab_size'])
    transp_table_2 = TranspTable(search_args_1['transp_tab_size'])
    if visual:
        display_board(board)
    while not board.is_game_over():
        if (engine_1_white and board.turn) or ((not engine_1_white) and (not board.turn)):
            move, value, depth = search(board, engine_1_white, transp_table_1,
                                 search_args_1['q_search_depth'], time_limit)
        else:
            move, value, depth = search(board, not engine_1_white, transp_table_2,
                                 search_args_2['q_search_depth'], time_limit)
        board.push(move)
        if visual:
            display_board(board)
            print(f'Depth: {depth}')
    if visual:
        winner = 'Draw'
        if board.outcome():
            winner = board.outcome().winner
            if winner is not None:
                if winner:
                    winner = 'White'
                else:
                    winner = 'Black'
            else:
                winner = 'Draw'
        display_board(board, winner=winner)


def play_sf_vs_engine(engine_white: bool, engine_args: dict, sf_args: dict, visual: bool=False):
    sf = configure_sf(**sf_args)
    board = chess.Board()
    transp_table = TranspTable(engine_args['transp_tab_size'])
    if visual:
        display_board(board)
    while not board.is_game_over():
        if ((not engine_white) and board.turn) or (engine_white and (not board.turn)):
            if sf.sf_elo is not None:
                if len(board.move_stack) <= 40:
                    sf_tl = 60 / 40 / 2
                else:
                    sf_tl = 0.6
            else:
                sf_tl = sf.sf_tl
            move = sf.sf.play(board, limit=chess.engine.Limit(time=sf_tl)).move
        else:
            move, value, depth = search(board, engine_white, transp_table,
                                 engine_args['q_search_depth'], engine_args['time_limit'])
        board.push(move)
        display_board(board)
    if visual:
        winner = 'Draw'
        if board.outcome():
            winner = board.outcome().winner
            if winner is not None:
                if winner:
                    winner = 'White'
                else:
                    winner = 'Black'
        display_board(board, winner=winner)


def play_human_vs_engine(human_white: bool, engine_args: dict):
    board = chess.Board()
    transp_table = TranspTable(engine_args['transp_tab_size'])
    display_board(board)
    _quit = False
    while not board.is_game_over():
        if (human_white and board.turn) or ((not human_white) and (not board.turn)):
            while True:
                move = input('Move: ')
                if move == 'legal moves':
                    print([board.san(leg_move) for leg_move in board.legal_moves])
                    continue
                elif move == 'quit':
                    _quit = True
                    break
                try:
                    move = board.parse_san(move)
                    break
                except:
                    print('Invalid move!')
        else:
            move, value, depth = search(board, not human_white, transp_table,
                                 engine_args['q_search_depth'], engine_args['time_limit'])
        if _quit:
            break
        board.push(move)
        display_board(board)
    winner = 'Draw'
    if board.outcome():
        winner = board.outcome().winner
        if winner is not None:
            if winner:
                winner = 'White'
            else:
                winner = 'Black'
    elif _quit:
        if human_white:
            winner = 'Black'
        else:
            winner = 'White'
    display_board(board, winner=winner)


if __name__ == '__main__':

    play_engine_vs_engine(False, 3, 3, int(1e6), False)
