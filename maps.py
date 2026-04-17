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


MAP_COMPLEX_TERRAIN = {
    'dimension': [15, 15],
    'obstacles': [
        [5, 5], [5, 6], [5, 7], [5, 8], [5, 9],
        [9, 2], [9, 3], [9, 4], [9, 5], [9, 6],
        [2, 10], [3, 10], [4, 10], [5, 10], [6, 10],
    ],
    'terrain': {
        'grass': [[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3],
                  [10, 10], [10, 11], [11, 10], [11, 11]],
        'sand': [[3, 3], [3, 4], [3, 5], [4, 3], [4, 4], [4, 5], [5, 3],
                 [8, 8], [8, 9], [9, 8], [9, 9]],
        'water': [[7, 7], [7, 8], [8, 7], [8, 8]],
        'road': [[0, 7], [1, 7], [2, 7], [3, 7], [4, 7], [6, 7], [7, 7],
                 [7, 0], [7, 1], [7, 2], [7, 3], [7, 4], [7, 5], [7, 6]],
    },
    'agents': [
        {'start': [0, 0], 'goal': [14, 14], 'name': 'agent1', 'color': [255, 0, 0]},
        {'start': [14, 0], 'goal': [0, 14], 'name': 'agent2', 'color': [0, 255, 0]},
        {'start': [7, 0], 'goal': [7, 14], 'name': 'agent3', 'color': [0, 0, 255]},
    ],
    'wallRatio': -1,
    'use_diagonal': True
}


MAP_MAZE = {
    'dimension': [20, 20],
    'obstacles': [
        [2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5],
        [4, 2], [4, 3], [4, 4], [4, 5], [4, 6], [4, 7], [4, 8],
        [6, 0], [6, 1], [6, 2], [6, 4], [6, 5], [6, 6], [6, 7], [6, 8], [6, 9],
        [8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [8, 7], [8, 8], [8, 10], [8, 11], [8, 12],
        [10, 0], [10, 1], [10, 2], [10, 4], [10, 5], [10, 6], [10, 7], [10, 8], [10, 9],
        [12, 2], [12, 3], [12, 4], [12, 5], [12, 7], [12, 8], [12, 9], [12, 10], [12, 11],
        [14, 0], [14, 1], [14, 2], [14, 3], [14, 4], [14, 5], [14, 6], [14, 8], [14, 9], [14, 10],
        [16, 2], [16, 3], [16, 4], [16, 5], [16, 6], [16, 7], [16, 8], [16, 9], [16, 11], [16, 12], [16, 13],
        [18, 0], [18, 1], [18, 2], [18, 3], [18, 4], [18, 5], [18, 6], [18, 7], [18, 8], [18, 9], [18, 10],
    ],
    'terrain': {
        'road': [[1, 10], [3, 10], [5, 10], [7, 10], [9, 10], [11, 10], [13, 10], [15, 10], [17, 10], [19, 10],
                 [10, 3], [10, 5], [10, 7], [10, 9], [10, 11], [10, 13], [10, 15], [10, 17]],
    },
    'agents': [
        {'start': [0, 0], 'goal': [19, 19], 'name': 'agent1', 'color': [255, 0, 0]},
        {'start': [19, 0], 'goal': [0, 19], 'name': 'agent2', 'color': [0, 255, 0]},
    ],
    'wallRatio': -1,
    'use_diagonal': True
}


MAP_LARGE_COMPLEX = {
    'dimension': [30, 30],
    'obstacles': [
        [5, i] for i in range(15)
    ] + [
        [10, i] for i in range(20)
    ] + [
        [15, i] for i in range(10)
    ] + [
        [20, i] for i in range(20)
    ] + [
        [25, i] for i in range(15)
    ],
    'terrain': {
        'grass': [[i, j] for i in range(30) for j in range(30) if (i + j) % 7 == 0],
        'sand': [[i, j] for i in range(30) for j in range(30) if (i * j) % 11 == 0],
    },
    'agents': [
        {'start': [0, 0], 'goal': [29, 29], 'name': 'agent1', 'color': [255, 0, 0]},
        {'start': [29, 0], 'goal': [0, 29], 'name': 'agent2', 'color': [0, 255, 0]},
        {'start': [0, 15], 'goal': [29, 15], 'name': 'agent3', 'color': [0, 0, 255]},
    ],
    'wallRatio': -1,
    'use_diagonal': True
}


def get_map(name: str):
    """获取预设地图"""
    maps = {
        'map_8by8_12_1': MAP_8BY8_12_1,
        'map_8by8_12_2': MAP_8BY8_12_2,
        'map_8by8_12_3': MAP_8BY8_12_3,
        'map_10by10_simple': MAP_10BY10_SIMPLE,
        'map_15by15': MAP_15BY15,
        'map_complex_terrain': MAP_COMPLEX_TERRAIN,
        'map_maze': MAP_MAZE,
        'map_large_complex': MAP_LARGE_COMPLEX,
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
