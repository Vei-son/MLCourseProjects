"""包括游戏的棋局定义、游戏状态转换等"""
"""定义State类和Game类"""
import numpy as np 
import copy
from utils import render_game_ui

BOARD_SIZE = 3  # 棋盘大小
PLAYER_NUM = 2  # 玩家人数
RENDER_RULE = {0:' . ', 1:' o ', 2:' x '} # 画图的规则
FIXED_AI_PLAYER = 1 # 固定的AI玩家
HUMAN_OR_NEW_AI_PLAYER = 2  # 第二个玩家可以是人类也可以是AI
isBackgammon = False    # True：五子棋， False：井字棋

class State():
    """
    State作用为状态的描述
    - self.board,描述现在棋盘的样子
    - self.player,描述当前这个状态是哪个player下完的
    - 通过自己的状态,传入该状态下选择某个动作/位置,判断下一个状态是否结束
    根据是否结束,给定成功次数1作为reward进行反向传播
    - 更新当前状态实例并return
    """
    def __init__(self, board, player) -> None:
        self.board = board  # board是二维数组
        self.player = player    # player是当前状态下落棋子的行动者，可以对board进行落子，并进入下一个state

    def __eq__(self, __o: object) -> bool:
        return (np.all(self.board == __o.board) and self.player == __o.player)

    def get_possible_actions(self):
        board = self.board
        where = np.where(board==0)
        X, Y = where[0], where[1]
        possible_actions = []
        for x, y in zip(X, Y):
            possible_actions.append((x,y))
        return possible_actions
        
    def get_new_state(self, put_place=None):
        """
        returns:
        - 新的状态
        """
        if not put_place:
            return False 
        else:
            # 此处的action即为tuple(x,y)，其中x,y均为int类型如(0,5)
            # 因为下面对new_board进行了元素修改，且new_board是copy来的，会对self.board造成影响
            # 因此必须深拷贝
            new_board = copy.deepcopy(self.board)
            x, y = put_place
            new_board[x, y] = self.player    # 由于player本身的值就是棋盘上落子的棋子
            new_player = 1 if self.player == 2 else 2
            new_state = State(new_board, new_player)    # 创建新的游戏状态
            return new_state

    def judge_result(self, full_num=BOARD_SIZE, player_num=PLAYER_NUM, isBackgammon=isBackgammon,
        bg_full_num=5):
        """根据棋盘判断是否当前状态就是终止状态，如果有赢家，则返回赢家编号"""
        def isDraw(board):
            return np.all(board != 0)

        if not isBackgammon:
            # 井字棋游戏下的判断:
            for player in range(1, player_num+1):
                flag = player
                # 1.如果当前状态的board中横向满足满棋full_num
                for row in range(len(self.board)):
                    if np.all(self.board[row] == flag):
                        return True, player
                # 2.如果当前状态的board中纵向满足满棋full_num
                for col in range(len(self.board[0])):
                    if np.all(self.board[:, col] == flag):
                        return True, player
                # 3.如果当前状态的board中左上右下或左下右上满足full_num
                if (np.all(np.diag(self.board) == flag)
                 or np.all(np.diag(np.fliplr(self.board)) == flag)):
                    return True, player
                # 4.下完所有的格子，但没有输赢
                if isDraw(self.board):
                    return True, None
            return False, None
        else:
            # 五子棋游戏下的判断：
            for player in range(1, player_num+1):
                flag = player   # 1:1， 2:2
                def row_detect(board, flag, x, y):
                    if y+bg_full_num<=len(board[0]):
                        if np.all(board[x,y:y+bg_full_num]==flag):
                            return True
                    if y-bg_full_num+1>=0:
                        if np.all(board[x,y-bg_full_num+1:y+1]==flag):
                            return True
                    return False
                def col_detect(board, flag, x, y):
                    if x+bg_full_num<=len(board):
                        if np.all(board[x:x+bg_full_num, y]==flag):
                            return True
                    if x-bg_full_num+1>=0:
                        if np.all(board[x-bg_full_num+1:x+1, y]==flag):
                            return True
                    return False
                def diag_detect(board, flag, x, y):
                    if x+bg_full_num<=len(board) and y+bg_full_num<=len(board[0]):
                        if np.all(np.diag(board[x:,y:])[:bg_full_num]==flag):
                            return True
                    if x-bg_full_num+1>=0 and y-bg_full_num+1>=0:
                        if np.all(np.diag(np.fliplr(board[x-bg_full_num+1:x+1, y-bg_full_num+1:y+1]))==flag):
                            return True
                    return False
                for x in range(len(self.board)):
                    for y in range(len(self.board[0])):
                        if (row_detect(self.board, flag, x, y) 
                         or col_detect(self.board, flag, x, y) 
                         or diag_detect(self.board, flag, x, y)):
                            return True, player
                # 若非以上情况，且根据棋局判断已经平局了
                if isDraw(self.board):
                    return True, None
            return False, None

class Game():
    """
    Game的实例是一个游戏进程,需要有
    - 棋盘的大小 self.board_size
    - 游戏棋盘 self.board np方阵,包含0,1,2三种类型 (0:' ', 1:'O', 2:'X')  本身是0,1,2矩阵,渲染时使用' ','O','X'表示
    - 游戏当前的玩家 self.player
    - 游戏当前的状态 self.state

    Game在进行过程中需要进行游戏状态转换
    - method1: step()
    """
    def __init__(self, init_state=None) -> None:
        self.board_size = BOARD_SIZE
        self.board = np.zeros((self.board_size, self.board_size), dtype=np.int32)
        self.render_rule = RENDER_RULE

        if init_state == None:
            init_player = FIXED_AI_PLAYER
            self.state = State(self.board, init_player)
        else:
            self.state = init_state
        self.round = 0

    def update_game_state(self, action_crd):
        """给定一个action:(x,y),获取新的游戏状态,更新自己游戏状态,并返回该状态"""
        if action_crd:
            self.state = self.state.get_new_state(action_crd)
            self.round += 1
            self.get_ui()
    
    def get_ui(self):
        """使用utils中的函数进行展示"""
        render_game_ui(self)