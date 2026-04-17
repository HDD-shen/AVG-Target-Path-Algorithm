"""
Pygame可视化演示界面 - 简洁稳定版
"""

import pygame
import sys
import time
from typing import Dict, List

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (64, 64, 64)
BLUE = (70, 130, 180)

AGV_COLORS = [
    (255, 0, 0),
    (0, 0, 255),
    (0, 200, 0),
    (200, 0, 200),
    (255, 165, 0),
    (0, 255, 255),
]


class Visualizer:
    def __init__(self, env, cell_size: int = 40):
        pygame.init()
        
        self.env = env
        self.cell_size = cell_size
        
        self.width = env.cols * cell_size + 200
        self.height = max(env.rows * cell_size + 120, 500)
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AGV Path Planning")
        
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        
        self.running = True
        self.paused = True
        self.solution = None
        self.current_time = 0
        self.max_time = 0
        
        self.speed = 5
        self.last_update = time.time()
        
        self.agent_objs = []
        self.create_buttons()
    
    def create_buttons(self):
        self.buttons = []
        bx = self.env.cols * self.cell_size + 20
        
        self.buttons.append({'rect': pygame.Rect(bx, 60, 70, 30), 'text': 'Play/Pause', 'action': 'play'})
        self.buttons.append({'rect': pygame.Rect(bx, 100, 70, 30), 'text': 'Step', 'action': 'step'})
        self.buttons.append({'rect': pygame.Rect(bx, 140, 70, 30), 'text': 'Reset', 'action': 'reset'})
        self.buttons.append({'rect': pygame.Rect(bx + 80, 60, 50, 30), 'text': 'Faster', 'action': 'fast'})
        self.buttons.append({'rect': pygame.Rect(bx + 80, 100, 50, 30), 'text': 'Slower', 'action': 'slow'})
    
    def set_solution(self, solution: Dict):
        self.solution = solution
        self.current_time = 0
        
        self.max_time = 0
        for name in solution:
            self.max_time = max(self.max_time, len(solution[name]))
        
        self.agent_objs = []
        for i, agent in enumerate(self.env.agents):
            if agent.name in solution:
                color = tuple(agent.color) if agent.color else AGV_COLORS[i % len(AGV_COLORS)]
                self.agent_objs.append({
                    'agent': agent,
                    'path': solution[agent.name],
                    'color': color
                })
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for btn in self.buttons:
                    if btn['rect'].collidepoint(pos):
                        self.click_button(btn['action'])
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.click_button('play')
                elif event.key == pygame.K_RIGHT:
                    self.click_button('step')
                elif event.key == pygame.K_r:
                    self.click_button('reset')
    
    def click_button(self, action):
        if action == 'play':
            if self.solution:
                self.paused = not self.paused
                if not self.paused:
                    self.last_update = time.time()
        elif action == 'step':
            if self.solution and self.current_time < self.max_time - 1:
                self.current_time += 1
        elif action == 'reset':
            self.current_time = 0
            self.paused = True
        elif action == 'fast':
            self.speed = min(self.speed + 2, 20)
        elif action == 'slow':
            self.speed = max(self.speed - 2, 1)
    
    def update(self):
        if not self.paused and self.solution:
            now = time.time()
            if now - self.last_update >= 1.0 / self.speed:
                if self.current_time < self.max_time - 1:
                    self.current_time += 1
                else:
                    self.paused = True
                self.last_update = now
    
    def draw(self):
        self.screen.fill(WHITE)
        
        self.draw_title()
        self.draw_grid()
        self.draw_agents()
        self.draw_buttons()
        self.draw_info()
        
        pygame.display.flip()
    
    def draw_title(self):
        title = self.font.render("AGV Path Planning Demo", True, DARK_GRAY)
        self.screen.blit(title, (20, 20))
    
    def draw_grid(self):
        cs = self.cell_size
        
        pygame.draw.rect(self.screen, LIGHT_GRAY, (15, 55, self.env.cols * cs + 10, self.env.rows * cs + 10), 1)
        
        for i in range(self.env.cols + 1):
            pygame.draw.line(self.screen, GRAY, (20 + i * cs, 60), (20 + i * cs, 60 + self.env.rows * cs), 1)
        
        for j in range(self.env.rows + 1):
            pygame.draw.line(self.screen, GRAY, (20, 60 + j * cs), (20 + self.env.cols * cs, 60 + j * cs), 1)
        
        for obs in self.env.obstacles:
            x, y = obs
            rect = (20 + x * cs + 2, 60 + y * cs + 2, cs - 4, cs - 4)
            pygame.draw.rect(self.screen, DARK_GRAY, rect)
    
    def draw_agents(self):
        if not self.solution:
            return
        
        cs = self.cell_size
        
        for obj in self.agent_objs:
            path = obj['path']
            color = obj['color']
            agent = obj['agent']
            
            for i in range(len(path) - 1):
                if i > self.current_time:
                    break
                p1, p2 = path[i], path[i + 1]
                x1 = 20 + p1['x'] * cs + cs // 2
                y1 = 60 + p1['y'] * cs + cs // 2
                x2 = 20 + p2['x'] * cs + cs // 2
                y2 = 60 + p2['y'] * cs + cs // 2
                pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)
            
            sx = 20 + agent.start[0] * cs + cs // 2
            sy = 60 + agent.start[1] * cs + cs // 2
            pygame.draw.circle(self.screen, color, (sx, sy), cs // 4, 1)
            
            gx = 20 + agent.goal[0] * cs + 4
            gy = 60 + agent.goal[1] * cs + 4
            pygame.draw.rect(self.screen, color, (gx, gy, cs - 8, cs - 8), 1)
        
        for obj in self.agent_objs:
            path = obj['path']
            color = obj['color']
            
            if self.current_time < len(path):
                pos = path[self.current_time]
            else:
                pos = path[-1]
            
            cx = 20 + pos['x'] * cs + cs // 2
            cy = 60 + pos['y'] * cs + cs // 2
            
            pygame.draw.circle(self.screen, color, (cx, cy), cs // 3)
            
            name = self.small_font.render(obj['agent'].name.replace('agent', 'A'), True, WHITE)
            rect = name.get_rect(center=(cx, cy))
            self.screen.blit(name, rect)
    
    def draw_buttons(self):
        for btn in self.buttons:
            pygame.draw.rect(self.screen, BLUE, btn['rect'])
            text = self.small_font.render(btn['text'], True, WHITE)
            rect = text.get_rect(center=btn['rect'].center)
            self.screen.blit(text, rect)
    
    def draw_info(self):
        y = self.env.rows * self.cell_size + 80
        
        info = [
            f"Time: {self.current_time} / {max(0, self.max_time - 1)}",
            f"Speed: {self.speed} steps/s",
            f"Agents: {len(self.agent_objs)}",
        ]
        
        for i, text in enumerate(info):
            surf = self.small_font.render(text, True, BLACK)
            self.screen.blit(surf, (20, y + i * 20))
        
        status = "RUNNING" if not self.paused else "PAUSED"
        color = (0, 180, 0) if not self.paused else (200, 100, 0)
        status_surf = self.font.render(status, True, color)
        self.screen.blit(status_surf, (self.env.cols * self.cell_size + 20, 20))
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.time.wait(16)
        
        pygame.quit()
        sys.exit()


def create_demo(env, solution):
    vis = Visualizer(env)
    vis.set_solution(solution)
    return vis
