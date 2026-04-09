
import numpy as np
import math

from src.utils import AGENT_RADIUS, GOAL_RADIUS, WIDTH, HEIGHT

best_agent_length = 0.0
best_reached_goal = 0 

# Place cells
class PlaceCells:
    def __init__(self, radius, grid_res):
        self.radius = radius
        self.grid_res = grid_res

    def get_inputs(self, agent, goal, static_obs, dynamic_obs):
        obs_grid = np.zeros((self.grid_res, self.grid_res))
        goal_grid = np.zeros((self.grid_res, self.grid_res))
        c, s = math.cos(-agent.angle), math.sin(-agent.angle)
        cell_size = (self.radius * 2) / self.grid_res
        def map_to_grid(px, py, grid, value=1.0):
            dx, dy = px - agent.x, py - agent.y
            dist = math.hypot(dx, dy)
            if dist > self.radius:
                return
            rx = dx * c - dy * s
            ry = dx * s + dy * c
            gx = int((rx + self.radius) / cell_size)
            gy = int((ry + self.radius) / cell_size)
            if 0 <= gx < self.grid_res and 0 <= gy < self.grid_res:
                grid[gy, gx] = max(grid[gy, gx], value)

        for ox, oy in static_obs:
            map_to_grid(ox, oy, obs_grid, 1.0)

        for dyn in dynamic_obs:
            dx, dy = dyn.get_pos()
            map_to_grid(dx, dy, obs_grid, 1.0)

        map_to_grid(goal[0], goal[1], goal_grid, 1.0)
        
        angle_to_goal = math.atan2(goal[1] - agent.y, goal[0] - agent.x)
        rel_angle = angle_to_goal - agent.angle
        head_dir = [math.sin(rel_angle), math.cos(rel_angle)]

        speed_cell = [agent.speed / 3.0]

        return np.concatenate([
            obs_grid.flatten(),    # 9
            goal_grid.flatten(),   # 9
            head_dir,              # 2
            speed_cell            # 1
        ])  # total 21 inputs


def calculate_path_length(path_history):
    if len(path_history) < 2:
        return 0.0
    
    total_dist = 0.0
    for i in range(1, len(path_history)):
        # Calculate distance between point (i-1) and point (i)
        p1 = path_history[i-1]
        p2 = path_history[i]
        total_dist += math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    
    return total_dist

def is_visible(start_pos, end_pos, static_obs):
    """Checks if there is a clear line between two points."""
    x1, y1 = start_pos
    x2, y2 = end_pos
    
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist < 10: return True # Close enough to see
    
    # Check points along the line every 10 pixels
    steps = int(dist / 10)
    for i in range(1, steps):
        # Calculate intermediate point
        curr_x = x1 + (x2 - x1) * (i / steps)
        curr_y = y1 + (y2 - y1) * (i / steps)
        
        # Check against all static obstacle points
        for ox, oy in static_obs:
            if math.hypot(curr_x - ox, curr_y - oy) < 15: # 15 is wall thickness
                return False
    return True



class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0.0
        self.speed = 0.0
        self.radius = AGENT_RADIUS
        self.alive = True
        self.reached_goal = False
        self.age = 0
        self.start_dist = 0.0
        self.path_history = [(x, y)]
        self.path_length = 0.0


    def move(self, steering, throttle):
        if not self.alive or self.reached_goal:
            return

        self.age += 1
        
        steering = np.clip(steering, -1, 1)
        throttle = np.clip(throttle, -1, 1)

        self.angle += steering * 0.12
        target_speed = np.clip((throttle + 1) / 2, 0.0, 1.0) * 3.0
        self.speed = 0.9 * self.speed + 0.1 * target_speed

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Record position
        self.path_history.append((self.x, self.y))
    
    def check_collision(self, static_obs, dynamic_obs, goal):
        if math.hypot(self.x - goal[0], self.y - goal[1]) < GOAL_RADIUS + self.radius:
            self.reached_goal = True
            return
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.alive = False
            return
        for ox, oy in static_obs:
            if math.hypot(self.x - ox, self.y - oy) < self.radius + 8:
                self.alive = False
                return
        
        for dyn in dynamic_obs:
            dx, dy = dyn.get_pos()
            if math.hypot(self.x - dx, self.y - dy) < self.radius + dyn.radius:
                self.alive = False
                return



