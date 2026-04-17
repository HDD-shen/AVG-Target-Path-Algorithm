"""
测试地图和预设场景
"""


# 预设测试地图
MAP_8BY8_12_1 = {
    'dimension': [8, 8],
    'obstacles': [
        [2, 0], [2, 1], [2, 2], [2, 3], [2, 4],
        [5, 3], [5, 4], [5, 5], [5, 6], [5, 7],
        [0, 5], [1, 5]
    ],
    'agents': [
        {'start': [0, 0], 'goal': [7, 7], 'name': 'agent1', 'color': [255, 0, 0]},
    ],
    'wallRatio': -1
}

MAP_8BY8_12_2 = {
    'dimension': [8, 8],
    'obstacles': [
        [2, 0], [2, 1], [2, 2], [2, 3], [2, 4],
        [5, 3], [5, 4], [5, 5], [5, 6], [5, 7],
        [0, 5], [1, 5]
    ],
    'agents': [
        {'start': [0, 0], 'goal': [7, 7], 'name': 'agent1', 'color': [255, 0, 0]},
        {'start': [7, 0], 'goal': [0, 7], 'name': 'agent2', 'color': [0, 255, 0]},
    ],
    'wallRatio': -1
}

MAP_8BY8_12_3 = {
    'dimension': [8, 8],
    'obstacles': [
        [2, 0], [2, 1], [2, 2], [2, 3], [2, 4],
        [5, 3], [5, 4], [5, 5], [5, 6], [5, 7],
        [0, 5], [1, 5]
    ],
    'agents': [
        {'start': [0, 0], 'goal': [7, 7], 'name': 'agent1', 'color': [255, 0, 0]},
        {'start': [7, 0], 'goal': [0, 7], 'name': 'agent2', 'color': [0, 255, 0]},
        {'start': [3, 0], 'goal': [3, 7], 'name': 'agent3', 'color': [0, 0, 255]},
    ],
    'wallRatio': -1
}

MAP_10BY10_SIMPLE = {
    'dimension': [10, 10],
    'obstacles': [
        [3, 3], [3, 4], [3, 5], [3, 6],
        [6, 2], [6, 3], [6, 4], [6, 5],
    ],
    'agents': [
        {'start': [0, 0], 'goal': [9, 9], 'name': 'agent1', 'color': [255, 0, 0]},
        {'start': [9, 0], 'goal': [0, 9], 'name': 'agent2', 'color': [0, 255, 0]},
        {'start': [0, 5], 'goal': [9, 5], 'name': 'agent3', 'color': [0, 0, 255]},
    ],
    'wallRatio': -1
}

MAP_15BY15 = {
    'dimension': [15, 15],
    'obstacles': [
        [5, 5], [5, 6], [5, 7], [5, 8], [5, 9],
        [9, 2], [9, 3], [9, 4], [9, 5], [9, 6],
        [2, 10], [3, 10], [4, 10], [5, 10], [6, 10],
    ],
    'agents': [
        {'start': [0, 0], 'goal': [14, 14], 'name': 'agent1', 'color': [255, 0, 0]},
        {'start': [14, 0], 'goal': [0, 14], 'name': 'agent2', 'color': [0, 255, 0]},
        {'start': [7, 0], 'goal': [7, 14], 'name': 'agent3', 'color': [0, 0, 255]},
        {'start': [0, 7], 'goal': [14, 7], 'name': 'agent4', 'color': [255, 255, 0]},
    ],
    'wallRatio': -1
}


def get_map(name: str):
    """获取预设地图"""
    maps = {
        'map_8by8_12_1': MAP_8BY8_12_1,
        'map_8by8_12_2': MAP_8BY8_12_2,
        'map_8by8_12_3': MAP_8BY8_12_3,
        'map_10by10_simple': MAP_10BY10_SIMPLE,
        'map_15by15': MAP_15BY15,
    }
    return maps.get(name, MAP_10BY10_SIMPLE)


def generate_random_agents(num: int, cols: int, rows: int, 
                          existing_obstacles: list = None) -> list:
    """生成随机智能体"""
    import random
    
    agents = []
    colors = [
        [255, 0, 0], [0, 255, 0], [0, 0, 255],
        [255, 255, 0], [255, 0, 255], [0, 255, 255],
        [255, 128, 0], [128, 0, 255]
    ]
    
    occupied = set()
    if existing_obstacles:
        for obs in existing_obstacles:
            occupied.add(tuple(obs))
    
    for i in range(num):
        while True:
            start = [random.randint(0, cols-1), random.randint(0, rows-1)]
            if tuple(start) not in occupied:
                occupied.add(tuple(start))
                break
        
        while True:
            goal = [random.randint(0, cols-1), random.randint(0, rows-1)]
            if tuple(goal) not in occupied and tuple(goal) != tuple(start):
                break
        
        agent = {
            'start': start,
            'goal': goal,
            'name': f'agent{i+1}',
            'color': colors[i % len(colors)]
        }
        agents.append(agent)
    
    return agents


def generate_random_map(cols: int, rows: int, agent_num: int, 
                        obstacle_ratio: float = 0.1) -> dict:
    """生成随机地图"""
    import random
    
    obstacles = []
    for i in range(cols):
        for j in range(rows):
            if random.random() < obstacle_ratio:
                obstacles.append([i, j])
    
    agents = generate_random_agents(agent_num, cols, rows, obstacles)
    
    return {
        'dimension': [cols, rows],
        'obstacles': obstacles,
        'agents': agents,
        'wallRatio': -1
    }
