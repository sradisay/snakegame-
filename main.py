import math
import random
import time

import numpy as np
import pygame

from brain import Net as Brain

pygame.init()

screen = pygame.display.set_mode((600, 600))

running = True

NTH = (0, -1)
STH = (0, 1)
WST = (-1, 0)
EST = (1, 0)

oppo = {(0, -1): (0, 1), (1, 0): (-1, 0), (0, 1): (0, -1), (-1, 0): (1, 0)}
rights = {(0, -1): (1, 0), (1, 0): (0, 1), (0, 1): (-1, 0), (-1, 0): (0, -1)}
lefts = {(0, -1): (-1, 0), (1, 0): (0, -1), (0, 1): (1, 0), (-1, 0): (0, 1)}
VERTICAL = [(0, -1), (0, 1)]
HORIZONTAL = [(1, 0), (-1, 0)]
RAY_DIRS = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
DEAD = 0
ALIVE = 1

mut_cut = 0.2
mut_bad = 0.3
mut_mod = 0.3

WALLS = [[(0, 0), (0, 600)], [(0, 0), (600, 0)], [(600, 600), (600, 0)], [(600, 600), (0, 600)]]
WALLS_DICT = {(0, -1): [[(0, 0), (0, 600)]]}


class Apple:
    def __init__(self, color):
        self.posX = 400
        self.posY = 200
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, [[self.posX, self.posY], [10, 10]])

    def kill(self, b):
        if b:
            self.posX = random.randint(0, 60) * 10
            self.posY = random.randint(0, 60) * 10
        else:
            self.posX = 200
            self.posY = 400


class Snake:
    def __init__(self):
        self.starting_posX, self.starting_posY = 300, 300
        self.direction = (1, 0)
        self.state = ALIVE
        self.frame = 0
        self.color = (random.randint(30, 255), random.randint(30, 255), random.randint(30, 255))
        self.apple = Apple(self.color)
        self.net = Brain(32, 24, 12, 4)
        self.num_apples = 0
        self.frames_alive = 0
        self.fitness = 0
        self.segments = [Segment(self, 0)]
        self.grow()
        self.grow()
        self.grow()
        self.grow()

    def reset(self):
        self.state = ALIVE
        self.apple.kill(False)
        self.num_apples = 0
        self.frames_alive = 0
        self.fitness = 0
        self.direction = (1, 0)
        self.segments = [Segment(self, 0)]
        self.grow()
        self.grow()
        self.grow()
        self.grow()

    def grow(self):

        self.segments.append(Segment(self, len(self.segments)))

    def move(self):
        for segment in reversed(self.segments):
            segment.move()

    def draw(self):
        for i, segment in enumerate(self.segments):
            pygame.draw.rect(screen, self.color, [[segment.posX, segment.posY], [10, 10]])
        self.apple.draw()

        for d in RAY_DIRS:
            X = self.segments[0].posX
            Y = self.segments[0].posY
            X2 = X + d[0] * 600
            Y2 = Y + d[1] * 600
            pygame.draw.line(screen, self.color, [X, Y], [X2, Y2])

    def change_targets(self):
        for segment in reversed(self.segments):
            segment.target = (self.segments[segment.index - 1].posX, self.segments[segment.index - 1].posY)

    def check_for_apple(self):
        if self.segments[0].posX == self.apple.posX and self.segments[0].posY == self.apple.posY:
            self.apple.kill(True)
            self.num_apples += 10
            self.grow()

    def check_collision(self):

        for segment in self.segments:
            if segment.index > 0 and segment.posX == self.segments[0].posX and segment.posY == self.segments[
                0].posY and self.state != DEAD:
                self.state = DEAD
                generation.num_alive -= 1

        if self.state != DEAD:
            if not (0 <= self.segments[0].posX < 600 and 0 <= self.segments[0].posY < 600):
                self.state = DEAD
                generation.num_alive -= 1

    def get_intersect(self, A, B, C, D):
        # a1x + b1y = c1
        a1 = B[1] - A[1]
        b1 = A[0] - B[0]
        c1 = a1 * (A[0]) + b1 * (A[1])

        # a2x + b2y = c2
        a2 = D[1] - C[1]
        b2 = C[0] - D[0]
        c2 = a2 * (C[0]) + b2 * (C[1])

        # determinant
        det = a1 * b2 - a2 * b1

        # parallel line
        if det == 0:
            return False

        # intersect point(x,y)
        x = ((b2 * c1) - (b1 * c2)) / det
        y = ((a1 * c2) - (a2 * c1)) / det
        return (x, y)

    def vision(self):
        vision_inputs = []
        for d in RAY_DIRS:
            X = self.segments[0].posX
            Y = self.segments[0].posY
            X2 = X + d[0] * 600
            Y2 = Y + d[1] * 600
            if X - X2 == 0:  # (0,-1) (0, 1)
                if self.apple.posX != X:
                    vision_inputs.append(0)  # Is there and apple in this direction
                else:
                    vision_inputs.append(1)  # Is there and apple in this direction
                nothing_detected = True
                for seg in self.segments:
                    if nothing_detected and seg.index != 0 and seg.posX == X and (
                            ((seg.posY - Y) + 1) / ((abs(seg.posY - Y)) + 1) == d[1]):
                        vision_inputs.append(1)
                        nothing_detected = False
                if nothing_detected:
                    vision_inputs.append(0)
                dist1 = []

                for wall in WALLS:
                    intersection = self.get_intersect((X, Y), (X2, Y2), wall[0], wall[1])
                    if intersection:
                        dist1.append(np.linalg.norm(np.array([X, Y]) - np.array(intersection)))

                vision_inputs.append(min(dist1) / 600)


            else:
                slope = (Y - Y2) / (X - X2)
                B = Y - slope * X

                if slope * self.apple.posX + B - self.apple.posY != 0:
                    vision_inputs.append(0)  # Is there and apple in this direction
                else:
                    vision_inputs.append(1)  # Is there and apple in this direction
                nothing_detected = True
                for seg in self.segments:
                    if nothing_detected and seg.index != 0 and slope * seg.posX + B - seg.posY == 0:
                        vision_inputs.append(1)
                        nothing_detected = False

                if nothing_detected:
                    vision_inputs.append(0)

                dist1 = []

                for wall in WALLS:
                    intersection = self.get_intersect((X, Y), (X2, Y2), wall[0], wall[1])
                    if intersection:
                        dist1.append(np.linalg.norm(np.array([X, Y]) - np.array(intersection)))
                vision_inputs.append(min(dist1) / 850)

        return vision_inputs

    def get_inputs(self, dir):
        tail_dir = self.segments[-1].direction
        inputs = [dir == NTH, dir == STH, dir == EST, dir == WST, tail_dir == NTH, tail_dir == STH, tail_dir == EST,
                  tail_dir == WST]

        for val in self.vision():
            inputs.append(val)
        return inputs

    def get_direction(self, current_direction):
        inputs = self.get_inputs(current_direction)
        val = self.net.get_max_value(inputs)
        for index, value in enumerate(val):
            if value == np.max(val):
                if index == 0:
                    return 0, -1
                elif index == 1:
                    return 0, 1
                elif index == 2:
                    return 1, 0
                elif index == 3:
                    return -1, 0

    def create_offspring(p1, p2):
        new_snake = Snake()
        new_snake.net.create_mixed_weight(p1.net, p2.net)
        return new_snake

    def update(self):
        if self.state != DEAD:
            self.frame += gameSpeed / 20
            if self.frame % (gameSpeed / 10) == 0:
                self.move()
            if self.frame == gameSpeed and self.segments[0].posX % 10 == 0 and self.segments[0].posY % 10 == 0:
                self.frame = 0
                self.segments[0].direction = self.get_direction(self.segments[0].direction)
                self.check_collision()
                self.check_for_apple()
                self.change_targets()

            self.draw()


class Segment:
    def __init__(self, snake, index):
        self.starting_posX = snake.starting_posX
        self.starting_posY = snake.starting_posY

        self.index = index
        if self.index == 0:
            self.posX = self.starting_posX
            self.posY = self.starting_posY
            self.direction = snake.direction

        else:
            self.parent = snake.segments[self.index - 1]
            self.posX = self.parent.posX
            self.posY = self.parent.posY
            self.direction = snake.segments[self.index - 1].direction
            self.target = (self.parent.posX, self.parent.posY)

    def move(self):
        if self.index == 0:
            self.posX += self.direction[0]
            self.posY += self.direction[1]
        else:
            self.direction = tuple(map(lambda i, j: i - j, self.target, (self.posX, self.posY)))

            if self.direction[0] > 0:
                self.posX += 1

            elif self.direction[0] < 0:
                self.posX += -1

            if self.direction[1] > 0:
                self.posY += 1

            elif self.direction[1] < 0:
                self.posY += -1


class SnakeGeneration():
    def __init__(self):
        self.snakes = []
        self.num_alive = 0
        self.length = 0

    def get_overall_length(self):
        self.length = 0
        for s in self.snakes:
            self.length += len(s.segments)

    def has_length_changes(self):
        previous_length = self.length
        global death_clock
        self.get_overall_length()
        if previous_length == self.length:

            death_clock -= 1
        else:
            death_clock += 1000

    def create(self):
        for _ in range(100):
            self.snakes.append(Snake())
            self.num_alive += 1

    def create_more(self):
        for snake in self.snakes:
            snake.reset()
            self.num_alive += 1

    def evolve(self):
        for s in self.snakes:
            s.fitness += (s.num_apples)

        self.snakes.sort(key=lambda x: x.fitness, reverse=True)
        print(self.snakes[0].fitness)
        cut_off = int(len(self.snakes) * mut_cut)
        good_snakes = self.snakes[0:cut_off]
        bad_snakes = self.snakes[cut_off:]
        num_bad = int(len(self.snakes) * mut_bad)

        for s in bad_snakes:
            s.net.modify_weights()

        new_snakes = []

        idx_bad = np.random.choice(np.arange(len(bad_snakes)), num_bad, replace=False)

        for index in idx_bad:
            new_snakes.append(bad_snakes[index])

        new_snakes.extend(good_snakes)
        childs = len(self.snakes) - len(new_snakes)

        while len(new_snakes) < len(self.snakes):
            idx_new = np.random.choice(np.arange(len(good_snakes)), 2, replace=False)
            if idx_new[0] != idx_new[1]:
                new_snake = Snake.create_offspring(good_snakes[idx_new[0]], good_snakes[idx_new[1]])
                if random.random() < mut_mod:
                    new_snake.net.modify_weights()
                new_snakes.append(new_snake)
        for s in new_snakes:
            s.reset()
            self.num_alive += 1

        self.snakes = new_snakes


clock = pygame.time.Clock()

gameSpeed = 5

generation = SnakeGeneration()
generation.create()
death_clock = 10000

while running:
    clock.tick(3000)
    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                for s in generation.snakes:
                    s.grow()
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 10))
    for s in generation.snakes:
        if s.state != DEAD:
            s.update()
    if generation.num_alive <= 0 or death_clock < 0:
        time.sleep(0.5)
        generation.num_alive = 0
        generation.evolve()
        death_clock = 10000

    pygame.display.flip()
    generation.has_length_changes()

pygame.quit()
