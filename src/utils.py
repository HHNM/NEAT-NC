
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
AGENT_RADIUS = 10
GOAL_RADIUS = 20
SENSOR_RADIUS = 100
GRID_RES = 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)       # Dynamic Obstacles
BLUE = (50, 100, 255)     # Agent
GREEN = (50, 200, 50)     # Goal
GRAY = (180, 180, 180)    # Static Walls
YELLOW = (255, 200, 0)


def draw_best_path(screen, agent):
    #Draws the final trajectory of the winner.
    if len(agent.path_history) > 2:
        # Use pygame.draw.lines to connect all recorded points
        pygame.draw.lines(screen, (255, 165, 0), False, agent.path_history, 3)


def draw_hud(screen, inputs):
    """Draws the 3x3 mental map of the best agent."""
    grid_size = 20  # size of each cell in the HUD
    start_x, start_y = WIDTH - 150, 20
    
    # Extract grids from the flattened 'inputs' list
    # inputs[0:9] is Obstacles, inputs[9:18] is Goal
    obs_grid = inputs[0:9].reshape((3, 3))
    goal_grid = inputs[9:18].reshape((3, 3))

    # Label
    font = pygame.font.SysFont("Arial", 14, bold=True)
    screen.blit(font.render("Best Agent's Navigation Cells", True, BLACK), (start_x - 10, start_y + 60))

    for row in range(3):
        for col in range(3):
            # Draw Obstacle Grid (Red if active)
            obs_color = RED if obs_grid[row][col] > 0 else (220, 220, 220)
            pygame.draw.rect(screen, obs_color, (start_x + col*grid_size, start_y + row*grid_size, grid_size-2, grid_size-2))
            
            # Draw Goal Grid (Green if active)
            goal_color = GREEN if goal_grid[row][col] > 0 else (220, 220, 220)
            pygame.draw.rect(screen, goal_color, (start_x + 80 + col*grid_size, start_y + row*grid_size, grid_size-2, grid_size-2))

    screen.blit(font.render("Border Cells", True, BLACK), (start_x, start_y - 18))
    screen.blit(font.render("Place Cells", True, BLACK), (start_x + 80, start_y - 18))

