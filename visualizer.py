"""
Pygame可视化演示界面 - 美化版
"""

import pygame
import sys
import time
from typing import Dict, List, Optional

# 颜色定义 - 现代配色方案
COLORS = {
    'bg': (240, 244, 248),
    'bg_dark': (30, 30, 40),
    'panel': (255, 255, 255),
    'grid': (200, 200, 210),
    'grid_line': (180, 180, 190),
    'wall': (60, 60, 70),
    'text': (30, 30, 40),
    'text_light': (255, 255, 255),
    'button': (70, 130, 180),
    'button_hover': (100, 160, 210),
    'button_pressed': (50, 100, 150),
    'success': (46, 204, 113),
    'warning': (241, 196, 15),
}

TERRAIN_COLORS = {
    'flat': (255, 255, 255),
    'grass': (152, 251, 152),
    'sand': (244, 224, 159),
    'water': (135, 206, 250),
    'road': (180, 180, 180),
    'mud': (181, 137, 96),
    'mountain': (139, 119, 101),
}

AGV_COLORS = [
    (231, 76, 60),
    (52, 152, 219),
    (46, 204, 113),
    (155, 89, 182),
    (230, 126, 34),
    (26, 188, 156),
    (241, 196, 15),
    (149, 165, 166),
]


class Visualizer:
    """可视化演示类 - 美化版"""
    
    def __init__(self, env, cell_size: int = 45):
        self.env = env
        self.cell_size = cell_size
        
        self.width = env.cols * cell_size + 280
        self.height = max(env.rows * cell_size + 180, 650)
        
        pygame.init()
        pygame.display.set_caption("AGV多智能体路径规划系统")
        
        icon = pygame.Surface((32, 32))
        icon.fill(COLORS['button'])
        pygame.display.set_icon(icon)
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        self.font = pygame.font.SysFont('simhei', 14)
        self.font_bold = pygame.font.SysFont('simhei', 16, bold=True)
        self.title_font = pygame.font.SysFont('simhei', 24, bold=True)
        self.info_font = pygame.font.SysFont('simhei', 12)
        
        self.running = True
        self.paused = True
        self.solution = None
        self.current_time = 0
        self.max_time = 0
        
        self.speed = 8
        self.last_update_time = 0
        
        self.agent_objs = []
        self.buttons = []
        self.create_buttons()
        
        self.animation_offset = 0
    
    def create_buttons(self):
        panel_x = self.env.cols * self.cell_size + 20
        
        button_configs = [
            {'y': 80, 'text': '播放/暂停', 'action': 'run_pause', 'key': 'SPACE'},
            {'y': 130, 'text': '单步前进', 'action': 'step', 'key': 'RIGHT'},
            {'y': 180, 'text': '重新开始', 'action': 'reset', 'key': 'R'},
            {'y': 240, 'text': '加速 +', 'action': 'speed_up', 'key': 'UP'},
            {'y': 280, 'text': '减速 -', 'action': 'speed_down', 'key': 'DOWN'},
        ]
        
        for cfg in button_configs:
            self.buttons.append({
                'rect': pygame.Rect(panel_x, cfg['y'], 120, 36),
                'text': cfg['text'],
                'sub': f'[{cfg["key"]}]',
                'action': cfg['action']
            })
    
    def set_solution(self, solution: Dict[str, List[Dict]]):
        self.solution = solution
        self.current_time = 0
        
        self.max_time = 0
        for agent_name in solution:
            self.max_time = max(self.max_time, len(solution[agent_name]))
        
        self.agent_objs = []
        for i, agent in enumerate(self.env.agents):
            if agent.name in solution:
                path = solution[agent.name]
                color = tuple(agent.color) if agent.color else AGV_COLORS[i % len(AGV_COLORS)]
                agent_obj = {
                    'agent': agent,
                    'path': path,
                    'color': color,
                    'start_pos': tuple(agent.start),
                    'goal_pos': tuple(agent.goal),
                }
                self.agent_objs.append(agent_obj)
        
        self.paused = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
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
                elif event.key == pygame.K_UP:
                    self.handle_button_click('speed_up')
                elif event.key == pygame.K_DOWN:
                    self.handle_button_click('speed_down')
    
    def handle_button_click(self, action: str):
        if action == 'run_pause':
            if self.solution is None:
                return
            self.paused = not self.paused
            if not self.paused:
                self.last_update_time = time.time()
        
        elif action == 'step':
            if self.solution is None or self.current_time >= self.max_time - 1:
                return
            self.current_time += 1
        
        elif action == 'reset':
            self.current_time = 0
            self.paused = True
        
        elif action == 'speed_up':
            self.speed = min(self.speed + 2, 30)
        
        elif action == 'speed_down':
            self.speed = max(self.speed - 2, 1)
    
    def update(self):
        if not self.paused and self.solution:
            current_time = time.time()
            interval = 1.0 / self.speed
            
            if current_time - self.last_update_time >= interval:
                if self.current_time < self.max_time - 1:
                    self.current_time += 1
                else:
                    self.paused = True
                self.last_update_time = current_time
    
    def draw(self):
        self.screen.fill(COLORS['bg'])
        
        self.draw_title_bar()
        self.draw_map_panel()
        self.draw_side_panel()
        
        pygame.display.flip()
    
    def draw_title_bar(self):
        pygame.draw.rect(self.screen, COLORS['bg_dark'], (0, 0, self.width, 50))
        
        title = self.title_font.render("AGV 多智能体路径规划系统", True, COLORS['text_light'])
        self.screen.blit(title, (20, 12))
        
        status = "运行中" if not self.paused else "已暂停"
        status_color = COLORS['success'] if not self.paused else COLORS['warning']
        status_text = self.font_bold.render(status, True, status_color)
        self.screen.blit(status_text, (self.width - 120, 15))
    
    def draw_map_panel(self):
        map_bg = pygame.Rect(15, 60, self.env.cols * self.cell_size + 10, self.env.rows * self.cell_size + 10)
        pygame.draw.rect(self.screen, COLORS['panel'], map_bg, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['grid_line'], map_bg, 2, border_radius=8)
        
        offset_x, offset_y = 20, 65
        
        for y in range(self.env.rows):
            for x in range(self.env.cols):
                rect = pygame.Rect(
                    offset_x + x * self.cell_size,
                    offset_y + y * self.cell_size,
                    self.cell_size - 1,
                    self.cell_size - 1
                )
                
                terrain_cost = self.env.get_terrain_cost(x, y)
                if [x, y] in self.env.obstacles:
                    pygame.draw.rect(self.screen, COLORS['wall'], rect, border_radius=4)
                else:
                    color = (255, 255, 255)
                    if hasattr(self.env, 'grid') and self.env.grid:
                        cell = self.env.grid[x][y]
                        if hasattr(cell, 'terrain_type'):
                            color = TERRAIN_COLORS.get(cell.terrain_type, (255, 255, 255))
                    pygame.draw.rect(self.screen, color, rect, border_radius=2)
                    pygame.draw.rect(self.screen, COLORS['grid'], rect, 1, border_radius=2)
        
        self.draw_paths(offset_x, offset_y)
        self.draw_agents(offset_x, offset_y)
        self.draw_start_goal_markers(offset_x, offset_y)
    
    def draw_paths(self, offset_x, offset_y):
        if not self.solution:
            return
        
        for agent_obj in self.agent_objs:
            path = agent_obj['path']
            color = agent_obj['color']
            
            points = []
            for i, p in enumerate(path[:self.current_time + 1]):
                px = offset_x + p['x'] * self.cell_size + self.cell_size // 2
                py = offset_y + p['y'] * self.cell_size + self.cell_size // 2
                points.append((px, py))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, (*color, 100), False, points, 3)
    
    def draw_start_goal_markers(self, offset_x, offset_y):
        for agent_obj in self.agent_objs:
            color = agent_obj['color']
            start = agent_obj['start_pos']
            goal = agent_obj['goal_pos']
            
            sx = offset_x + start[0] * self.cell_size + self.cell_size // 2
            sy = offset_y + start[1] * self.cell_size + self.cell_size // 2
            pygame.draw.circle(self.screen, (*color, 80), (sx, sy), self.cell_size // 2 + 4, 2)
            
            gx = offset_x + goal[0] * self.cell_size + 5
            gy = offset_y + goal[1] * self.cell_size + 5
            goal_rect = pygame.Rect(gx, gy, self.cell_size - 10, self.cell_size - 10)
            pygame.draw.rect(self.screen, (*color, 150), goal_rect, 2, border_radius=4)
            
            start_label = self.info_font.render("S", True, color)
            goal_label = self.info_font.render("G", True, color)
            self.screen.blit(start_label, (sx - 4, sy - 6))
            self.screen.blit(goal_label, (gx + 5, gy + 3))
    
    def draw_agents(self, offset_x, offset_y):
        if not self.solution:
            return
        
        for agent_obj in self.agent_objs:
            path = agent_obj['path']
            color = agent_obj['color']
            
            if self.current_time < len(path):
                pos = path[self.current_time]
            else:
                pos = path[-1]
            
            cx = offset_x + pos['x'] * self.cell_size + self.cell_size // 2
            cy = offset_y + pos['y'] * self.cell_size + self.cell_size // 2
            
            pygame.draw.circle(self.screen, (*color, 50), (cx, cy), self.cell_size // 2 + 2)
            pygame.draw.circle(self.screen, color, (cx, cy), self.cell_size // 3, border_radius=4)
            
            name = agent_obj['agent'].name.replace('agent', 'AGV')
            name_text = self.font.render(name, True, COLORS['text_light'])
            text_rect = name_text.get_rect(center=(cx, cy))
            self.screen.blit(name_text, text_rect)
    
    def draw_side_panel(self):
        panel_x = self.env.cols * self.cell_size + 15
        
        panel = pygame.Rect(panel_x, 60, 250, self.height - 70)
        pygame.draw.rect(self.screen, COLORS['panel'], panel, border_radius=8)
        
        self.draw_buttons(panel_x)
        self.draw_info_panel(panel_x)
        self.draw_legend(panel_x)
    
    def draw_buttons(self, panel_x):
        mouse_pos = pygame.mouse.get_pos()
        
        for btn in self.buttons:
            is_hovered = btn['rect'].collidepoint(mouse_pos)
            
            if is_hovered:
                color = COLORS['button_hover']
            else:
                color = COLORS['button']
            
            pygame.draw.rect(self.screen, color, btn['rect'], border_radius=6)
            
            text = self.font_bold.render(btn['text'], True, COLORS['text_light'])
            text_rect = text.get_rect(center=(btn['rect'].centerx, btn['rect'].centery - 6))
            self.screen.blit(text, text_rect)
            
            sub = self.info_font.render(btn['sub'], True, (*COLORS['text_light'], 180))
            sub_rect = sub.get_rect(center=(btn['rect'].centerx, btn['rect'].centery + 10))
            self.screen.blit(sub, sub_rect)
    
    def draw_info_panel(self, panel_x):
        y = 340
        
        title = self.font_bold.render("状态信息", True, COLORS['text'])
        self.screen.blit(title, (panel_x + 20, y))
        
        y += 35
        
        info_items = [
            ("时间步", f"{self.current_time} / {max(0, self.max_time - 1)}"),
            ("运行速度", f"{self.speed} 步/秒"),
            ("AGV数量", str(len(self.agent_objs))),
            ("地图大小", f"{self.env.cols} x {self.env.rows}"),
        ]
        
        for label, value in info_items:
            label_text = self.font.render(label + ":", True, COLORS['text'])
            value_text = self.font_bold.render(str(value), True, COLORS['button'])
            
            self.screen.blit(label_text, (panel_x + 20, y))
            self.screen.blit(value_text, (panel_x + 100, y))
            y += 28
        
        if self.solution:
            total_cost = sum(len(p) for p in self.solution.values())
            y += 10
            cost_text = self.font.render("总代价:", True, COLORS['text'])
            cost_value = self.font_bold.render(str(total_cost), True, COLORS['success'])
            self.screen.blit(cost_text, (panel_x + 20, y))
            self.screen.blit(cost_value, (panel_x + 100, y))
    
    def draw_legend(self, panel_x):
        y = 490
        
        title = self.font_bold.render("图例", True, COLORS['text'])
        self.screen.blit(title, (panel_x + 20, y))
        
        y += 30
        
        legend_items = [
            ("起点", None, True),
            ("终点", None, False),
            ("障碍物", COLORS['wall'], None),
            ("草地", TERRAIN_COLORS['grass'], None),
            ("沙地", TERRAIN_COLORS['sand'], None),
            ("道路", TERRAIN_COLORS['road'], None),
        ]
        
        for label, color, marker_type in legend_items:
            if marker_type is not None:
                cx = panel_x + 25 + 8
                cy = y + 8
                if marker_type:
                    pygame.draw.circle(self.screen, (100, 100, 100), (cx, cy), 6, 1)
                else:
                    pygame.draw.rect(self.screen, (100, 100, 100), (cx - 5, cy - 5, 10, 10), 1)
            elif color:
                pygame.draw.rect(self.screen, color, (panel_x + 20, y, 16, 16), border_radius=2)
            
            text = self.info_font.render(label, True, COLORS['text'])
            self.screen.blit(text, (panel_x + 45, y + 2))
            y += 22
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()


def create_demo(env, solution):
    vis = Visualizer(env)
    vis.set_solution(solution)
    return vis
