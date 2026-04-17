
"""
多AGV路径规划演示系统 - 主程序
"""

import sys
import time
import random
from typing import Dict, List

# 导入项目模块
from core.data_structures import Agent
from core.environment import Environment
from core.algorithms import MAPFPUSH
from maps import get_map, generate_random_map


def create_environment(map_config: dict) -> Environment:
    """从配置创建环境"""
    dimension = map_config['dimension']
    obstacles = map_config.get('obstacles', [])
    wall_ratio = map_config.get('wallRatio', -1)
    terrain_map = map_config.get('terrain', {})
    use_diagonal = map_config.get('use_diagonal', True)
    
    # 创建智能体对象
    agents = []
    for agent_config in map_config['agents']:
        agent = Agent(
            start=agent_config['start'],
            goal=agent_config['goal'],
            name=agent_config['name'],
            color=agent_config.get('color', [255, 0, 0])
        )
        agents.append(agent)
    
    env = Environment(dimension, agents, wall_ratio, obstacles, terrain_map, use_diagonal)
    return env


def run_algorithm(env: Environment, path_algorithm: str = "astar") -> Dict:
    """运行MAPF-PUSH路径规划算法
    
    Args:
        env: 环境对象
        path_algorithm: 寻路算法类型 "astar", "astar_v2", "weighted", "jps"
    
    Returns:
        Dict: 解决方案
    """
    print(f"\n{'='*50}")
    print(f"MAPF-PUSH 高效多智能体路径规划")
    print(f"地图尺寸: {env.cols} x {env.rows}")
    print(f"智能体数量: {len(env.agents)}")
    print(f"障碍物数量: {len(env.obstacles)}")
    print(f"允许对角线移动: {env.use_diagonal}")
    print(f"寻路算法: {path_algorithm}")
    print(f"{'='*50}\n")
    
    start_time = time.time()
    
    solver = MAPFPUSH(env, path_algorithm=path_algorithm)
    solution = solver.search()
    
    end_time = time.time()
    
    print(f"\n{'='*50}")
    print(f"算法运行完成！")
    print(f"总耗时: {end_time - start_time:.3f} 秒")
    if solution:
        total_cost = sum(len(path) for path in solution.values())
        print(f"解决方案总代价: {total_cost}")
    print(f"{'='*50}\n")
    
    return solution


def run_console_demo():
    """运行控制台演示"""
    print("\n" + "="*60)
    print("       多AGV路径规划演示系统 (Python版)")
    print("="*60)
    print("\n请选择测试地图:")
    print("1. map_8by8_12_1 - 8x8地图，1个AGV")
    print("2. map_8by8_12_2 - 8x8地图，2个AGV")
    print("3. map_8by8_12_3 - 8x8地图，3个AGV")
    print("4. map_10by10_simple - 10x10地图，3个AGV")
    print("5. map_15by15 - 15x15地图，4个AGV")
    print("6. map_complex_terrain - 复杂地形图(草地/沙地/水域)")
    print("7. map_maze - 迷宫地图")
    print("8. map_large_complex - 大型复杂地图")
    print("9. 自定义随机地图")
    print("0. 退出")
    
    choice = input("\n请选择 (0-9): ")
    
    if choice == '0':
        print("退出程序")
        return
    
    # 选择地图
    if choice == '1':
        map_config = get_map('map_8by8_12_1')
    elif choice == '2':
        map_config = get_map('map_8by8_12_2')
    elif choice == '3':
        map_config = get_map('map_8by8_12_3')
    elif choice == '4':
        map_config = get_map('map_10by10_simple')
    elif choice == '5':
        map_config = get_map('map_15by15')
    elif choice == '6':
        map_config = get_map('map_complex_terrain')
    elif choice == '7':
        map_config = get_map('map_maze')
    elif choice == '8':
        map_config = get_map('map_large_complex')
    elif choice == '9':
        try:
            cols = int(input("输入地图列数 (5-50): "))
            rows = int(input("输入地图行数 (5-50): "))
            agent_num = int(input("输入AGV数量 (1-10): "))
            obstacle_ratio = float(input("输入障碍物比例 (0.0-0.3): "))
            map_config = generate_random_map(cols, rows, agent_num, obstacle_ratio)
        except ValueError:
            print("输入无效，使用默认地图")
            map_config = get_map('map_10by10_simple')
    else:
        print("无效选择，使用默认地图")
        map_config = get_map('map_10by10_simple')
    
    # 创建环境
    print("\n创建环境...")
    env = create_environment(map_config)
    print(f"环境创建成功: {env}")
    
    # 选择寻路算法
    print("\n请选择寻路算法:")
    print("1. A* (标准)")
    print("2. A* v2 (改进版)")
    print("3. Weighted A* (加权，支持地形)")
    path_choice = input("请选择 (1-3): ")
    if path_choice == '2':
        path_algorithm = "astar_v2"
    elif path_choice == '3':
        path_algorithm = "weighted"
    else:
        path_algorithm = "astar"
    
    # 运行算法
    solution = run_algorithm(env, path_algorithm)
    
    if solution:
        print("\n路径规划成功！")
        
        # 显示每个AGV的路径
        for agent_name in solution:
            path = solution[agent_name]
            print(f"\n{agent_name} 路径 (长度: {len(path)}):")
            path_str = " -> ".join([f"({p['x']},{p['y']})" for p in path[:10]])
            if len(path) > 10:
                path_str += " -> ..."
            print(path_str)
        
        # 询问是否运行可视化
        show_viz = input("\n是否运行可视化演示? (y/n): ")
        if show_viz.lower() == 'y':
            try:
                from visualizer import Visualizer
                print("\n启动可视化界面...")
                print("控制说明:")
                print("  空格键: 暂停/继续")
                print("  右箭头: 单步执行")
                print("  R键: 重置")
                print("  关闭窗口退出")
                
                vis = Visualizer(env)
                vis.set_solution(solution)
                vis.run()
            except ImportError:
                print("错误: 请安装 pygame 库")
                print("运行: pip install pygame")
    else:
        print("\n路径规划失败！找不到解决方案。")


def run_simple_test():
    """运行简单测试"""
    print("\n运行简单测试...")
    
    # 使用简单地图
    map_config = get_map('map_10by10_simple')
    env = create_environment(map_config)
    
    # 运行算法
    solution = run_algorithm(env, "astar")
    
    if solution:
        print("\n路径规划成功！")
        for agent_name in solution:
            path = solution[agent_name]
            print(f"{agent_name}: {len(path)} 步")
    else:
        print("\n路径规划失败！")
    
    return solution


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            run_simple_test()
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("用法: python main.py [--test]")
    else:
        run_console_demo()
