import os
from searching_framework import *
import pygame
import time
from collections import namedtuple

pygame.init()
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREY = (195, 180, 180)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 60
SPEED = 1.1

nodes_count = 0


def move_up(x, y, g_x, g_y, obstacles, grid):
    if y < grid[1] - 1 and (x, y + 1) not in obstacles and (x, y + 1) != (g_x, g_y):
        return x, y + 1, 'U'


def move_down(x, y, g_x, g_y, obstacles):
    if y > 0 and (x, y - 1) not in obstacles and (x, y - 1) != (g_x, g_y):
        return x, y - 1, 'D'


def move_left(x, y, g_x, g_y, obstacles):
    if x > 0 and (x - 1, y) not in obstacles and (x - 1, y) != (g_x, g_y):
        return x - 1, y, 'L'


def move_right(x, y, g_x, g_y, obstacles, grid):
    if x < grid[0] - 1 and (x + 1, y) not in obstacles and (x + 1, y) != (g_x, g_y):
        return x + 1, y, 'R'


def turn_left(x, y, direction, g_x, g_y, obstacles, grid):
    valid_result = (x, y, direction)

    if direction == 'R':
        valid_result = move_up(x, y, g_x, g_y, obstacles, grid)

    if direction == 'U':
        valid_result = move_left(x, y, g_x, g_y, obstacles)

    if direction == 'L':
        valid_result = move_down(x, y, g_x, g_y, obstacles)

    if direction == 'D':
        valid_result = move_right(x, y, g_x, g_y, obstacles, grid)

    return valid_result if valid_result is not None else (x, y, direction)


def turn_right(x, y, direction, g_x, g_y, obstacles, grid):
    valid_result = (x, y, direction)

    if direction == 'R':
        valid_result = move_down(x, y, g_x, g_y, obstacles)

    if direction == 'D':
        valid_result = move_left(x, y, g_x, g_y, obstacles)

    if direction == 'L':
        valid_result = move_up(x, y, g_x, g_y, obstacles, grid)

    if direction == 'U':
        valid_result = move_right(x, y, g_x, g_y, obstacles, grid)

    return valid_result if valid_result is not None else (x, y, direction)


def move_forward(x, y, direction, g_x, g_y, obstacles, grid):
    valid_result = (x, y, direction)

    if direction == 'R':
        valid_result = move_right(x, y, g_x, g_y, obstacles, grid)

    if direction == 'D':
        valid_result = move_down(x, y, g_x, g_y, obstacles)

    if direction == 'L':
        valid_result = move_left(x, y, g_x, g_y, obstacles)

    if direction == 'U':
        valid_result = move_up(x, y, g_x, g_y, obstacles, grid)

    return valid_result if valid_result is not None else (x, y, direction)


def validate_and_expand_ghost_move(x, y, grid, obstacles, fringe, explored):
    # up
    if y < grid[1] - 1 and (x, y + 1) not in obstacles and (x, y + 1) not in explored and (x, y + 1) not in fringe:
        fringe.append((x, y + 1))

    # down
    if y > 0 and (x, y - 1) not in obstacles and (x, y - 1) not in explored and (x, y - 1) not in fringe:
        fringe.append((x, y - 1))

    # left
    if x > 0 and (x - 1, y) not in obstacles and (x - 1, y) not in explored and (x - 1, y) not in fringe:
        fringe.append((x - 1, y))

    # right
    if x < grid[0] - 1 and (x + 1, y) not in obstacles and (x + 1, y) not in explored and (x + 1, y) not in fringe:
        fringe.append((x + 1, y))


def move_ghost(x, y, fringe, explored, obstacles, grid):
    explored_list = list(explored)
    fringe_fifo = list(fringe)

    # initial
    if not explored_list and not fringe_fifo:
        explored_list.append((x, y))
        validate_and_expand_ghost_move(x, y, grid, obstacles, fringe_fifo, explored_list)

    # end
    if explored_list and not fringe_fifo:
        return x, y, tuple(fringe_fifo), tuple(explored_list)

    node = fringe_fifo.pop(0)

    if node not in explored_list:
        explored_list.append(node)

        x = node[0]
        y = node[1]

        validate_and_expand_ghost_move(x, y, grid, obstacles, fringe_fifo, explored_list)

    return x, y, tuple(fringe_fifo), tuple(explored_list)


class Pacman(Problem):
    def value(self):
        pass

    def __init__(self, obstacles, grid, initial, goal=None):
        super().__init__(initial, goal=goal)
        self.obstacles = obstacles
        self.grid = grid

    def successor(self, state):

        # region :: evaluating variables
        global nodes_count
        nodes_count += 1
        # endregion

        successors = dict()

        pacman_x, pacman_y = state[0]
        pacman_dir = state[1]
        ghost_x, ghost_y = state[2]
        ghost_fringe = state[3]
        ghost_explored = state[4]

        # region :: Move ghost ---------------------------------------------------------------------------------------
        new_ghost_x, new_ghost_y, new_ghost_fringe, new_ghost_explored = move_ghost(ghost_x, ghost_y, ghost_fringe,
                                                                                    ghost_explored,
                                                                                    self.obstacles,
                                                                                    self.grid)
        # endregion --------------------------------------------------------------------------------------------------

        # region :: Stop Pacman --------------------------------------------------------------------------------------
        successors['Stop'] = (
            (pacman_x, pacman_y), pacman_dir, (new_ghost_x, new_ghost_y), new_ghost_fringe, new_ghost_explored)
        # endregion --------------------------------------------------------------------------------------------------

        # region :: Turn Pacman left & move --------------------------------------------------------------------------
        new_pacman_x, new_pacman_y, new_pacman_direction = turn_left(pacman_x, pacman_y, pacman_dir, new_ghost_x,
                                                                     new_ghost_y,
                                                                     self.obstacles, self.grid)

        if [pacman_x, pacman_y, pacman_dir] != [new_pacman_x, new_pacman_y, new_pacman_direction]:
            successors['TurnLeft'] = ((new_pacman_x, new_pacman_y), new_pacman_direction,
                                      (new_ghost_x, new_ghost_y), new_ghost_fringe, new_ghost_explored)
        # endregion --------------------------------------------------------------------------------------------------

        # region :: Turn Pacman right & move -------------------------------------------------------------------------
        new_pacman_x, new_pacman_y, new_pacman_direction = turn_right(pacman_x, pacman_y, pacman_dir, new_ghost_x,
                                                                      new_ghost_y,
                                                                      self.obstacles, self.grid)

        if [pacman_x, pacman_y, pacman_dir] != [new_pacman_x, new_pacman_y, new_pacman_direction]:
            successors['TurnRight'] = ((new_pacman_x, new_pacman_y), new_pacman_direction,
                                       (new_ghost_x, new_ghost_y), new_ghost_fringe, new_ghost_explored)
        # endregion --------------------------------------------------------------------------------------------------

        # region :: Move Pacman forward ------------------------------------------------------------------------------
        new_pacman_x, new_pacman_y, new_pacman_direction = move_forward(pacman_x, pacman_y, pacman_dir, new_ghost_x,
                                                                        new_ghost_y,
                                                                        self.obstacles,
                                                                        self.grid)

        if [pacman_x, pacman_y, pacman_dir] != [new_pacman_x, new_pacman_y, new_pacman_direction]:
            successors['MoveForward'] = ((new_pacman_x, new_pacman_y), new_pacman_direction,
                                         (new_ghost_x, new_ghost_y), new_ghost_fringe, new_ghost_explored)
        # endregion --------------------------------------------------------------------------------------------------

        return successors

    def actions(self, state):
        return self.successor(state).keys()

    def result(self, state, action):
        return self.successor(state)[action]

    def goal_test(self, state):
        p_x, p_y = state[0]  # pacman x, y coordinates
        t_x, t_y = self.goal  # treasure x, y coordinates

        return (p_x, p_y) == (t_x, t_y)

    def h(self, node):
        man_x, man_y = node.state[0]

        return abs(man_x - self.goal[0])


class PacmanTreasureVisual:

    def __init__(self, pacman_state, ghost_state, obs_list, grd_size, pacman_pos,
                 pacman_dir, ghost_pos, treasure_pos):
        self.w = grd_size[0] * BLOCK_SIZE
        self.h = grd_size[1] * BLOCK_SIZE

        self.obs_list = obs_list
        self.grd_size = grd_size

        self.pacman_state = pacman_state
        self.pac_x = pacman_pos[0]
        self.pac_y = grd_size[1] - 1 - pacman_pos[1]
        self.pac_dir = pacman_dir

        self.ghost_state = ghost_state
        self.ghost_x = ghost_pos[0]
        self.ghost_y = grd_size[1] - 1 - ghost_pos[1]

        self.treasure_x = treasure_pos[0]
        self.treasure_y = grd_size[1] - 1 - treasure_pos[1]

        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Pacman Treasure Hunting')
        self.clock = pygame.time.Clock()

        # init images
        self.pacmanImg = pygame.image.load(os.path.join(os.path.dirname(__file__), 'images', 'pacman.png'))
        self.pacmanImg = pygame.transform.scale(self.pacmanImg, (BLOCK_SIZE - 14, BLOCK_SIZE - 14))

        self.ghostImg = pygame.image.load(os.path.join(os.path.dirname(__file__), 'images', 'ghost.png'))
        self.ghostImg = pygame.transform.scale(self.ghostImg, (BLOCK_SIZE - 14, BLOCK_SIZE - 14))

    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

    def _move(self):
        if self.pacman_state:
            current_pos = self.pacman_state.pop(0)
            self.pac_x = current_pos[0][0]
            self.pac_y = self.grd_size[1] - 1 - current_pos[0][1]

            new_img = None
            if current_pos[1] == 'R':
                new_img = pygame.transform.rotate(self.pacmanImg, 0)
            elif current_pos[1] == 'D':
                new_img = pygame.transform.rotate(self.pacmanImg, -90)
            elif current_pos[1] == 'L':
                new_img = pygame.transform.flip(self.pacmanImg, True, False)
            elif current_pos[1] == 'U':
                new_img = pygame.transform.rotate(self.pacmanImg, 90)
            self.display.blit(new_img, (self.pac_x * BLOCK_SIZE + 7, self.pac_y * BLOCK_SIZE + 7))
        else:
            self.display.blit(self.pacmanImg, (self.pac_x * BLOCK_SIZE + 7, self.pac_y * BLOCK_SIZE + 7))

        if self.ghost_state:
            current_pos = self.ghost_state.pop(0)
            self.ghost_x = current_pos[0]
            self.ghost_y = self.grd_size[1] - 1 - current_pos[1]
            #  print(f"Ghost to: ({self.ghost_x}, {self.ghost_y})")
        self.display.blit(self.ghostImg, (self.ghost_x * BLOCK_SIZE + 7, self.ghost_y * BLOCK_SIZE + 7))

    def _update_ui(self):
        self.display.fill(WHITE)
        for x in range(0, self.w, BLOCK_SIZE):
            for y in range(0, self.h, BLOCK_SIZE):
                rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(self.display, BLACK, rect, 1)

        for obs in self.obs_list:
            obs_x = obs[0] * BLOCK_SIZE + 1
            obs_y = (self.grd_size[1] - 1 - obs[1]) * BLOCK_SIZE + 1
            pygame.draw.rect(self.display, GREY, pygame.Rect(obs_x, obs_y, BLOCK_SIZE - 2, BLOCK_SIZE - 2))

        pygame.draw.circle(self.display, BLUE1, (
            self.treasure_x * BLOCK_SIZE + (BLOCK_SIZE // 2), self.treasure_y * BLOCK_SIZE + (BLOCK_SIZE // 2)), 20, 20)

        self._move()

        pygame.display.flip()


if __name__ == '__main__':
    obstacles_list = []
    grid_size = (9, 6)  # x, y grid size

    pacman_position = (0, 2)  # x, y coordinates
    pacman_direction = "R"  # U: up, D: down, L: lef, R: right

    ghost_position = (4, 0)  # x, y coordinates
    ghost_bfs_fringe = tuple()  # FIFOQueue() logic inside, using tuple because of state immutability
    ghost_bfs_explored = tuple()  # simple list() logic inside, using tuple because of state immutability

    treasure_position = (5, 4)  # x, y coordinates

    print("Please, select the maze:")
    print("1) Medium Maze")
    print("2) Difficult Maze")
    maze_selection = int(input("Type the maze number to select: "))
    print()

    print("Select the search algorithm for solving the problem:")
    print("1) DFS (Depth First Search)")
    print("2) UCS (Uniform Cost Search)")
    print("3) BFS (Breadth First Search)")
    print("4) A* (Best First Search)")
    algorithm_selection = int(input("Type the algorithm number to select: "))
    print()

    if maze_selection == 1:
        print('====== SELECTED:: Medium Maze ======')
        obstacles_list = [
            (0, 5), (8, 5),
            (4, 4), (6, 4),
            (0, 3), (3, 3), (4, 3), (5, 3), (6, 3),
            (2, 0), (6, 0)
        ]

    elif maze_selection == 2:
        print('====== SELECTED:: Difficult Maze ======')
        obstacles_list = [
            (0, 8), (1, 8), (2, 8), (5, 8), (11, 8), (12, 8),
            (2, 6), (4, 6), (5, 6), (6, 6), (9, 6), (12, 6),
            (0, 5), (7, 5), (8, 5),
            (3, 4), (4, 4), (6, 4), (8, 4), (9, 4), (10, 4), (12, 4),
            (0, 3), (3, 3), (4, 3), (5, 3), (6, 3), (10, 3),
            (3, 2), (7, 2), (8, 2), (11, 2),
            (8, 1),
            (2, 0), (6, 0)
        ]
        grid_size = (13, 9)
        pacman_position = (5, 4)
        ghost_position = (3, 6)
        treasure_position = (7, 4)
    else:
        sys.exit("Wrong maze selection, please select one from above options!")

    pacman = Pacman(obstacles_list, grid_size,
                    (pacman_position, pacman_direction, ghost_position, ghost_bfs_fringe, ghost_bfs_explored),
                    treasure_position)

    result = None
    if algorithm_selection == 1:
        print('====== SELECTED:: DFS (Depth First Search) ======')
        print()
        print("Searching...")
        print()
        tic = time.perf_counter()
        result = depth_first_graph_search(pacman)
    elif algorithm_selection == 2:
        print('====== SELECTED:: UCS (Uniform Cost Search) ======')
        print()
        print("Searching...")
        print()
        tic = time.perf_counter()
        result = uniform_cost_search(pacman)
    elif algorithm_selection == 3:
        print('====== SELECTED:: BFS (Breadth First Search) ======')
        print()
        print("Searching...")
        print()
        tic = time.perf_counter()
        result = breadth_first_graph_search(pacman)
    elif algorithm_selection == 4:
        print('====== SELECTED:: A* (Best First Search) ======')
        print()
        print("Searching...")
        print()
        tic = time.perf_counter()
        result = astar_search(pacman)
    else:
        print("You didn't select any given algorithm, we'll continue with the default one!")
        print('====== DEFAULT:: BFS (Breadth First Search) ======')
        print()
        print("Searching...")
        print()
        tic = time.perf_counter()
        result = breadth_first_graph_search(pacman)

    toc = time.perf_counter()
    result_solution = result.solution()

    print("====== Solution found ======")
    print(f"Solution: {result_solution}")
    print(f"Nodes expanded: {nodes_count}")
    print(f"Steps: {len(result_solution)}")
    print(f"Time: {toc - tic:0.4f} seconds")
    print()

    print("Do you want to draw/visualise the solution using PyGame?")
    print("1) Yes")
    print("2) No")
    pygame_selection = int(input("Type 1 or 2: "))

    if pygame_selection == 1:
        result_path = result.path()
        pacman_result_state = [(x.state[0], x.state[1]) for x in result_path]
        ghost_result_state = [x.state[2] for x in result_path]

        game = PacmanTreasureVisual(pacman_result_state, ghost_result_state, obstacles_list, grid_size,
                                    pacman_position,
                                    pacman_direction, ghost_position, treasure_position)
        while True:
            game.play_step()
