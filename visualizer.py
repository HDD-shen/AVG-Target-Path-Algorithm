"""
Pygame可视化演示界面
"""

import pygame
import sys
import time
from typing import Dict, List, Optional

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128,128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (51, 51, 51)

# AGV颜色
AGV_COLORS = [
    (255, 0, 0),     # 红色
    (0, 255, 0),     # 绿色
    (0, 0, 255),     # 蓝色
    (255, 255, 0),   # 黄色
    (255, 0, 255),   # 紫色
    (0, 255, 255),   # 青色
    (255, 128, 0),   # 橙色
    (128, 0, 255),   # 紫罗兰
]


class Visualizer:
    """可视化演示类"""
    
    def __init__(self, env, cell_size: int = 40):
        """
        初始化可视化器
        :param env: 环境对象
        :param cell_size: 单元格大小
        """
        self.env = env
        self.cell_size = cell_size
        
        # 计算画布大小
        self.width = env.cols * cell_size + 200  # 额外空间用于UI
        self.height = env.rows * cell_size + 150
        
        # 初始化Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("多AGV路径规划演示系统")
        
        # 字体
        self.font = pygame.font.SysFont('microsoftyahei', 14)
        self.title_font = pygame.font.SysFont('microsoftyahei', 20, bold=True)
        
        # 状态
        self.running = True
        self.paused = True
        self.solution = None
        self.current_time = 0
        self.max_time = 0
        
        # 速度控制
        self.speed = 10  # 步/秒
        self.last_update_time = 0
        
        # AGV对象
        self.agent_objs = []
        
        # 按钮
        self.buttons = []
        self.create_buttons()
    
    def create_buttons(self):
        """创建按钮"""
        btn_x = self.env.cols * self.cell_size + 20
        btn_y = 30
        
        # 运行/暂停按钮
        self.buttons.append({
            'rect': pygame.Rect(btn_x, btn_y, 80, 30),
            'text': '运行',
            'action': 'run_pause'
        })
        
        # 单步按钮
        self.buttons.append({
            'rect': pygame.Rect(btn_x, btn_y + 40, 80, 30),
            'text': '单步',
            'action': 'step'
        })
        
        # 重置按钮
        self.buttons.append({
            'rect': pygame.Rect(btn_x, btn_y + 80, 80, 30),
            'text': '重置',
            'action': 'reset'
        })
        
        # 加速按钮
        self.buttons.append({
            'rect': pygame.Rect(btn_x, btn_y + 130, 80, 30),
            'text': '加速',
            'action': 'speed_up'
        })
        
        # 减速按钮
        self.buttons.append({
            'rect': pygame.Rect(btn_x + 90, btn_y + 130, 80, 30),
            'text': '减速',
            'action': 'speed_down'
        })
    
    def set_solution(self, solution: Dict[str, List[Dict]]):
        """设置解决方案"""
        self.solution = solution
        self.current_time = 0
        
        # 计算最大时间
        self.max_time = 0
        for agent_name in solution:
            self.max_time = max(self.max_time, len(solution[agent_name]))
        
        # 为每个智能体创建对象
        self.agent_objs = []
        for agent in self.env.agents:
            if agent.name in solution:
                path = solution[agent.name]
                agent_obj = {
                    'agent': agent,
                    'path': path,
                    'color': tuple(agent.color) if agent.color else AGV_COLORS[len(self.agent_objs) % len(AGV_COLORS)]
                }
                self.agent_objs.append(agent_obj)
        
        print(f"解决方案设置完成，最大时间步: {self.max_time}")
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查按钮点击
                mouse_pos = event.pos
                for btn in self.buttons:
                    if btn['rect'].collidepoint(mouse_pos):
                        self.handle_button_click(btn['action'])
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.handle_button_click('run_pause')
                elif event.key == pygame.K_RIGHT:
                    self.handle_button_click('step')
                elif event.key == pygame.K_r:
                    self.handle_button_click('reset')
    
    def handle_button_click(self, action: str):
        """处理按钮点击"""
        if action == 'run_pause':
            if self.solution is None:
                print("请先计算路径！")
                return
            self.paused = not self.paused
            if not self.paused:
                self.last_update_time = time.time()
        
        elif action == 'step':
            if self.solution is None:
                print("请先计算路径！")
                return
            if self.current_time < self.max_time - 1:
                self.current_time += 1
            else:
                print("已到达终点！")
        
        elif action == 'reset':
            self.current_time = 0
            self.paused = True
        
        elif action == 'speed_up':
            self.speed = min(self.speed + 5, 50)
        
        elif action == 'speed_down':
            self.speed = max(self.speed - 5, 1)
    
    def update(self):
        """更新状态"""
        if not self.paused and self.solution:
            current_time = time.time()
            interval = 1.0 / self.speed
            
            if current_time - self.last_update_time >= interval:
                if self.current_time < self.max_time - 1:
                    self.current_time += 1
                else:
                    self.paused = True
                    print("所有AGV已到达终点！")
                self.last_update_time = current_time
    
    def draw(self):
        """绘制画面"""
        self.screen.fill(WHITE)
        
        # 绘制标题
        title = self.title_font.render("多AGV路径规划演示系统", True, BLACK)
        self.screen.blit(title, (20, 5))
        
        # 绘制地图
        self.draw_grid()
        self.draw_agents()
        self.draw_buttons()
        self.draw_info()
        
        pygame.display.flip()
    
    def draw_grid(self):
        """绘制网格"""
        cell_size = self.cell_size
        
        # 绘制网格线
        pygame.draw.lines(self.screen, DARK_GRAY, True, 
                         [(0, 0), (self.env.cols * cell_size, 0),
                          (self.env.cols * cell_size, self.env.rows * cell_size),
                          (0, self.env.rows * cell_size)], 2)
        
        for i in range(self.env.cols + 1):
            pygame.draw.line(self.screen, DARK_GRAY, 
                           (i * cell_size, 0), (i * cell_size, self.env.rows * cell_size), 1)
        
        for j in range(self.env.rows + 1):
            pygame.draw.line(self.screen, DARK_GRAY,
                           (0, j * cell_size), (self.env.cols * cell_size, j * cell_size), 1)
        
        # 绘制障碍物
        for obs in self.env.obstacles:
            x, y = obs
            rect = pygame.Rect(x * cell_size + 2, y * cell_size + 2, 
                              cell_size - 4, cell_size - 4)
            pygame.draw.rect(self.screen, GRAY, rect)
    
    def draw_agents(self):
        """绘制智能体"""
        cell_size = self.cell_size
        
        # 绘制起点和终点
        for agent_obj in self.agent_objs:
            agent = agent_obj['agent']
            color = agent_obj['color']
            
            # 起点 - 圆形
            start_x = agent.start[0] * cell_size + cell_size // 2
            start_y = agent.start[1] * cell_size + cell_size // 2
            pygame.draw.circle(self.screen, color, (start_x, start_y), cell_size // 3, 2)
            
            # 终点 - 方框
            goal_rect = pygame.Rect(
                agent.goal[0] * cell_size + 4,
                agent.goal[1] * cell_size + 4,
                cell_size - 8, cell_size - 8
            )
            pygame.draw.rect(self.screen, color, goal_rect, 2)
        
        # 绘制当前位置
        if self.solution:
            for agent_obj in self.agent_objs:
                agent = agent_obj['agent']
                color = agent_obj['color']
                path = agent_obj['path']
                
                # 获取当前位置
                if self.current_time < len(path):
                    x, y = path[self.current_time]['x'], path[self.current_time]['y']
                else:
                    x, y = path[-1]['x'], path[-1]['y']
                
                # 绘制AGV（实心圆）
                center_x = x * cell_size + cell_size // 2
                center_y = y * cell_size + cell_size // 2
                pygame.draw.circle(self.screen, color, (center_x, center_y), cell_size // 3)
                
                # 绘制名称
                name_text = self.font.render(agent.name, True, WHITE)
                text_rect = name_text.get_rect(center=(center_x, center_y))
                self.screen.blit(name_text, text_rect)
    
    def draw_buttons(self):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        
        for btn in self.buttons:
            # 检查鼠标悬停
            is_hovered = btn['rect'].collidepoint(mouse_pos)
            color = LIGHT_GRAY if is_hovered else GRAY
            
            # 绘制按钮
            pygame.draw.rect(self.screen, color, btn['rect'])
            pygame.draw.rect(self.screen, DARK_GRAY, btn['rect'], 2)
            
            # 绘制文字
            text = self.font.render(btn['text'], True, BLACK)
            text_rect = text.get_rect(center=btn['rect'].center)
            self.screen.blit(text, text_rect)
    
    def draw_info(self):
        """绘制信息"""
        info_y = self.env.rows * self.cell_size + 10
        
        # 当前时间
        time_text = self.font.render(f"时间步: {self.current_time}/{self.max_time - 1}", True, BLACK)
        self.screen.blit(time_text, (20, info_y))
        
        # 状态
        status = "运行中" if not self.paused else "已暂停"
        status_text = self.font.render(f"状态: {status}", True, BLACK)
        self.screen.blit(status_text, (150, info_y))
        
        # 速度
        speed_text = self.font.render(f"速度: {self.speed} 步/秒", True, BLACK)
        self.screen.blit(speed_text, (280, info_y))
    
    def run(self):
        """主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            time.sleep(0.01)
        
        pygame.quit()
        sys.exit()


def create_demo(env, solution):
    """创建演示实例"""
    vis = Visualizer(env)
    vis.set_solution(solution)
    return vis
