"""通过MCTS算法,实现AI对于一个局面的应对方法"""
import numpy as np
import random
from Game import *

# AI每一轮要进行蒙特卡洛树搜索次数
SAMPLE_TIMES = 3000


class Node():
    """
    一棵树上的结点需要有以下的内容：
    - 结点对应的状态实例
    - 结点的父节点parent_node
    - 结点的子节点child集合
        - 结点的子节点还需要挂载：结点到子节点的状态转移是用了什么action
    - 结点的总value
    - 结点的visit次数
    """
    def __init__(self, state=None, parent=None) -> None:
        self.state = copy.deepcopy(state)
        self.parent = parent
        self.untried_actions = self.state.get_possible_actions()    # 状态下可行的列表
        self.childs = {}    # dict:{action: Node}
        self.all_value = 0.0    # 结点的总value值
        self.visit = 0  # 结点总visit次数
    
    def get_state(self):
        return self.state
    
    def get_ave_value(self):
        try:
            return self.all_value/self.visit
        except Exception:
            print("不能获取该结点的平均价值！")
            return None
    
    def update_value(self, reward: int):
        self.all_value += reward
    
    def update_visit(self):
        self.visit += 1
    
    def update(self, reward: int):
        self.update_value(reward)
        self.update_visit()

    def isTerminal(self):
        return self.state.judge_result()[0]

    def isAllExpanded(self):
        return len(self.untried_actions) == 0

    def update_untried_actions(self, action):
        self.untried_actions.remove(action)


class MCTS():
    """
    一棵Monte Carlo Search树,需要定义遍历过程中的描述
    - 这棵树的根节点 root_node
    - 这棵树的当前节点 cur_node
    """
    def __init__(self) -> None:
        self.cur_node = None
        self.root_node = None
    
    def choose_action(self, game_cur_state):
        # 选择动作之前，需要更新AI当前节点到目前的棋局状态
        # 如果是不存在MCTS树的话，需要实例化第一个root结点，并将该root结点作为当前节点
        if self.root_node == None:
            self.root_node = Node(game_cur_state)
            self.cur_node = self.root_node
        # 如果已经存在了MCTS树，说明AI自己已经至少作出了一次action
        # 此时的node是对方选择的局面，再结合当前的棋局状态game_cur_state，要判断出是否在
        else:
            for child_node in self.cur_node.childs.values():
                if game_cur_state == child_node.state:
                    # 如果从对方局面的若干子节点对应状态集合中找到了当前的状态
                    # 当前状态对应的这个子节点就是AI面临的局面/状态
                    self.cur_node = child_node
                    break
            else:
                # 因为我们设置的采样次数足够多，如果不是重启游戏的情况下，
                # 不应该出现找不到子节点与当前状态对应
                # 唯一的可能性就是又回到了最初的起点，所以当前节点又成为了根节点
                self.cur_node = self.root_node

        # 先是要以当前节点为根节点进行采样估计，通过MC方法模拟该结点下及其各个子节点的价值函数
        self.Sample_Estimate(sample_times=SAMPLE_TIMES)
        # 仅根据exploit原则选取结点，得到对应的动作
        next_node, action = self.UCB_selection(self.cur_node, C=0)
        self.cur_node = next_node   # 当AI选择了action之后，结点应该往下探一层，所以next_node就是选择后对方面临的当前状态
        return action   # 返回AI作出的action

    def Sample_Estimate(self, sample_times=2000):
        for t in range(sample_times):
            # 采样episode的数量为training_times
            # 目的：蒙特卡洛大数定律方法估计当前节点的价值
            
            # 第一步：UCT方法搜索，得到需要扩展的点
            expand_node = self.UCT_search()
            # 第二步：通过对需要expand的节点进行模拟/随机游走，得到叶子结点、winner
            winner = self.Simulation(expand_node)
            # 第三步：通过叶子结点的值，反向传播
            self.BackPropagation(expand_node, winner)

    def UCT_search(self):
        # 每次搜索的时候，从当前节点开始搜索，直到搜索到一个可以expand的叶节点
        node = self.cur_node
        # 如果已经搜索到叶子结点，直接返回
        while not node.isTerminal():
            # 1.如果全部扩展，根据置信区间上限公式选择最优结点
            if node.isAllExpanded():
                node, _ = self.UCB_selection(node) # UCB exploit+explore
            # 2.如果没有全部扩展，进行expand操作
            else:
                node = self.expand(node)
                return node
        # 返回叶子结点
        leaf_node = node
        return leaf_node

    def expand(self, node):
        """
        给定一个node,根据该node下的未被选择的actions随机选取一个action,
        然后对该action获得新的状态,并构建一个node与新的状态挂载
        """
        action = random.choice(node.untried_actions)    # 随机选择一个未被执行的动作
        node.update_untried_actions(action) # 删除掉该动作
        new_state = node.state.get_new_state(action)
        new_node = Node(new_state, node)    # 创建一个新的结点
        node.childs[action] = new_node  # 给当前节点添加新的节点作为子节点
        return new_node

    def Simulation(self, start_node):
        """
        从某个结点开始随机游走作为模拟。
        """
        cur_state = start_node.state
        while True:
            done, winner = cur_state.judge_result()
            if done:
                # 如果已经到达结束位置
                break
            action = self.random_select_action(cur_state)
            cur_state = cur_state.get_new_state(action)
        return winner

    def BackPropagation(self, cur_node, winner):
        """
        反向传播
        - 通过叶子结点反向传播,直到根节点
        返回
        """
        # 1.更新visit
        cur_node.visit += 1
        # 2.更新values
        if winner:
            cur_node.all_value += 1 if winner == cur_node.state.player else -1
        else:
            pass

        if cur_node.parent != None:
            return self.BackPropagation(cur_node.parent, winner)


    def UCB_selection(self, node, C=np.sqrt(2)):
        """
        根据置信区间上限函数,对给定node的所有已扩展的子节点进行扫描判断哪个结点最优
        
        返回：
        - 最佳的结点
        - 最佳的动作
        """
        max_ucb = -10000
        best_node = None
        best_action = None
        child2action = {node.childs[key]:key for key in node.childs.keys()}
        for child in node.childs.values():
            exploit = - child.get_ave_value()
            explore =  C * np.sqrt(2 * np.log(node.visit) / child.visit)
            ucb = exploit + explore
            if ucb > max_ucb:
                max_ucb = ucb
                best_node = child
                best_action = child2action[child]
        return best_node, best_action

    def random_select_action(self, cur_state):
        """给定当前的state,随机选择一个可行的action"""
        return random.choice(cur_state.get_possible_actions())