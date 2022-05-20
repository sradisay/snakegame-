import math
import random

import numpy as np
import pygame

from brain import Net as Brain

pygame.init()

screen = pygame.display.set_mode((800, 600))

running = True
directions = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
opposites = {(0, -1): 'S', (1, 0): 'W', (0, 1): 'N', (-1, 0): 'E'}
oppo = {(0, -1): (0, 1), (1, 0): (-1, 0), (0, 1): (0, -1), (-1, 0): (1, 0)}
movements = {pygame.K_UP: 'N', pygame.K_RIGHT: 'E', pygame.K_DOWN: 'S', pygame.K_LEFT: 'W'}
cardinals = ['N', 'E', 'S', 'W']
rights = {(0, -1): (1, 0), (1, 0): (0, 1), (0, 1): (-1, 0), (-1, 0): (0, -1)}
lefts = {(0, -1): (-1, 0), (1, 0): (0, -1), (0, 1): (1, 0), (-1, 0): (0, 1)}
direction_to_data = {(0, -1): 0.25, (1, 0): 0.5, (0, 1): 0.75, (-1, 0): 0.99}
VERTICAL = [(0, -1), (0, 1)]
HORIZONTAL = [(1, 0), (-1, 0)]
DEAD = 'DEAD'
ALIVE = 'ALIVE'
mut_cut = 0.2
mut_bad = 0.3
mut_mod = 0.4


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
        self.direction = 'E'
        self.state = ALIVE
        self.frame = 0
        self.color = (random.randint(30, 255), random.randint(30, 255), random.randint(30, 255))
        self.apple = Apple(self.color)
        self.net = Brain(5, 25, 1)
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
        self.frames_alive = 0
        self.num_apples = 0
        self.direction = 'E'
        self.segments = [Segment(self, 0)]
        self.grow()
        self.grow()
        self.grow()
        self.grow()

    def grow(self):

        self.segments.append(Segment(self, len(self.segments)))
        self.num_apples += 10

    def move(self):
        for segment in reversed(self.segments):
            segment.move()

    def draw(self):
        for i, segment in enumerate(self.segments):
            pygame.draw.rect(screen, self.color, [[segment.posX, segment.posY], [10, 10]])
        self.apple.draw()

    def change_targets(self):
        for segment in reversed(self.segments):
            segment.target = (self.segments[segment.index - 1].posX, self.segments[segment.index - 1].posY)

    def check_for_apple(self):
        if self.segments[0].posX == self.apple.posX and self.segments[0].posY == self.apple.posY:
            self.apple.kill(True)
            self.grow()
            global death_clock
            death_clock = 100000

    def check_collision(self):

        for segment in self.segments:
            if segment.index > 0 and segment.posX == self.segments[0].posX and segment.posY == self.segments[0].posY:
                self.state = DEAD
                generation.num_alive -= 1
                break
        if self.state != DEAD:
            if not (0 <= self.segments[0].posX <= 600 and 0 <= self.segments[0].posY <= 600):
                self.state = DEAD
                generation.num_alive -= 1

    def next_col(self):
        next_posX = self.segments[0].posX + self.segments[0].direction[0]
        next_posY = self.segments[0].posX + self.segments[0].direction[1]
        if not (0 <= next_posX <= 600 and 0 <= next_posY <= 600):
            return 1
        for segment in self.segments:
            if segment.index > 0 and segment.posX == next_posX and segment.posY == next_posY:
                return 1
        return 0

    def next_col_right(self, current_direction):
        next_posX = self.segments[0].posX + rights[current_direction][0]
        next_posY = self.segments[0].posX + rights[current_direction][1]
        if not (0 <= next_posX <= 600 and 0 <= next_posY <= 600):
            return 1
        for segment in self.segments:
            if segment.index > 0 and segment.posX == next_posX and segment.posY == next_posY:
                return 1
        return 0

    def next_col_left(self, current_direction):
        next_posX = self.segments[0].posX + lefts[current_direction][0]
        next_posY = self.segments[0].posX + lefts[current_direction][1]
        if not (0 <= next_posX <= 600 and 0 <= next_posY <= 600):
            return 1
        for segment in self.segments:
            if segment.index > 0 and segment.posX == next_posX and segment.posY == next_posY:
                return 1
        return 0

    def apple_angle(self):
        pX = self.segments[0].posX
        pY = self.segments[0].posY
        ApX = self.apple.posX
        ApY = self.apple.posY

        angle = math.atan2(ApY - pY, ApX - pX) * 180 / math.pi;

        return angle / 180

    def suggested_direction(self, current_direction):
        d = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        d.remove(oppo[current_direction])
        for dir in d:
            if dir == current_direction and self.next_col() == 1:
                d.remove(dir)
            elif dir == lefts[current_direction] and self.next_col_left(current_direction) == 1:
                d.remove(dir)
            elif dir == rights[current_direction] and self.next_col_right(current_direction) == 1:
                d.remove(dir)
        s = []
        for dir in d:
            if dir in VERTICAL:
                if abs(self.apple.posY - (self.segments[0].posY + dir[1])) <= abs(
                        self.apple.posY - self.segments[0].posY):
                    s.append(dir)
            if dir in HORIZONTAL:
                if abs(self.apple.posX - (self.segments[0].posX + dir[0])) <= abs(
                        self.apple.posX - self.segments[0].posX):
                    s.append(dir)
        if len(s) == 0:
           suggested =  d[0]
        elif len(s) != 1:
            suggested = random.choice(s)
        else:
            suggested = s[0]

        if suggested == lefts[current_direction]:
            return -1
        elif suggested == rights[current_direction]:
            return 1
        elif suggested == current_direction:
            return 0


    def get_inputs(self, current_direction):

        inputs = [self.next_col(), self.next_col_left(current_direction), self.next_col_right(current_direction),
                  self.apple_angle(), self.suggested_direction(current_direction)]

        return inputs

    def get_direction(self, current_direction):
        inputs = self.get_inputs(current_direction)
        val = self.net.get_max_value(inputs)
        print(val)
        if val >= 0.66:
            return rights[current_direction]
        elif val >= 0.33:
            return lefts[current_direction]
        else:
            return current_direction

    def create_offspring(p1, p2):
        new_snake = Snake()
        new_snake.net.create_mixed_weight(p1.net, p2.net)
        return new_snake

    def update(self):
        if self.state != DEAD:
            self.frame += gameSpeed / 20
            if self.frame % (gameSpeed / 10) == 0:
                self.move()
            if self.frame == gameSpeed:
                self.frame = 0
                self.segments[0].direction = self.get_direction(self.segments[0].direction)
                self.check_collision()
                self.check_for_apple()
                self.change_targets()
                self.frames_alive += 1
            self.draw()


class Segment:
    def __init__(self, snake, index):
        self.starting_posX = snake.starting_posX
        self.starting_posY = snake.starting_posY

        self.index = index
        if self.index == 0:
            self.posX = self.starting_posX
            self.posY = self.starting_posY
            self.direction = directions[snake.direction]

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
        self.create_more()
        self.num_alive = 0

    def create(self):
        for _ in range(1000):
            self.snakes.append(Snake())
            self.num_alive += 1

    def create_more(self):
        for snake in self.snakes:
            snake.reset()
            self.num_alive += 1

    def evolve(self):
        for s in self.snakes:
            s.fitness += (s.frames_alive * s.num_apples)

        self.snakes.sort(key=lambda x: x.fitness, reverse=True)

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
direction = 'E'

generation = SnakeGeneration()
generation.create()
death_clock = 30000
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
        s.update()
    if generation.num_alive <= 1 or death_clock < 0:
        generation.num_alive = 0
        generation.evolve()
        death_clock = 30000
    death_clock -= 1
    pygame.display.flip()

pygame.quit()
