"""
环境类 - 管理地图、智能体和约束
"""

from typing import Dict, List, Optional, Set
from .data_structures import (
    Location, State, Cell, Agent, Constraints, 
    VertexConstraint, EdgeConstraint, Conflict, DIRS, DIRS8
)


class Environment:
    """环境类 - 管理地图网格、智能体和约束"""
    
    def __init__(self, dimension: List[int], agents: List[Agent], 
                 wall_ratio: float = -1, obstacles: List[List[int]] = None,
                 terrain_map: Dict[str, List[List[int]]] = None,
                 use_diagonal: bool = True):
        """
        初始化环境
        :param dimension: [cols, rows] 地图尺寸
        :param agents: 智能体列表
        :param wall_ratio: 障碍物比例（-1表示使用指定的obstacles）
        :param obstacles: 指定障碍物位置列表
        :param terrain_map: 地形图 {terrain_type: [[x,y], ...]}
        :param use_diagonal: 是否允许对角线移动
        """
        self.dimension = dimension
        self.cols = dimension[0]
        self.rows = dimension[1]
        
        self.wall_ratio = wall_ratio
        self.obstacles = obstacles if obstacles else []
        self.terrain_map = terrain_map if terrain_map else {}
        self.use_diagonal = use_diagonal
        
        self.grid: List[List[Cell]] = []
        
        self.agents = agents
        self.agent_dict: Dict[str, Dict] = {}
        
        self.constraints = Constraints()
        self.constraint_dict: Dict[str, Constraints] = {}
        
        from .astar import AStar, AStarV2, WeightedAStar, JumpPointSearch
        self.a_star = AStar(self)
        self.a_star_v2 = AStarV2(self)
        self.weighted_astar = WeightedAStar(self)
        self.jps = JumpPointSearch(self)
        self.alg = self.a_star
        
        self.init_grid()
        self.make_agent_dict()
    
    def init_grid(self):
        """初始化网格"""
        if self.wall_ratio == -1:
            for i in range(self.cols):
                self.grid.append([])
                for j in range(self.rows):
                    self.grid[i].append(Cell(i, j))
            
            for obs in self.obstacles:
                self.grid[obs[0]][obs[1]].set_wall(True)
        else:
            import random
            for i in range(self.cols):
                self.grid.append([])
                for j in range(self.rows):
                    is_wall = random.random() < self.wall_ratio
                    self.grid[i][j] = Cell(i, j, is_wall)
                    if is_wall:
                        self.obstacles.append([i, j])
        
        self._apply_terrain_map()
    
    def _apply_terrain_map(self):
        """应用地形图"""
        for terrain_type, positions in self.terrain_map.items():
            for pos in positions:
                x, y = pos[0], pos[1]
                if 0 <= x < self.cols and 0 <= y < self.rows:
                    self.grid[x][y].set_terrain(terrain_type)
    
    def set_terrain(self, x: int, y: int, terrain_type: str):
        """设置指定位置的地形"""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.grid[x][y].set_terrain(terrain_type)
    
    def get_terrain_cost(self, x: int, y: int) -> float:
        """获取位置的地形代价"""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[x][y].get_cost()
        return float('inf')
    
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
        
        new_state = State(state.time + 1, state.location)
        if self.is_state_valid(new_state):
            neighbors.append(new_state)
        
        directions = DIRS8 if self.use_diagonal else DIRS
        for dx, dy in directions:
            new_x = state.location.x + dx
            new_y = state.location.y + dy
            
            if self.use_diagonal and dx != 0 and dy != 0:
                if not self._can_move_diagonal(state.location.x, state.location.y, new_x, new_y):
                    continue
            
            new_loc = Location(new_x, new_y)
            new_state = State(state.time + 1, new_loc)
            
            if self.is_state_valid(new_state) and self.is_edge_satisfied(state, new_state):
                neighbors.append(new_state)
        
        return neighbors
    
    def _can_move_diagonal(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """检查对角线移动是否可行（需要两个相邻格子都不是墙）"""
        if self.is_wall(x1, y2) and self.is_wall(x2, y1):
            return False
        return True
    
    def get_neighbors_extended(self, state: State) -> List[State]:
        """获取邻居状态（带移动代价）"""
        neighbors = []
        
        new_state = State(state.time + 1, state.location)
        if self.is_state_valid(new_state):
            cost = self.get_terrain_cost(state.location.x, state.location.y)
            neighbors.append((new_state, cost))
        
        directions = DIRS8 if self.use_diagonal else DIRS
        for dx, dy in directions:
            new_x = state.location.x + dx
            new_y = state.location.y + dy
            
            if self.use_diagonal and dx != 0 and dy != 0:
                if not self._can_move_diagonal(state.location.x, state.location.y, new_x, new_y):
                    continue
            
            new_loc = Location(new_x, new_y)
            new_state = State(state.time + 1, new_loc)
            
            if self.is_state_valid(new_state) and self.is_edge_satisfied(state, new_state):
                if dx != 0 and dy != 0:
                    move_cost = 1.414
                else:
                    move_cost = 1.0
                terrain_cost = self.get_terrain_cost(new_x, new_y)
                total_cost = move_cost * terrain_cost
                neighbors.append((new_state, total_cost))
        
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
    
    def calc_g(self, current: State, neighbor: State, use_weighted: bool = False) -> float:
        """计算g值（移动代价）"""
        if not use_weighted:
            return 1
        
        dx = neighbor.location.x - current.location.x
        dy = neighbor.location.y - current.location.y
        
        if dx != 0 and dy != 0:
            move_cost = 1.414
        else:
            move_cost = 1.0
        
        terrain_cost = self.get_terrain_cost(neighbor.location.x, neighbor.location.y)
        return move_cost * terrain_cost
    
    def calc_h(self, state: State, agent_name: str, heuristic_type: str = "manhattan") -> float:
        """计算h值（启发式估计）"""
        goal = self.get_agent_goal(agent_name)
        
        if heuristic_type == "manhattan":
            return abs(state.location.x - goal.x) + abs(state.location.y - goal.y)
        elif heuristic_type == "euclidean":
            return ((state.location.x - goal.x) ** 2 + (state.location.y - goal.y) ** 2) ** 0.5
        elif heuristic_type == "octile":
            dx = abs(state.location.x - goal.x)
            dy = abs(state.location.y - goal.y)
            return max(dx, dy) + (1.414 - 1) * min(dx, dy)
        elif heuristic_type == "weighted":
            dx = abs(state.location.x - goal.x)
            dy = abs(state.location.y - goal.y)
            base = max(dx, dy) + (1.414 - 1) * min(dx, dy)
            return base * 1.0
        return abs(state.location.x - goal.x) + abs(state.location.y - goal.y)
    
    def calc_h_with_terrain(self, state: State, agent_name: str) -> float:
        """计算带地形的h值（考虑地形代价）"""
        goal = self.get_agent_goal(agent_name)
        dx = abs(state.location.x - goal.x)
        dy = abs(state.location.y - goal.y)
        
        base_h = max(dx, dy) + (1.414 - 1) * min(dx, dy)
        
        avg_terrain_cost = 1.0
        return base_h * avg_terrain_cost
    
    def is_reach_target(self, state: State, agent_name: str) -> bool:
        """检查是否到达目标"""
        goal_state = self.agent_dict[agent_name]['goal']
        return state.is_equal_except_time(goal_state)
    
    def calc_solution(self, use_v2: bool = False, use_weighted: bool = False,
                      algorithm: str = "astar") -> Dict[str, List[State]]:
        """计算所有智能体的路径解决方案
        :param use_v2: 是否使用A* v2
        :param use_weighted: 是否使用加权A*
        :param algorithm: 算法类型 "astar", "astar_v2", "weighted", "jps"
        """
        if algorithm == "astar_v2" or use_v2:
            self.alg = self.a_star_v2
        elif algorithm == "weighted":
            self.alg = self.weighted_astar
        elif algorithm == "jps":
            self.alg = self.jps
        else:
            self.alg = self.a_star
        
        solution = {}
        for agent_name in self.agent_dict.keys():
            if agent_name not in self.constraint_dict:
                self.constraint_dict[agent_name] = Constraints()
            self.constraints = self.constraint_dict[agent_name]
            
            path = self.alg.search(agent_name)
            if not path:
                return {}
            solution[agent_name] = path
        
        return solution
    
    def calc_one_solution(self, org_solution: Dict, agent_to_adjust: str,
                          use_weighted: bool = False) -> Dict[str, List[State]]:
        """只重新计算单个智能体的路径
        :param org_solution: 原解决方案
        :param agent_to_adjust: 要重新规划的智能体名称
        :param use_weighted: 是否使用加权A*
        """
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
