"""
A*寻路算法实现
"""

import heapq
from typing import Dict, List, Optional, Set
from .data_structures import State, Location, Agent, Constraints, Cell


class AStar:
    """A*寻路算法类"""
    
    def __init__(self, env):
        """
        初始化A*算法
        :param env: 环境对象
        """
        self.env = env
    
    def search(self, agent_name: str) -> List[State]:
        """
        为单个智能体搜索路径
        :param agent_name: 智能体名称
        :return: 路径列表，失败返回False
        """
        initial_state = State(0, self.env.get_agent_start(agent_name))
        
        # 开放列表（优先队列）
        open_list = []
        # 关闭列表
        closed_set: Set[tuple] = set()
        
        # 记录父节点
        parents: Dict[tuple, tuple] = {}
        
        # g分数：从起点到当前点的代价
        g_score: Dict[tuple, int] = {}
        initial_key = (initial_state.time, initial_state.location.x, initial_state.location.y)
        g_score[initial_key] = 0
        
        # h分数：从当前点到终点的启发式估计
        h_score: Dict[tuple, int] = {}
        h_score[initial_key] = self.env.calc_h(initial_state, agent_name)
        
        # f分数：g + h
        f_score: Dict[tuple, int] = {}
        f_score[initial_key] = h_score[initial_key]
        
        # 将初始状态加入开放列表
        heapq.heappush(open_list, (f_score[initial_key], initial_key))
        
        # 最大迭代次数，防止无路可走时无限循环
        cnt = 0
        max_cnt = 10000
        
        while open_list:
            cnt += 1
            if cnt > max_cnt:
                print(f"Agent {agent_name} search timeout")
                break
            
            # 取出f值最小的节点
            _, current_key = heapq.heappop(open_list)
            
            # 解析当前状态
            current_time = current_key[0]
            current_loc = Location(current_key[1], current_key[2])
            current_state = State(current_time, current_loc)
            
            # 检查是否到达目标
            if self.env.is_reach_target(current_state, agent_name):
                return self.reconstruct_path(parents, current_key)
            
            # 加入关闭列表
            closed_set.add(current_key)
            
            # 获取邻居状态
            neighbors = self.env.get_neighbors(current_state)
            
            for neighbor in neighbors:
                neighbor_key = (neighbor.time, neighbor.location.x, neighbor.location.y)
                
                # 如果在关闭列表中，跳过
                if neighbor_key in closed_set:
                    continue
                
                # 计算新的g值
                tmp_g = g_score[current_key] + self.env.calc_g(current_state, neighbor)
                
                # 检查邻居是否在开放列表中
                in_open = any(n[1] == neighbor_key for n in open_list)
                
                if not in_open:
                    # 新节点
                    g_score[neighbor_key] = tmp_g
                    h_score[neighbor_key] = self.env.calc_h(neighbor, agent_name)
                    f_score[neighbor_key] = tmp_g + h_score[neighbor_key]
                    parents[neighbor_key] = current_key
                    heapq.heappush(open_list, (f_score[neighbor_key], neighbor_key))
                elif tmp_g < g_score[neighbor_key]:
                    # 更新已有节点
                    g_score[neighbor_key] = tmp_g
                    f_score[neighbor_key] = tmp_g + h_score[neighbor_key]
                    parents[neighbor_key] = current_key
        
        print(f"Agent {agent_name} search failed: no path found")
        return False
    
    def reconstruct_path(self, parents: Dict[tuple, tuple], current_key: tuple) -> List[State]:
        """
        重建路径
        :param parents: 父节点字典
        :param current_key: 当前节点
        :return: 路径列表
        """
        path = []
        while current_key in parents:
            state = State(current_key[0], Location(current_key[1], current_key[2]))
            path.append(state)
            current_key = parents[current_key]
        
        # 添加起点
        path.append(State(current_key[0], Location(current_key[1], current_key[2])))
        
        path.reverse()
        return path


class AStarV2:
    """改进版A*算法 - 优先选择h值小的邻居"""
    
    def __init__(self, env):
        self.env = env
    
    def search(self, agent_name: str) -> List[State]:
        """为单个智能体搜索路径"""
        initial_state = State(0, self.env.get_agent_start(agent_name))
        
        open_list = []
        closed_set: Set[tuple] = set()
        parents: Dict[tuple, tuple] = {}
        
        g_score: Dict[tuple, int] = {}
        h_score: Dict[tuple, int] = {}
        f_score: Dict[tuple, int] = {}
        
        initial_key = (initial_state.time, initial_state.location.x, initial_state.location.y)
        g_score[initial_key] = 0
        h_score[initial_key] = self.env.calc_h(initial_state, agent_name)
        f_score[initial_key] = h_score[initial_key]
        
        heapq.heappush(open_list, (f_score[initial_key], initial_key))
        
        cnt = 0
        max_cnt = 10000
        
        while open_list:
            cnt += 1
            if cnt > max_cnt:
                break
            
            _, current_key = heapq.heappop(open_list)
            
            current_time = current_key[0]
            current_loc = Location(current_key[1], current_key[2])
            current_state = State(current_time, current_loc)
            
            if self.env.is_reach_target(current_state, agent_name):
                return self.reconstruct_path(parents, current_key)
            
            closed_set.add(current_key)
            
            neighbors = self.env.get_neighbors(current_state)
            
            # 改进：按h值排序邻居
            neighbors_sorted = sorted(neighbors, 
                key=lambda s: self.env.calc_h(s, agent_name))
            
            for neighbor in neighbors_sorted:
                neighbor_key = (neighbor.time, neighbor.location.x, neighbor.location.y)
                
                if neighbor_key in closed_set:
                    continue
                
                tmp_g = g_score[current_key] + self.env.calc_g(current_state, neighbor)
                
                in_open = any(n[1] == neighbor_key for n in open_list)
                
                if not in_open:
                    g_score[neighbor_key] = tmp_g
                    h_score[neighbor_key] = self.env.calc_h(neighbor, agent_name)
                    f_score[neighbor_key] = tmp_g + h_score[neighbor_key]
                    parents[neighbor_key] = current_key
                    heapq.heappush(open_list, (f_score[neighbor_key], neighbor_key))
                elif tmp_g < g_score[neighbor_key]:
                    g_score[neighbor_key] = tmp_g
                    f_score[neighbor_key] = tmp_g + h_score[neighbor_key]
                    parents[neighbor_key] = current_key
        
        return False
    
    def reconstruct_path(self, parents: Dict[tuple, tuple], current_key: tuple) -> List[State]:
        """重建路径"""
        path = []
        while current_key in parents:
            state = State(current_key[0], Location(current_key[1], current_key[2]))
            path.append(state)
            current_key = parents[current_key]
        
        path.append(State(current_key[0], Location(current_key[1], current_key[2])))
        path.reverse()
        return path
