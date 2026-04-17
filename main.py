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
from core.cbs import CBS, CBSV2
from maps import get_map, generate_random_map


def create_environment(map_config: dict) -> Environment:
    """从配置创建环境"""
    dimension = map_config['dimension']
    obstacles = map_config.get('obstacles', [])
    wall_ratio = map_config.get('wallRatio', -1)
    
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
    
    env = Environment(dimension, agents, wall_ratio, obstacles)
    return env


def run_algorithm(env: Environment, algorithm: str = 'cbs') -> Dict:
    """运行路径规划算法"""
    print(f"\n{'='*50}")
    print(f"开始运行 {algorithm.upper()} 算法...")
    print(f"地图尺寸: {env.cols} x {env.rows}")
    print(f"智能体数量: {len(env.agents)}")
    print(f"障碍物数量: {len(env.obstacles)}")
    print(f"{'='*50}\n")
    
    start_time = time.time()
    
    if algorithm == 'cbs':
        cbs = CBS(env)
        solution = cbs.search()
    elif algorithm == 'cbs_v2':
        cbs = CBSV2(env)
        solution = cbs.search()
    else:
        print(f"未知算法: {algorithm}")
        return {}
    
    end_time = time.time()
    
    print(f"\n{'='*50}")
    print(f"算法运行完成！")
    print(f"总耗时: {end_time - start_time:.3f} 秒")
    print(f"解决方案: {solution}")
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
    print("6. 自定义随机地图")
    print("0. 退出")
    
    choice = input("\n请选择 (0-6): ")
    
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
    
    # 选择算法
    print("\n请选择算法:")
    print("1. CBS (原始版本)")
    print("2. CBS_v2 (改进版本)")
    alg_choice = input("请选择 (1-2): ")
    algorithm = 'cbs_v2' if alg_choice == '2' else 'cbs'
    
    # 运行算法
    solution = run_algorithm(env, algorithm)
    
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
    solution = run_algorithm(env, 'cbs')
    
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
