import sys
import random
import pygame

pygame.init()
size = width, height = 600, 400

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)
YELLOW = (255, 255, 0)
RED_DARK = (150, 0, 0)
BLUE = (0, 0, 255)
BLUE_DARK = (0, 0, 150)
CYAN = (0, 255, 255)
BROWN = (115, 74, 18)

CELL_SIZE = 20
M = int(size[0] / CELL_SIZE)
N = int(size[1] / CELL_SIZE)

flag = "flag.png"
mine = "mine.png"

screen = pygame.display.set_mode(size)


class Block:

    def __init__(self, prop, x, y):
        self.prop = prop
        self.status = 0  # 0: undetected, 1: detected
        self.press = 0
        self.position = x, y
        self.dangers = 0

    def draw(self):
        # pressed
        if self.press == 1:
            pygame.draw.rect(
                screen,
                DARKGREEN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                0
            )
        # undetected
        elif self.status == 0:
            pygame.draw.rect(
                screen,
                GREEN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                0
            )
            pygame.draw.rect(
                screen,
                DARKGREEN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                2
            )
        # detected
        elif self.status == -1:
            pygame.draw.rect(
                screen,
                BROWN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                0
            )
            pygame.draw.rect(
                screen,
                DARKGRAY,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1),
                1
            )
            if self.prop == 1:
                self.show_pic(mine)
        # marked
        elif self.status == 1:
            pygame.draw.rect(
                screen,
                GREEN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                0
            )
            pygame.draw.rect(
                screen,
                DARKGREEN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                2
            )
            self.show_pic(flag)

    def text(self, content=None):
        if content:
            t = content
        else:
            t = str(self.dangers)
        font = pygame.font.Font(None, 20)
        colors = (BLUE, GREEN, RED, YELLOW, CYAN, WHITE, RED_DARK, BLUE_DARK)
        te = font.render(t, 1, colors[self.dangers-1])
        center = (self.position[0]*CELL_SIZE+CELL_SIZE/2, self.position[1]*CELL_SIZE+CELL_SIZE/2)
        textpos = te.get_rect(center=center)
        screen.blit(te, textpos)

    def show_pic(self, pic):
        background = pygame.image.load(pic).convert_alpha()
        background = pygame.transform.scale(background, (16, 16))
        screen.blit(background, (self.position[0] * CELL_SIZE + 1, self.position[1] * CELL_SIZE + 1))

    def left_button_up(self):
        self.status = -1
        self.press = 0

    def button_down(self):
        if self.status != -1:
            self.press = 1

    def right_button_up(self):
        self.press = 0
        if self.status != -1:
            if self.status == 1:
                self.status = 0
            else:
                self.status = 1


def get_pressed(pos):
    x, y = pos
    a = x // CELL_SIZE
    b = y // CELL_SIZE
    return a, b


def get_mines_around(blocks, a, b):
    count = 0
    cors = ([a - 1, b - 1], [a, b - 1], [a + 1, b - 1],
            [a - 1, b],                 [a + 1, b],
            [a - 1, b + 1], [a, b + 1], [a + 1, b + 1])
    for cor in cors:
        if M-1 >= cor[0] >= 0 and N-1 >= cor[1] >= 0:
            if blocks[cor[0]][cor[1]].prop == 1:
                count += 1
    return count


def generate_mine(n=10):
    mine_set = set()
    while True:
        x = random.randint(0, M)
        y = random.randint(0, N)
        mine_set.add((x, y))
        if len(mine_set) == n:
            break
    return mine_set


def fail(t):
    font = pygame.font.Font("/System/Library/Fonts/Courier.dfont", 90)
    te = font.render('BOOM!!!', 0, RED)
    center = [width / 2, height / 2]
    textpos = te.get_rect(center=center)
    screen.blit(te, textpos)
    time.sleep(int(t))


def main():
    blocks = [[] for i in range(M)]
    mines = generate_mine(30)
    for i in range(M):
        for j in range(N):
            if (i, j) in mines:
                blocks[i].append(Block(1, i, j))
            else:
                blocks[i].append(Block(0, i, j))
    for i in range(M):
        for j in range(N):
            blocks[i][j].dangers = get_mines_around(blocks, i, j)
    pygame.display.set_caption('扫雷')
    a, b = 0, 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if get_pressed(event.pos) == (a, b):
                    if event.button == 1:
                        blocks[a][b].left_button_up()
                    elif event.button == 3:
                        blocks[a][b].right_button_up()
                else:
                    blocks[a][b].press = 0
                print('[mouse button up]', ' #', event.pos, event.button, 'Number:', get_pressed(event.pos))
                print(blocks[a][b].dangers)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                a, b = get_pressed(event.pos)
                blocks[a][b].button_down()
                print('[mouse button down]', ' #', event.pos, event.button)

        screen.fill(BLACK)

        for row in blocks:
            for block in row:
                block.draw()
                if block.status == -1:
                    if block.dangers > 0 and block.prop == 0:
                        block.text()

        # if blocks[a][b].prop == 1:
        #     fail(3)
        #     sys.exit()

        pygame.display.flip()

    sys.exit()


if __name__ == '__main__':
    main()
