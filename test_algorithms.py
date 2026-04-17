#!/usr/bin/env python
"""测试所有寻路算法"""

from core.data_structures import Agent
from core.environment import Environment
from core.algorithms import MAPFPUSH
from maps import get_map


def test_algorithm(algo_name, algo_type):
    """测试单个算法"""
    try:
        map_config = get_map('map_10by10_simple')
        agents = [Agent(start=a['start'], goal=a['goal'], name=a['name'], color=a['color']) 
                  for a in map_config['agents']]
        env = Environment(map_config['dimension'], agents, -1, map_config.get('obstacles', []))
        solver = MAPFPUSH(env, path_algorithm=algo_type)
        solution = solver.search()
        
        if solution:
            cost = sum(len(p) for p in solution.values())
            print(f"[OK] {algo_name}: 成功 - 代价 {cost}")
            return True
        else:
            print(f"[FAIL] {algo_name}: 失败")
            return False
    except Exception as e:
        print(f"[ERROR] {algo_name}: {e}")
        return False


if __name__ == "__main__":
    algorithms = [
        ("A* 标准", "astar"),
        ("A* v2", "astar_v2"),
        ("Weighted A*", "weighted"),
        ("JPS", "jps"),
    ]
    
    print("=" * 50)
    print("测试所有寻路算法")
    print("=" * 50)
    
    success_count = 0
    for name, algo_type in algorithms:
        if test_algorithm(name, algo_type):
            success_count += 1
    
    print("=" * 50)
    print(f"测试完成: {success_count}/{len(algorithms)} 成功")
    print("=" * 50)
