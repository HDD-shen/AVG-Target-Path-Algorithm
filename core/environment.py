"""
环境类 - 管理地图、智能体和约束
"""

from typing import Dict, List, Optional, Set
from .data_structures import (
    Location, State, Cell, Agent, Constraints, 
    VertexConstraint, EdgeConstraint, Conflict, DIRS
)


class Environment:
    """环境类 - 管理地图网格、智能体和约束"""
    
    def __init__(self, dimension: List[int], agents: List[Agent], 
                 wall_ratio: float = -1, obstacles: List[List[int]] = None):
        """
        初始化环境
        :param dimension: [cols, rows] 地图尺寸
        :param agents: 智能体列表
        :param wall_ratio: 障碍物比例（-1表示使用指定的obstacles）
        :param obstacles: 指定障碍物位置列表
        """
        self.dimension = dimension  # [cols, rows]
        self.cols = dimension[0]
        self.rows = dimension[1]
        
        self.wall_ratio = wall_ratio
        self.obstacles = obstacles if obstacles else []
        
        # 网格
        self.grid: List[List[Cell]] = []
        
        # 智能体
        self.agents = agents
        self.agent_dict: Dict[str, Dict] = {}
        
        # 约束
        self.constraints = Constraints()
        self.constraint_dict: Dict[str, Constraints] = {}
        
        # 算法
        from .astar import AStar, AStarV2
        self.a_star = AStar(self)
        self.a_star_v2 = AStarV2(self)
        self.alg = self.a_star
        
        # 初始化
        self.init_grid()
        self.make_agent_dict()
    
    def init_grid(self):
        """初始化网格"""
        if self.wall_ratio == -1:
            # 使用指定的障碍物
            for i in range(self.cols):
                self.grid.append([])
                for j in range(self.rows):
                    self.grid[i].append(Cell(i, j))
            
            # 设置障碍物
            for obs in self.obstacles:
                self.grid[obs[0]][obs[1]].set_wall(True)
        else:
            # 随机生成障碍物
            import random
            for i in range(self.cols):
                self.grid.append([])
                for j in range(self.rows):
                    is_wall = random.random() < self.wall_ratio
                    self.grid[i].append(Cell(i, j, is_wall))
                    if is_wall:
                        self.obstacles.append([i, j])
    
    def make_agent_dict(self):
        """创建智能体字典"""
        self.agent_dict = {}
        for agent in self.agents:
            start_state = State(0, Location(agent.start[0], agent.start[1]))
            goal_state = State(0, Location(agent.goal[0], agent.goal[1]))
            
            self.agent_dict[agent.name] = {
                'start': start_state,
                'goal': goal_state
            }
    
    def get_agent_start(self, agent_name: str) -> Location:
        """获取智能体起点"""
        return self.agent_dict[agent_name]['start'].location
    
    def get_agent_goal(self, agent_name: str) -> Location:
        """获取智能体终点"""
        return self.agent_dict[agent_name]['goal'].location
    
    def get_neighbors(self, state: State) -> List[State]:
        """获取邻居状态"""
        neighbors = []
        
        # 等待（停在原地）
        new_state = State(state.time + 1, state.location)
        if self.is_state_valid(new_state):
            neighbors.append(new_state)
        
        # 四个方向移动
        for dx, dy in DIRS:
            new_x = state.location.x + dx
            new_y = state.location.y + dy
            new_loc = Location(new_x, new_y)
            new_state = State(state.time + 1, new_loc)
            
            if self.is_state_valid(new_state) and self.is_edge_satisfied(state, new_state):
                neighbors.append(new_state)
        
        return neighbors
    
    def is_state_valid(self, state: State) -> bool:
        """检查状态是否有效（边界、障碍物、顶点约束）"""
        loc = state.location
        
        # 边界检查
        if loc.x < 0 or loc.x >= self.cols or loc.y < 0 or loc.y >= self.rows:
            return False
        
        # 障碍物检查
        if [loc.x, loc.y] in self.obstacles:
            return False
        
        # 顶点约束检查
        if self.constraints.has_vertex_constraint(state.time, loc):
            return False
        
        return True
    
    def is_edge_satisfied(self, state1: State, state2: State) -> bool:
        """检查边约束是否满足"""
        return not self.constraints.has_edge_constraint(
            state1.time, state1.location, state2.location
        )
    
    def calc_g(self, current: State, neighbor: State) -> int:
        """计算g值（移动代价）"""
        return 1
    
    def calc_h(self, state: State, agent_name: str) -> int:
        """计算h值（启发式估计 - 曼哈顿距离）"""
        goal = self.get_agent_goal(agent_name)
        return abs(state.location.x - goal.x) + abs(state.location.y - goal.y)
    
    def is_reach_target(self, state: State, agent_name: str) -> bool:
        """检查是否到达目标"""
        goal_state = self.agent_dict[agent_name]['goal']
        return state.is_equal_except_time(goal_state)
    
    def calc_solution(self, use_v2: bool = False) -> Dict[str, List[State]]:
        """计算所有智能体的路径解决方案"""
        if use_v2:
            self.alg = self.a_star_v2
        else:
            self.alg = self.a_star
        
        solution = {}
        for agent_name in self.agent_dict.keys():
            # 确保每个agent都有约束
            if agent_name not in self.constraint_dict:
                self.constraint_dict[agent_name] = Constraints()
            self.constraints = self.constraint_dict[agent_name]
            
            path = self.alg.search(agent_name)
            if not path:
                return {}
            solution[agent_name] = path
        
        return solution
    
    def calc_one_solution(self, org_solution: Dict, agent_to_adjust: str) -> Dict[str, List[State]]:
        """只重新计算单个智能体的路径"""
        import copy
        solution = copy.deepcopy(org_solution)
        
        for agent_name in self.agent_dict.keys():
            if agent_name == agent_to_adjust:
                if agent_name not in self.constraint_dict:
                    self.constraint_dict[agent_name] = Constraints()
                self.constraints = self.constraint_dict[agent_name]
                
                path = self.alg.search(agent_name)
                if not path:
                    return {}
                solution[agent_name] = path
        
        return solution
    
    def calc_solution_cost(self, solution: Dict[str, List[State]]) -> int:
        """计算解决方案的总代价"""
        total_cost = 0
        for agent_name in solution:
            path = solution[agent_name]
            total_cost += len(path)
        return total_cost
    
    def calc_num_of_conflicts(self, constraint_dict: Dict[str, Constraints]) -> int:
        """计算约束数量"""
        nc = 0
        for agent_name in constraint_dict:
            c = constraint_dict[agent_name]
            nc += len(c.vertex_constraints)
            nc += len(c.edge_constraints)
        return nc
    
    def set_constraints(self, constraint_dict: Dict[str, Constraints]):
        """设置约束字典"""
        self.constraint_dict = constraint_dict
    
    def get_first_conflict(self, solution: Dict[str, List[State]]) -> Optional[Conflict]:
        """获取解决方案中的第一个冲突"""
        # 找到最大时间步
        max_time = 0
        agent_names = []
        
        for agent_name in solution:
            path = solution[agent_name]
            max_time = max(max_time, len(path))
            agent_names.append(agent_name)
        
        # 检查所有智能体对
        for t in range(max_time):
            # 检查点冲突
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
            
            # 检查边冲突
            for i in range(len(agent_names)):
                for j in range(i + 1, len(agent_names)):
                    agent1 = agent_names[i]
                    agent2 = agent_names[j]
                    
                    state1a = self.get_state(agent1, solution, t)
                    state1b = self.get_state(agent1, solution, t + 1)
                    state2a = self.get_state(agent2, solution, t)
                    state2b = self.get_state(agent2, solution, t + 1)
                    
                    # 交换冲突
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
            # 超过路径长度，返回最后一个状态
            index = len(solution[agent_name]) - 1
            return solution[agent_name][index]
    
    def create_constraint_from_conflict(self, conflict: Conflict) -> Dict[str, Constraints]:
        """从冲突创建约束"""
        constraint_dict = {}
        
        if conflict.conflict_type == Conflict.TYPE_VERTEX:
            # 点冲突
            c = Constraints()
            vc = VertexConstraint(conflict.time, conflict.location1)
            c.add_vertex_constraint(vc)
            constraint_dict[conflict.agent1] = c
            constraint_dict[conflict.agent2] = c
        
        elif conflict.conflict_type == Conflict.TYPE_EDGE:
            # 边冲突
            c1 = Constraints()
            c2 = Constraints()
            
            ec1 = EdgeConstraint(conflict.time, conflict.location1, conflict.location2)
            ec2 = EdgeConstraint(conflict.time, conflict.location2, conflict.location1)
            
            c1.add_edge_constraint(ec1)
            c2.add_edge_constraint(ec2)
            
            constraint_dict[conflict.agent1] = c1
            constraint_dict[conflict.agent2] = c2
        
        return constraint_dict
    
    def add_obstacle(self, x: int, y: int):
        """添加障碍物"""
        if [x, y] not in self.obstacles:
            self.obstacles.append([x, y])
            if 0 <= x < self.cols and 0 <= y < self.rows:
                self.grid[x][y].set_wall(True)
    
    def remove_obstacle(self, x: int, y: int):
        """移除障碍物"""
        if [x, y] in self.obstacles:
            self.obstacles.remove([x, y])
            if 0 <= x < self.cols and 0 <= y < self.rows:
                self.grid[x][y].is_wall = False
                self.grid[x][y].cell_type = 0
    
    def is_wall(self, x: int, y: int) -> bool:
        """检查是否为障碍物"""
        return [x, y] in self.obstacles
    
    def __str__(self):
        return f"Environment(cols={self.cols}, rows={self.rows}, agents={len(self.agents)}, obstacles={len(self.obstacles)})"
