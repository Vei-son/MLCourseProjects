"""通过运行该文件,可以开始人类与AI之间的游戏对决"""
# 如果要玩五子棋，需要在Game.py中修改isBackgammon = True；
# 如果要玩井字棋，需要修改为False

from Game import *
from AI_MCTS import *
from Human import *

if __name__ == '__main__':
    while True:
        while True:
            ans = input("马上游戏开始了，请问您要选择人机对抗(1)还是双机对抗(2)呢？（请输入1或2）")
            try:
                ans = int(ans)
                break
            except Exception:
                print("格式错误，请重新输入！")
        if ans == 1 or ans == 2:
            two_AI_players = True if ans == 2 else False
            break
        else:
            print("输入的数字有误，请重新输入！")
    
    game = Game()
    player1 = MCTS()    # fixed AI
    player2 = MCTS() if two_AI_players else Human()
    players = [player1, player2]
    if two_AI_players:
        name = {player1: 'AI player 1', player2: "AI player 2"}
    else:
        name = {player1: 'AI player', player2: "Human player"}

    player_no = 0
    while True:
        # 获取当前状态
        cur_state = game.state
        # 根据状态获取下棋位置
        player = players[player_no]
        action = player.choose_action(cur_state)
        # 根据当前状态和动作，更新game的状态，并获取当前的界面
        game.update_game_state(action)
        
        
        print('刚刚{}在{}下了一颗棋'.format(name[player], action))

        done, winner = game.state.judge_result()
        if done:
            if not winner:
                print()
                print("{}和{}打成了平局！".format(name[player1], name[player2]))
            elif winner-1 == 0:
                print("{}赢了这局！".format(name[player1]))
            else:
                print("{}赢了这局！".format(name[player2]))
            break

        # 交换下棋玩家
        player_no = 1 - player_no