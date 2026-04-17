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
    nc: int = 0  # number of conflicts


class CBS:
    """CBS（基于冲突的搜索）算法类"""
    
    def __init__(self, env, use_v2=False):
        """
        初始化CBS算法
        :param env: 环境对象
        :param use_v2: 是否使用改进版本
        """
        self.env = env
        self.use_v2 = use_v2
        self.open_set: List[CTNode] = []
        self.closed_set: List[CTNode] = []
    
    def search(self) -> Dict[str, List[Dict]]:
        """
        执行CBS算法搜索
        :return: 解决方案字典 {agent_name: [{'t': t, 'x': x, 'y': y}, ...]}
        """
        # 创建根节点
        start_node = CTNode()
        
        # 初始化约束字典
        for agent_name in self.env.agent_dict.keys():
            start_node.constraint_dict[agent_name] = Constraints()
        
        # 计算初始解
        start_node.solution = self.env.calc_solution(use_v2=self.use_v2)
        
        if not start_node.solution:
            return {}
        
        start_node.cost = self.env.calc_solution_cost(start_node.solution)
        
        # 加入开放列表
        self.open_set.append(start_node)
        
        cnt = 0
        
        while self.open_set:
            cnt += 1
            
            # 取出cost最小的节点
            p = self.find_min_cost(self.open_set)
            self.open_set.remove(p)
            self.closed_set.append(p)
            
            # 设置当前约束
            self.env.set_constraints(p.constraint_dict)
            
            # 获取第一个冲突
            conflict = self.env.get_first_conflict(p.solution)
            
            print(f"CBS iteration {cnt}")
            
            # 如果没有冲突，找到解
            if not conflict:
                print(f"CBS solved in {cnt} iterations")
                return self.generate_plan(p.solution)
            
            # 将冲突转换为约束
            constraint_dict = self.env.create_constraint_from_conflict(conflict)
            
            # 根据冲突分裂节点
            for agent_name in constraint_dict.keys():
                new_node = copy.deepcopy(p)
                new_node.constraint_dict[agent_name].vertex_constraints.update(
                    constraint_dict[agent_name].vertex_constraints
                )
                new_node.constraint_dict[agent_name].edge_constraints.update(
                    constraint_dict[agent_name].edge_constraints
                )
                
                # 切换环境约束
                self.env.set_constraints(new_node.constraint_dict)
                
                # 重新计算该agent的路径
                if self.use_v2:
                    new_node.solution = self.env.calc_one_solution(p.solution, agent_name)
                else:
                    new_node.solution = self.env.calc_solution(use_v2=self.use_v2)
                
                if not new_node.solution:
                    continue
                
                new_node.cost = self.env.calc_solution_cost(new_node.solution)
                new_node.nc = self.env.calc_num_of_conflicts(new_node.constraint_dict)
                
                # 检查是否已在开放列表中
                if not self.is_in_open_set(new_node):
                    self.open_set.append(new_node)
        
        print("CBS failed: no solution found")
        return {}
    
    def find_min_cost(self, node_list: List[CTNode]) -> CTNode:
        """找到cost最小的节点"""
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
        super().__init__(env, use_v2=True)
