import pygame
import time
import random
from brain import Net as Brain
import numpy as np

pygame.init()

screen = pygame.display.set_mode((800, 600))

running = True
directions = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
opposites = {(0, -1): 'S', (1, 0): 'W', (0, 1): 'N', (-1, 0): 'E'}
movements = {pygame.K_UP: 'N', pygame.K_RIGHT: 'E', pygame.K_DOWN: 'S', pygame.K_LEFT: 'W'}
cardinals = ['N', 'E', 'S', 'W']
rights = {(0, -1): (1, 0), (1, 0): (0, 1), (0, 1): (-1, 0), (-1, 0): (0, -1)}
lefts = {(0, -1): (-1, 0), (1, 0): (0, -1), (0, 1): (1, 0), (-1, 0): (0, 1)}
DEAD = 'DEAD'
ALIVE = 'ALIVE'



class Apple:
    def __init__(self):
        self.posX = random.randint(0, 60) * 10
        self.posY = random.randint(0, 60) * 10
        self.color = (255, 0, 20)

    def draw(self):
        pygame.draw.rect(screen, self.color, [[self.posX, self.posY], [10, 10]])

    def kill(self):
        self.posX = random.randint(0, 60) * 10
        self.posY = random.randint(0, 60) * 10
        self.color = (random.randint(0, 255), 0, random.randint(0, 255))


class Snake:
    def __init__(self):
        self.starting_posX, self.starting_posY = 300, 300
        self.direction = 'E'
        self.state = ALIVE
        self.frame = 0
        self.color = (random.randint(30, 255), random.randint(30, 255), random.randint(30, 255))
        self.apple = Apple()
        self.net = Brain(2, 5, 2)
        self.num_apples = 0
        self.frames_alive = 0
        self.fitness = 0
        self.death = 100
        self.segments = [Segment(self, 0)]
        self.grow()
        self.grow()


    def reset(self):
        self.state = ALIVE
        self.fitness = 0
        self.frames_alive = 0
        self.num_apples = 0
        self.direction = 'E'
        self.segments = [Segment(self, 0)]
        self.grow()
        self.grow()

    def grow(self):

        self.segments.append(Segment(self, len(self.segments)))
        self.num_apples += 1
        self.death += 20

    def move(self):
        for segment in reversed(self.segments):
            segment.move()
        self.death -= 1

    def draw(self):
        for i, segment in enumerate(self.segments):
            pygame.draw.rect(screen, self.color, [[segment.posX, segment.posY], [10, 10]])
        self.apple.draw()

    def change_targets(self):
        for segment in reversed(self.segments):
            segment.target = (self.segments[segment.index - 1].posX, self.segments[segment.index - 1].posY)

    def check_for_apple(self):
        if self.segments[0].posX == self.apple.posX and self.segments[0].posY == self.apple.posY:
            self.apple.kill()
            self.grow()

    def check_collision(self):

        for segment in self.segments:
            if segment.index > 0 and segment.posX == self.segments[0].posX and segment.posY == self.segments[0].posY:
                self.state = DEAD
                generation.num_alive -= 1

        if not (0 <= self.segments[0].posX <= 600 and 0 <= self.segments[0].posY <= 600):
            self.state = DEAD
            generation.num_alive -= 1

    def get_inputs(self):
        inputs = [(self.segments[0].posX - self.apple.posX + 600) / 600,
                  (self.segments[0].posX - self.apple.posX + 600) / 600]

        return inputs

    def get_direction(self, current_direction):
        inputs = self.get_inputs()
        val = self.net.get_max_value(inputs)
        d = np.where(val == np.max(val))

        if d[0] == 1 and np.max(val) > 0.5:
            return lefts[current_direction]
        elif d[0] == 0 and np.max(val) > 0.5:
            return rights[current_direction]
        else:
            return current_direction

    def update(self):
        global death_clock
        if self.state != DEAD:
            self.frame += 1
            if self.frame % 2 == 0:
                self.move()
            if self.frame == gameSpeed:
                self.frame = 0
                self.segments[0].direction = self.get_direction(self.segments[0].direction)
                self.check_collision()
                self.check_for_apple()
                self.change_targets()
                self.frames_alive += 1
                if self.death <= 0:
                    death_clock -= 2
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
        for _ in range(100):
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

        for s in self.snakes:
            print('fitness: ', s.fitness)
        self.create_more()


death_clock = 10000
clock = pygame.time.Clock()

gameSpeed = 20
direction = 'E'

generation = SnakeGeneration()
generation.create()
while running:
    clock.tick(144)

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
    if generation.num_alive == 0 or death_clock < 1000:
        generation.evolve()
        death_clock = 10000
    pygame.display.flip()

pygame.quit()
