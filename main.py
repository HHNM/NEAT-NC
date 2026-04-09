import pygame
import neat
import os
import time
import csv
from src.utils import *
from src.environment import create_maze
from src.NEATNC import *


# NEAT Evaluation and Visualization
def eval_genomes(genomes, config):
    global best_agent_length, best_reached_goal

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    # Create Environment
    static_obstacles, dynamic_obstacles, goal, reward_zone = create_maze(Environment=1) # Choose Between Environment 1, 2 and 3

    epf = PlaceCells(SENSOR_RADIUS, GRID_RES)

    for _, genome in genomes:
        genome.fitness = 0.0

    agents = [Agent(80, 100) for _ in genomes]
    nets = [neat.nn.RecurrentNetwork.create(g, config) for _, g in genomes]

    best_idx = 0
    max_fit = -999
    best_agent = None
    for step in range(1000):
        clock.tick(FPS)
        screen.fill(WHITE)
        for dyn in dynamic_obstacles:
            dyn.update()  
        # Draw goal
        pygame.draw.circle(screen, GREEN, goal, GOAL_RADIUS)
        # Draw static obstacles
        SQUARE_SIZE = 20
        for obs in static_obstacles:
            rect = pygame.Rect(
                obs[0] - SQUARE_SIZE // 2,
                obs[1] - SQUARE_SIZE // 2,
                SQUARE_SIZE,
                SQUARE_SIZE
            )
            pygame.draw.rect(screen, GRAY, rect)
        
        # Draw dynamic obstacles
        for dyn in dynamic_obstacles:
            dx, dy = dyn.get_pos()
            pygame.draw.circle(screen, RED, (int(dx), int(dy)), dyn.radius)

        # Update all agents
        for i, agent in enumerate(agents):
            if agent.alive and not agent.reached_goal:

                old_x, old_y = agent.x, agent.y

                active_found = True

                inputs = epf.get_inputs(agent, goal, static_obstacles, dynamic_obstacles)
                outputs = nets[i].activate(inputs)
                
                
                agent.move(outputs[0], outputs[1])
                agent.check_collision(static_obstacles, dynamic_obstacles, goal)

                # Get the vector from the agent to the goal
                dx_goal = goal[0] - old_x
                dy_goal = goal[1] - old_y
                dist_to_goal = math.hypot(dx_goal, dy_goal)
                # Fitness Accumulation
                if dist_to_goal > 0:
                    # Normalize goal vector (unit vector)
                    u_goal_x = dx_goal / dist_to_goal
                    u_goal_y = dy_goal / dist_to_goal

                    # Get the actual movement vector (displacement)
                    move_x = agent.x - old_x
                    move_y = agent.y - old_y

                    # Projections of movement onto goal direction
                    directional_progress = (move_x * u_goal_x) + (move_y * u_goal_y)
                    

                    genomes[i][1].fitness += directional_progress

                pygame.draw.rect(screen, (0, 255, 0), reward_zone, 2) # 2px green border
                
                agent_rect = pygame.Rect(agent.x - 5, agent.y - 5, 10, 10)
                if reward_zone.colliderect(agent_rect):
                    # The agent is physically inside the target zone
                    genomes[i][1].fitness += 10
                # Normalize it so it doesn't overwhelm the goal bonus
                genomes[i][1].fitness -= 0.05 * abs(outputs[0])
                if agent.reached_goal:
                    genomes[i][1].fitness += 5000 + 5 * (1000 - step)
                elif not agent.alive:
                    genomes[i][1].fitness -= 100

            # Update best agent for HUD
            if genomes[i][1].fitness > max_fit:
                max_fit = genomes[i][1].fitness
                best_idx = i
                best_agent = agents[i]

            # Draw all agents
            if agent.alive:
                color = BLUE if not agent.reached_goal else YELLOW
                pygame.draw.circle(screen, color, (int(agent.x), int(agent.y)), AGENT_RADIUS)
                # Draw simple heading line
                hx = agent.x + math.cos(agent.angle) * 15
                hy = agent.y + math.sin(agent.angle) * 15
                pygame.draw.line(screen, BLACK, (agent.x, agent.y), (hx, hy), 2)

        # Draw the Navigation Cells HUD of the best performing agent
        if active_found:
            best_inputs = epf.get_inputs(agents[best_idx], goal, static_obstacles, dynamic_obstacles)
            draw_hud(screen, best_inputs)
        
        if not active_found: break
        # Display step
        text = font.render(f"Step: {step}", True, BLACK)
        screen.blit(text, (10, 10))

        pygame.display.flip()

        # Exit if all dead or goal reached
        if all(a.reached_goal or not a.alive for a in agents):
            break
    
    # Draw the best path for the final frame/screenshot
    if best_agent:
        draw_best_path(screen, best_agent)
        best_agent_length = calculate_path_length(best_agent.path_history)
        print(f"Generation Winner Path Length: {best_agent_length:.2f} pixels")
        # Success flag
        best_reached_goal = 1 if best_agent.reached_goal else 0
        pygame.display.flip()
        pygame.time.delay(2000) # Pause so you can see the path
       
    pygame.quit()

if __name__ == "__main__":

    RUNS = 30
    GENERATIONS = 10

    config_path = os.path.join(os.path.dirname(__file__), "config/config-neatPC.txt")

    local_dir = os.path.dirname(__file__)
    results_file = os.path.join(local_dir, "data/neatNC_results.csv")

    # CSV header
    with open(results_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "run_id",
            "execution_time_sec",
            "best_fitness",
            "path_length",
            "success"
        ])
        
    for run in range(RUNS):

        print(f"\n==============================")
        print(f"RUN {run+1}/{RUNS}")
        print(f"==============================")

        start_time = time.time()

        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )

        p = neat.Population(config)
        p.add_reporter(neat.StdOutReporter(False))

        winner = p.run(eval_genomes, GENERATIONS)

        execution_time = time.time() - start_time

        best_fitness = winner.fitness

        # Save results
        with open(results_file, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                run + 1,
                round(execution_time, 3),
                round(best_fitness, 3),
                round(best_agent_length, 3),
                best_reached_goal
            ])

        print(f"==Run {run+1} finished")
        print(f"  Time: {execution_time:.2f}s")
        print(f"  Fitness: {best_fitness:.2f}")
        print(f"  Path length: {best_agent_length:.2f}")
        print(f"  Success: {best_reached_goal}")

        