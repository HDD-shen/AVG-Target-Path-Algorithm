"""
基础数据结构模块
"""

from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict, Any


@dataclass
class Location:
    """位置类"""
    x: int
    y: int
    
    def __eq__(self, other):
        if isinstance(other, Location):
            return self.x == other.x and self.y == other.y
        return False
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __repr__(self):
        return self.__str__()
    
    def to_list(self):
        return [self.x, self.y]
    
    @staticmethod
    def from_list(lst: List[int]):
        return Location(lst[0], lst[1])


@dataclass
class State:
    """状态类（包含位置和时间）"""
    time: int
    location: Location
    
    def is_equal_except_time(self, other) -> bool:
        """比较位置是否相同（忽略时间）"""
        if not isinstance(other, State):
            return False
        return self.location == other.location
    
    def __eq__(self, other):
        if isinstance(other, State):
            return self.time == other.time and self.location == other.location
        return False
    
    def __hash__(self):
        return hash((self.time, self.location.x, self.location.y))
    
    def __str__(self):
        return f"State(t={self.time}, loc={self.location})"
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        return {'t': self.time, 'x': self.location.x, 'y': self.location.y}
    
    @staticmethod
    def from_dict(d: Dict):
        return State(d['t'], Location(d['x'], d['y']))


@dataclass
class VertexConstraint:
    """顶点约束 - 禁止某个智能体在特定时间位于某个位置"""
    time: int
    location: Location
    
    def __eq__(self, other):
        if isinstance(other, VertexConstraint):
            return self.time == other.time and self.location == other.location
        return False
    
    def __hash__(self):
        return hash((self.time, self.location.x, self.location.y))
    
    def __str__(self):
        return f"VC(t={self.time}, loc={self.location})"
    
    def __repr__(self):
        return self.__str__()


@dataclass
class EdgeConstraint:
    """边约束 - 禁止某个智能体从位置A移动到位置B"""
    time: int
    location1: Location
    location2: Location
    
    def __eq__(self, other):
        if isinstance(other, EdgeConstraint):
            return (self.time == other.time and 
                    self.location1 == other.location1 and 
                    self.location2 == other.location2)
        return False
    
    def __hash__(self):
        return hash((self.time, self.location1.x, self.location1.y, 
                    self.location2.x, self.location2.y))
    
    def __str__(self):
        return f"EC(t={self.time}, {self.location1}->{self.location2})"
    
    def __repr__(self):
        return self.__str__()


class Constraints:
    """约束集合类"""
    def __init__(self):
        self.vertex_constraints: Set[VertexConstraint] = set()
        self.edge_constraints: Set[EdgeConstraint] = set()
    
    def add_vertex_constraint(self, vc: VertexConstraint):
        """添加顶点约束"""
        self.vertex_constraints.add(vc)
    
    def add_edge_constraint(self, ec: EdgeConstraint):
        """添加边约束"""
        self.edge_constraints.add(ec)
    
    def has_vertex_constraint(self, time: int, location: Location) -> bool:
        """检查是否存在顶点约束"""
        return VertexConstraint(time, location) in self.vertex_constraints
    
    def has_edge_constraint(self, time: int, loc1: Location, loc2: Location) -> bool:
        """检查是否存在边约束"""
        return EdgeConstraint(time, loc1, loc2) in self.edge_constraints
    
    def __str__(self):
        return f"VCs: {len(self.vertex_constraints)},ECs: {len(self.edge_constraints)}"
    
    def __repr__(self):
        return self.__str__()


@dataclass
class Conflict:
    """冲突类"""
    time: int = 0
    agent1: str = ""
    agent2: str = ""
    location1: Optional[Location] = None
    location2: Optional[Location] = None
    conflict_type: int = 0  # 1: Vertex conflict, 2: Edge conflict
    
    TYPE_VERTEX = 1
    TYPE_EDGE = 2


@dataclass
class Cell:
    """网格单元格类"""
    x: int
    y: int
    is_wall: bool = False
    cell_type: int = 0  # 0: empty, 1: wall, 2: start, 3: goal
    
    def set_wall(self, is_wall: bool):
        self.is_wall = is_wall
        if is_wall:
            self.cell_type = 1
    
    def __str__(self):
        return f"Cell({self.x}, {self.y}, type={self.cell_type})"
    
    def __repr__(self):
        return self.__str__()


@dataclass
class Agent:
    """智能体类"""
    start: List[int]  # [x, y]
    goal: List[int]
    name: str
    color: List[int]  # [r, g, b]
    path: List[Dict] = field(default_factory=list)  # [{'t': t, 'x': x, 'y': y}, ...]
    path_length: int = 0
    is_reached: bool = False
    turn_count: int = 0
    wait_count: int = 0
    
    def get_start_location(self) -> Location:
        return Location(self.start[0], self.start[1])
    
    def get_goal_location(self) -> Location:
        return Location(self.goal[0], self.goal[1])
    
    def full_fill_path(self, max_t: int):
        """将路径填充到最大时间点"""
        if not self.path:
            return
        n = len(self.path)
        last_item = self.path[-1]
        for i in range(n, max_t):
            self.path.append(last_item.copy())
    
    def calc_turn_count(self):
        """计算转弯次数"""
        self.turn_count = 0
        for i in range(2, len(self.path)):
            if (abs(self.path[i-2]['x'] - self.path[i]['x']) == 1 and 
                abs(self.path[i-2]['y'] - self.path[i]['y']) == 1):
                self.turn_count += 1
    
    def calc_wait_count(self):
        """计算等待次数"""
        self.wait_count = 0
        for i in range(1, len(self.path)):
            if (abs(self.path[i-1]['x'] - self.path[i]['x']) == 0 and 
                abs(self.path[i-1]['y'] - self.path[i]['y']) == 0):
                self.wait_count += 1
    
    def get_position_at(self, t: int) -> tuple:
        """获取特定时间的"""
        if t < len(self.path):
            return self.path[t]['x'], self.path[t]['y']
        elif self.path:
            return self.path[-1]['x'], self.path[-1]['y']
        return self.start[0], self.start[1]
    
    def __str__(self):
        return f"Agent({self.name}, start={self.start}, goal={self.goal})"
    
    def __repr__(self):
        return self.__str__()


# 四个方向的移动
DIRS = [
    (-1, 0),  # 左
    (1, 0),   # 右
    (0, -1),  # 上
    (0, 1)    # 下
]


# 八个方向的移动（包含对角线）
DIRS8 = [
    (-1, 0), (1, 0), (0, -1), (0, 1),
    (-1, -1), (-1, 1), (1, -1), (1, 1)
]
