# Dynamic Obstacles
import math
import numpy as np
from src.utils import WIDTH, HEIGHT
import pygame

class DynamicObstacle:
    def __init__(self, x, y, radius, move_x, move_y, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.start_pos = (x, y)
        self.move_range = (move_x, move_y)
        self.speed = speed
        self.phase = np.random.uniform(0, 2 * math.pi)

    def update(self):
        self.phase += self.speed
        self.x = self.start_pos[0] + math.sin(self.phase)*self.move_range[0]
        self.y = self.start_pos[1] + math.cos(self.phase)*self.move_range[1]

    def get_pos(self):
        return self.x, self.y

# Create S maze (Environment1)
def createSmaze():
    goal = (720, 505)
    reward_zone = pygame.Rect(200, 430, 580, 150)
    walls = []
    # Borders
    for x in range(0, WIDTH, 20):
        walls.append((x, 10)); walls.append((x, HEIGHT-10))
    for y in range(0, HEIGHT, 20):
        walls.append((10, y)); walls.append((WIDTH-10, y))
    # S-Maze Interior
    for x in range(10, 520, 20): walls.append((x, 220))
    for x in range(270, WIDTH-10, 20): walls.append((x, 420))

    dynamic_obstacles = []
    return walls, dynamic_obstacles, goal, reward_zone

# Create empty Maze (Environment2)
def createDynamicMaze():
    goal = (720, 300)
    reward_zone = pygame.Rect(630, 230, 150, 150)
    walls = []
    for x in range(0, WIDTH, 20):
        walls.append((x, 10)); walls.append((x, HEIGHT-10))
    for y in range(0, HEIGHT, 20):
        walls.append((10, y)); walls.append((WIDTH-10, y))
    
    dynamic_obstacles = [
    DynamicObstacle(400, 80, 15, 60, 0, 0.04),
    DynamicObstacle(400, 520, 15, 60, 0, 0.04),
    DynamicObstacle(200, 250, 15, 60, 0, 0.04),
    DynamicObstacle(700, 180, 15, 60, 0, 0.04),
    DynamicObstacle(560, 300, 20, 0, 120, 0.03)
    ]
    
    return walls, dynamic_obstacles, goal, reward_zone


# Zig Zag maze (Environment3)
def createComplexMaze():
    reward_zone = pygame.Rect(610, 20, 170, 550)
    goal = (720, 80)
    walls = []
    for x in range(0, WIDTH, 20):
        walls.append((x, 10))
        walls.append((x, HEIGHT-10))
    for y in range(0, HEIGHT, 20):
        walls.append((10, y))
        walls.append((WIDTH-10, y))
    for y in range(10, 450, 20):
        walls.append((200, y))
    for y in range(150, HEIGHT-10, 20):
        walls.append((400, y))
    for y in range(10, 450, 20):
        walls.append((600, y))

    dynamic_obstacles = [
        DynamicObstacle(495, 350, 15, 60, 0, 0.03),
        DynamicObstacle(670, 470, 15, 80, 0, 0.03)
    ]

    return walls, dynamic_obstacles, goal, reward_zone



def create_maze(Environment=1):
    if (Environment==1):
        # Create S maze Environment
        return createSmaze()
    elif (Environment==2):
        # Create Simple Dynamic Environment
        return createDynamicMaze()
    else:
        # Create Complex Dynamic Environment
        return createComplexMaze()