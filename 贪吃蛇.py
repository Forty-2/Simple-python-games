import sys
import random
import pygame
from pygame.locals import *

pygame.init()

size = width, height = 800, 800

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)
YELLOW = (255, 255, 0)
Red_DARK = (150, 0, 0)
BLUE = (0, 0, 255)
BLUE_DARK = (0, 0, 150)
CYAN = (0, 255, 255)

COLORS = [RED, BLUE, YELLOW, CYAN]

CELL_SIZE = 8

screen = pygame.display.set_mode(size)

wall1 = [[0, x] for x in range(100)]
wall2 = [[99, x] for x in range(100)]
wall3 = [[x, 0] for x in range(100)]
wall4 = [[x, 99] for x in range(100)]
walls = wall1 + wall2 + wall3 + wall4


class Snake:

    def __init__(self):
        self.length = 4
        self.speed = 1
        self.color = DARKGREEN
        self.direction = 'right'
        self.bodies = [[50, 50], [49, 50], [48, 50], [47, 50]]

    def draw(self):
        for body in self.bodies:
            pygame.draw.rect(
                screen,
                self.color,
                (body[0] * CELL_SIZE, body[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )

    def move(self, eat):
        """
        move the snake,
        grow if it eats food.
        """
        head = []
        # if the snake don't eat food, pop its ass.
        if eat == 0:
            self.bodies.pop(-1)

        # give the snake a new head.
        if self.direction == 'right':
            head = [self.bodies[0][0] + 1, self.bodies[0][1]]
        elif self.direction == 'left':
            head = [self.bodies[0][0] - 1, self.bodies[0][1]]
        elif self.direction == 'up':
            head = [self.bodies[0][0], self.bodies[0][1] - 1]
        elif self.direction == 'down':
            head = [self.bodies[0][0], self.bodies[0][1] + 1]

        self.bodies.insert(0, head)

    def is_dead(self):
        checknum = 0
        for body in self.bodies:
            if checknum == 0:
                checknum += 1
            else:
                if body == self.bodies[0]:
                    return True
        for block in walls:
            if block == self.bodies[0]:
                return True
        return False


class Food:

    def __init__(self, snake_body):
        while True:
            self.position = [random.randint(1, 98), random.randint(1, 98)]
            if self.is_on_the_snake(snake_body) == 0:
                break
        self.color = random.choice(COLORS)
        self.exist_time = 0
        self.frequency = 0.03
        if random.random() <= self.frequency:
            self.valid = True
        else:
            self.valid = False

    def is_on_the_snake(self, snake_body):
        """
        :type snake_position: list
        """
        for body in snake_body:
            if self.position == body:
                return 1
        return 0

    def draw(self):
        pygame.draw.rect(
            screen,
            self.color,
            (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )


def main():
    snake = Snake()
    foods = []
    new_dir = ''

    pygame.display.set_caption('贪吃蛇')

    # main loop
    while True:
        eat = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(BLACK)
        for block in walls:
            pygame.draw.rect(
                screen,
                WHITE,
                (block[0] * CELL_SIZE, block[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )

        if event.type == KEYDOWN:
            if event.key == K_DOWN:
                new_dir = 'down'
            elif event.key == K_UP:
                new_dir = 'up'
            elif event.key == K_RIGHT:
                new_dir = 'right'
            elif event.key == K_LEFT:
                new_dir = 'left'

        if snake.direction == 'right' or snake.direction == 'left':
            if new_dir == 'up' or new_dir == 'down':
                snake.direction = new_dir
        if snake.direction == 'up' or snake.direction == 'down':
            if new_dir == 'left' or new_dir == 'right':
                snake.direction = new_dir

        new_food = Food(snake.bodies)
        if new_food.valid and len(foods) < 20:
            foods.append(new_food)

        snake.draw()
        if snake.is_dead():
            return 0
        for food in foods:
            if snake.bodies[0] == food.position:
                eat = 1
                foods.remove(food)
            else:
                food.draw()
        snake.move(eat)

        pygame.display.flip()


print("Game Over!")

if __name__ == "__main__":
    main()
