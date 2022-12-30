"""用于环境可视化等工具性函数的实现"""
import numpy as np

def render_game_ui(game):
    size = game.board_size
    board = game.state.board 
    round = game.round
    render_rule = game.render_rule

    print()
    # 标题
    print('Round {}'.format(round).center(3*size, '-'))
    # 标注列号
    print('  ', end='')
    for y_ in range(len(board[0])):
        print('{0:^3}'.format(y_), end='')
    print()
    for x in range(len(board)):
        # 标注行号
        print('{0:<2}'.format(x), end='')
        for y in range(len(board[0])):
            print(render_rule[board[x, y]], end='')
        print() # 换行
