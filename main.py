import pygame
import time
import random

pygame.init()

screen = pygame.display.set_mode((800, 600))

running = True
directions = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
opposites = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
movements = {pygame.K_UP: 'N', pygame.K_RIGHT: 'E', pygame.K_DOWN: 'S', pygame.K_LEFT: 'W'}


class Sustanance:
    def __init__(self):
        self.posX = random.randint(0, 80) * 10
        self.posY = random.randint(0, 60) * 10
        self.color = (255, 0, 20)

    def draw(self):
        pygame.draw.rect(screen, self.color, [[self.posX, self.posY], [10, 10]])

    def kill(self):
        self.posX = random.randint(0, 80) * 10
        self.posY = random.randint(0, 60) * 10
        self.color = (255, 0, random.randint(0, 255))


class Snake:
    def __init__(self):
        self.starting_posX, self.starting_posY = 40, 80
        self.direction = 'E'
        self.segments = [Segment(self.starting_posX, self.starting_posY, self.direction, self, 0)]
        self.grow()
        self.grow()


    def grow(self):
        lastSegment = self.segments[len(self.segments) - 1]
        self.segments.append(Segment(lastSegment.posX, lastSegment.posY, None, self, len(self.segments)))

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
        if not (0 <= self.segments[0].posX <= 800 and 0 <= self.segments[0].posY <= 600):
            running = False

    def move(self, n=1):
        for segment in reversed(self.segments):
            segment.move(self, n)

    def draw(self):
        for i, segment in enumerate(self.segments):
            pygame.draw.rect(screen, [255, 255, 255], [[segment.posX, segment.posY], [10, 10]])

    def change_direction(self):
        for segment in reversed(self.segments):
            if segment.index != 0:
                segment.direction = segment.parent.direction

class Segment:
    def __init__(self, starting_posX, starting_posY, direction, snake, index):
        self.starting_posX = starting_posX
        self.starting_posY = starting_posY
        self.index = index

        if self.index == 0:
            self.posX = starting_posX
            self.posY = starting_posY
            self.direction = direction

        else:
            self.posX = snake.segments[self.index - 1].posX
            self.posY = snake.segments[self.index - 1].posY

            self.parent = snake.segments[index - 1]
            self.direction = self.parent.direction

    def move(self, snake, n):

        if self.index == 0:

            self.posX += directions[self.direction][0]*n
            self.posY += directions[self.direction][1]*n
        else:
            self.posX = (snake.segments[self.index - 1].posX*n) - directions[self.parent.direction][0]*10
            self.posY = (snake.segments[self.index - 1].posY*n) - directions[self.parent.direction][1]*10


snake1 = Snake()
apples = [Sustanance()]
clock = pygame.time.Clock()
direction = "E"
frame = 0
gameSpeed = 20
while running:
    clock.tick(165)
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

    for apple in apples:
        apple.draw()
    screen.blit(pygame.font.Font(None, 30).render(str(clock.get_fps()), True, [255, 255, 255]), [0, 0])

    if frame % 2 == 0:
        snake1.move()
    if frame == gameSpeed:
        frame = 0
        snake1.segments[0].direction = direction
        snake1.check_collision()
        snake1.check_for_apples(apples)
        snake1.change_direction()
    snake1.draw()

    pygame.display.flip()

pygame.quit()
