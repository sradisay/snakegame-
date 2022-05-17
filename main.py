import pygame
import time
import random

pygame.init()

screen = pygame.display.set_mode((800, 800))

running = True
directions = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
opposites = {(0, -1): 'S', (1, 0):'W', (0, 1):'N', (-1,0):'E'}
movements = {pygame.K_UP: 'N', pygame.K_RIGHT: 'E', pygame.K_DOWN: 'S', pygame.K_LEFT: 'W'}


class Apple:
    def __init__(self):
        self.posX = random.randint(0, 80) * 10
        self.posY = random.randint(0, 80) * 10
        self.color = (255, 0, 20)

    def draw(self):
        pygame.draw.rect(screen, self.color, [[self.posX, self.posY], [10, 10]])

    def kill(self):
        self.posX = random.randint(0, 80) * 10
        self.posY = random.randint(0, 80) * 10
        self.color = (random.randint(0, 255), 0, random.randint(0, 255))


class Snake:
    def __init__(self):
        self.starting_posX, self.starting_posY = 40, 80
        self.direction = 'E'
        self.segments = [Segment(self, 0)]
        self.grow()
        self.grow()

    def grow(self):
        self.segments.append(Segment(self, len(self.segments)))

    def move(self):
        for segment in reversed(self.segments):
            segment.move()

    def draw(self):
        for i, segment in enumerate(self.segments):
            pygame.draw.rect(screen, [255, 255, 255], [[segment.posX, segment.posY], [10, 10]])

    def change_targets(self):
        for segment in reversed(self.segments):
            segment.target = (self.segments[segment.index - 1].posX, self.segments[segment.index - 1].posY)

    def check_for_apples(self, apples):
        for apple in apples:
            if self.segments[0].posX == apple.posX and self.segments[0].posY == apple.posY:
                apple.kill()
                self.grow()
    def check_collision(self):
        global running
        for segment in self.segments:
            if segment.index > 0 and segment.posX == self.segments[0].posX and segment.posY == self.segments[0].posY:
                running = False
        if not (0 <= self.segments[0].posX <= 800 and 0 <= self.segments[0].posY <= 800  ):
            running = False


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


snake1 = Snake()
clock = pygame.time.Clock()
frame = 0
gameSpeed = 20
direction = 'E'
apples = [Apple()]
while running:
    clock.tick(144)
    frame += 1
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key in movements:
                if not movements[event.key] == opposites[snake1.segments[0].direction]:
                    direction = movements[event.key]
            if event.key == pygame.K_g:
                snake1.grow()
        if event.type == pygame.QUIT:
            running = False


    screen.fill((10, 10, 10))
    if frame % 2 == 0:
        snake1.move()

    if frame == gameSpeed:
        frame = 0
        snake1.segments[0].direction = directions[direction]
        snake1.check_collision()
        snake1.check_for_apples(apples)
        snake1.change_targets()
    snake1.draw()
    for apple in apples:
        apple.draw()
    pygame.display.flip()

pygame.quit()
