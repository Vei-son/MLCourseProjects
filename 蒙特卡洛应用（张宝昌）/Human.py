"""用于实现人类玩家的交互玩法"""
"""包含Human类"""
import re

class Human():
    """
    人类作为玩家,需要有以下的行动方式
    - choose_action
    """
    def __init__(self) -> None:
        pass

    def choose_action(self, game_cur_state):
        """给定当前的状态 需要人类玩家通过交互方式选择游戏"""
        while True:
            while True:
                human_input = input('请输入如格式"第1行第2列"以给出你的落子位置：')
                try:
                    x_y = re.findall(r'\d+', human_input)
                    x, y = x_y
                    x, y = int(x), int(y)
                    # 成功找到可能正确的行列号
                    break
                except Exception:
                    print('输入格式错误，请重新输入！')

            # 判断是否输入的行列号超过了游戏board的范围
            if (x >= len(game_cur_state.board) or x < 0
                or y >= len(game_cur_state.board[0]) or y < 0):
                # 如果超出
                print("您所输入的落子位置超出了棋盘，请重试！")
            elif (game_cur_state.board[x, y] != 0):
                print("抱歉！这个位置已经有棋子了，请选择其他位置！")
            else:
                break
        return (x, y)