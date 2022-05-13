import pygame
import time

pygame.init()

screen = pygame.display.set_mode((800, 800))

running = True
directions = {'N': (0, -10), 'E': (10, 0), 'S': (0, 10), 'W': (-10, 0)}
movements = {pygame.K_UP: 'N', pygame.K_RIGHT: 'E', pygame.K_DOWN: 'S', pygame.K_LEFT: 'W'}


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

    def move(self):
        for segment in reversed(self.segments):
            segment.move(self)

    def draw(self):
        for i,segment in enumerate(self.segments):
            pygame.draw.rect(screen, [255, 255, 255], [[segment.posX, segment.posY], [10, 10]])


class Segment():
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
            self.direction = snake.segments[self.index - 1].direction

    def move(self, snake):
        if self.index == 0:
            self.posX += directions[self.direction][0]
            self.posY += directions[self.direction][1]
            print(self.posX, self.posY)
        else:
            self.posX = snake.segments[self.index - 1].posX
            self.posY = snake.segments[self.index - 1].posY


snake1 = Snake()

while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key in movements:
                snake1.segments[0].direction = movements[event.key]
            if event.key == pygame.K_g:
                snake1.grow()
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 10))
    snake1.move()
    snake1.draw()
    pygame.display.flip()
    time.sleep(0.1)

pygame.quit()