'''
CBS（Conflict-Based Search）冲突解决算法实现
'''

import copy
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from .data_structures import State, Location, Agent, Constraints, VertexConstraint, EdgeConstraint, Conflict
from .astar import AStar


@dataclass
class CTNode:
    """CBS算法中的约束树节点"""
    constraint_dict: Dict[str, Constraints] = field(default_factory=dict)
    solution: Dict[str, List[State]] = field(default_factory=dict)
    cost: int = 0
    nc: int = 0
    parent: Optional['CTNode'] = None


class CBS:
    """CBS（基于冲突的搜索）算法类"""
    
    def __init__(self, env, use_v2=False, use_priority: bool = True):
        """
        初始化CBS算法
        :param env: 环境对象
        :param use_v2: 是否使用改进版本
        :param use_priority: 是否使用优先级冲突解决
        """
        self.env = env
        self.use_v2 = use_v2
        self.use_priority = use_priority
        self.open_set: List[CTNode] = []
        self.closed_set: List[CTNode] = []
        self.max_iterations = 50000
    
    def search(self) -> Dict[str, List[Dict]]:
        """
        执行CBS算法搜索
        :return: 解决方案字典 {agent_name: [{'t': t, 'x': x, 'y': y}, ...]}
        """
        start_node = CTNode()
        
        for agent_name in self.env.agent_dict.keys():
            start_node.constraint_dict[agent_name] = Constraints()
        
        start_node.solution = self.env.calc_solution(use_v2=self.use_v2)
        
        if not start_node.solution:
            return {}
        
        start_node.cost = self.env.calc_solution_cost(start_node.solution)
        
        self.open_set.append(start_node)
        
        cnt = 0
        
        while self.open_set:
            cnt += 1
            
            if cnt > self.max_iterations:
                print(f"CBS reached max iterations: {self.max_iterations}")
                return self.generate_plan(self.open_set[0].solution)
            
            p = self.find_min_cost(self.open_set)
            self.open_set.remove(p)
            self.closed_set.append(p)
            
            self.env.set_constraints(p.constraint_dict)
            
            conflict = self.env.get_first_conflict(p.solution)
            
            if cnt % 100 == 0:
                print(f"CBS iteration {cnt}, cost: {p.cost}")
            
            if not conflict:
                print(f"CBS solved in {cnt} iterations")
                return self.generate_plan(p.solution)
            
            constraint_dict = self.env.create_constraint_from_conflict(conflict)
            
            for agent_name in constraint_dict.keys():
                new_node = copy.deepcopy(p)
                new_node.parent = p
                new_node.constraint_dict[agent_name].vertex_constraints.update(
                    constraint_dict[agent_name].vertex_constraints
                )
                new_node.constraint_dict[agent_name].edge_constraints.update(
                    constraint_dict[agent_name].edge_constraints
                )
                
                self.env.set_constraints(new_node.constraint_dict)
                
                if self.use_v2:
                    new_node.solution = self.env.calc_one_solution(p.solution, agent_name)
                else:
                    new_node.solution = self.env.calc_solution(use_v2=self.use_v2)
                
                if not new_node.solution:
                    continue
                
                new_node.cost = self.env.calc_solution_cost(new_node.solution)
                new_node.nc = self.env.calc_num_of_conflicts(new_node.constraint_dict)
                
                if not self.is_in_open_set(new_node):
                    self.open_set.append(new_node)
        
        print("CBS failed: no solution found")
        return {}
    
    def find_min_cost(self, node_list: List[CTNode]) -> CTNode:
        """找到cost最小的节点"""
        if self.use_priority:
            min_node = None
            min_cost = float('inf')
            
            for node in node_list:
                if node.cost < min_cost:
                    min_node = node
                    min_cost = node.cost
            
            return min_node
        else:
            min_node = None
            min_cost = float('inf')
            
            for node in node_list:
                if node.cost < min_cost:
                    min_node = node
                    min_cost = node.cost
                elif node.cost == min_cost:
                    if min_node and node.nc > min_node.nc:
                        min_node = node
            
            return min_node
    
    def is_in_open_set(self, node: CTNode) -> bool:
        """检查节点是否在开放列表中"""
        for n in self.open_set:
            if self.solution_equal(n.solution, node.solution):
                return True
        return False
    
    def solution_equal(self, sol1: Dict, sol2: Dict) -> bool:
        """比较两个解决方案是否相同"""
        for agent in sol1:
            if agent not in sol2:
                return False
            if len(sol1[agent]) != len(sol2[agent]):
                return False
            for i, state in enumerate(sol1[agent]):
                if (state.time != sol2[agent][i].time or 
                    state.location.x != sol2[agent][i].location.x or
                    state.location.y != sol2[agent][i].location.y):
                    return False
        return True
    
    def generate_plan(self, solution: Dict[str, List[State]]) -> Dict[str, List[Dict]]:
        """生成执行计划"""
        plan = {}
        for agent_name in solution:
            path = solution[agent_name]
            item_list = []
            for state in path:
                item = {
                    't': state.time,
                    'x': state.location.x,
                    'y': state.location.y
                }
                item_list.append(item)
                plan[agent_name] = item_list
        return plan


class CBSV2(CBS):
    """改进版CBS算法"""
    
    def __init__(self, env):
        super().__init__(env, use_v2=True, use_priority=True)


class EnhancedCBS(CBS):
    """增强版CBS - 支持更多冲突类型和优化策略"""
    
    def __init__(self, env):
        super().__init__(env, use_v2=True, use_priority=True)
        self.conflict_history: List[Conflict] = []
    
    def get_first_conflict_enhanced(self, solution: Dict[str, List[State]]) -> Optional[Conflict]:
        """获取第一个冲突（支持更多冲突类型）"""
        max_time = 0
        agent_names = []
        
        for agent_name in solution:
            path = solution[agent_name]
            max_time = max(max_time, len(path))
            agent_names.append(agent_name)
        
        for t in range(max_time):
            for i in range(len(agent_names)):
                for j in range(i + 1, len(agent_names)):
                    agent1 = agent_names[i]
                    agent2 = agent_names[j]
                    
                    state1 = self.get_state(agent1, solution, t)
                    state2 = self.get_state(agent2, solution, t)
                    
                    if state1.is_equal_except_time(state2):
                        conflict = Conflict()
                        conflict.time = t
                        conflict.conflict_type = Conflict.TYPE_VERTEX
                        conflict.location1 = state1.location
                        conflict.agent1 = agent1
                        conflict.agent2 = agent2
                        return conflict
                    
                    if t < max_time - 1:
                        state1a = self.get_state(agent1, solution, t)
                        state1b = self.get_state(agent1, solution, t + 1)
                        state2a = self.get_state(agent2, solution, t)
                        state2b = self.get_state(agent2, solution, t + 1)
                        
                        if (state1a.is_equal_except_time(state2b) and 
                            state1b.is_equal_except_time(state2a)):
                            conflict = Conflict()
                            conflict.time = t
                            conflict.conflict_type = Conflict.TYPE_EDGE
                            conflict.agent1 = agent1
                            conflict.agent2 = agent2
                            conflict.location1 = state1a.location
                            conflict.location2 = state1b.location
                            return conflict
        
        return None
    
    def get_state(self, agent_name: str, solution: Dict[str, List[State]], time: int) -> State:
        """获取特定时间的状态"""
        if time < len(solution[agent_name]):
            return solution[agent_name][time]
        else:
            index = len(solution[agent_name]) - 1
            return solution[agent_name][index]
