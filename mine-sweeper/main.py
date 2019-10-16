import sys
import random
from functools import lru_cache
import pygame
import time

sys.setrecursionlimit(99999)
pygame.init()

M, N = 30, 20
CELL_SIZE = 20
size = width, height = M * CELL_SIZE, N * CELL_SIZE

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


flag = "flag.png"
mine = "mine.png"

screen = pygame.display.set_mode(size)


class Block:

    def __init__(self, prop, x, y):
        self.prop = prop
        self.status = 0  # 0: undetected, -1: detected, 1: flagged
        self.press = 0
        self.position = x, y
        self.dangers = 0
        self.scanned = 0

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
        x = random.randint(0, M-1)
        y = random.randint(0, N-1)
        mine_set.add((x, y))
        if len(mine_set) == n:
            break
    return mine_set


def message(words, color):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 90)
    te = font.render(words, 0, color)
    te_rect = te.get_rect()
    center = [width / 2, height / 2]
    te_rect.center = center
    screen.blit(te, te_rect)
    pygame.display.flip()


# @lru_cache(3)
def find_safe_zone(a, b, blocks):
    cor = (a, b)
    safe_zone = set()
    blocks[a][b].scanned = 1
    if blocks[a][b].dangers > 0:
        safe_zone.add(cor)
    else:
        safe_zone.add(cor)
        if 0<=a-1 and blocks[a-1][b].scanned == 0:
            set_t = find_safe_zone(a-1, b, blocks)
            safe_zone = safe_zone.union(set_t)
        if a+1<M and blocks[a+1][b].scanned == 0:
            set_t = find_safe_zone(a+1, b, blocks)
            safe_zone = safe_zone.union(set_t)
        if b-1>=0 and blocks[a][b-1].scanned == 0:
            set_t = find_safe_zone(a, b-1, blocks)
            safe_zone = safe_zone.union(set_t)
        if b+1<N and blocks[a][b+1].scanned == 0:
            set_t = find_safe_zone(a, b+1, blocks)
            safe_zone = safe_zone.union(set_t)
        if 0<=a-1 and b>=1 and blocks[a-1][b-1].scanned == 0:
            set_t = find_safe_zone(a-1, b-1, blocks)
            safe_zone = safe_zone.union(set_t)
        if 0<=a-1 and b+1<N and blocks[a-1][b+1].scanned == 0:
            set_t = find_safe_zone(a-1, b+1, blocks)
            safe_zone = safe_zone.union(set_t)
        if a+1<M and b-1>=0 and blocks[a+1][b-1].scanned == 0:
            set_t = find_safe_zone(a+1, b-1, blocks)
            safe_zone = safe_zone.union(set_t)
        if a+1<M and b+1<N and blocks[a+1][b+1].scanned == 0:
            set_t = find_safe_zone(a+1, b+1, blocks)
            safe_zone = safe_zone.union(set_t)
    return safe_zone


def main():
    blocks = [[] for i in range(M)]
    mines = generate_mine(60)
    detected = set()
    whole = set((x,y) for x in range(M) for y in range(N))
    whole = whole.difference(mines)
    # generate minefield
    for i in range(M):
        for j in range(N):
            if (i, j) in mines:
                blocks[i].append(Block(1, i, j))
            else:
                blocks[i].append(Block(0, i, j))
    # calculate bombs around the blocks
    for i in range(M):
        for j in range(N):
            blocks[i][j].dangers = get_mines_around(blocks, i, j)
    pygame.display.set_caption('Mine Sweeper')
    a, b = 0, 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if get_pressed(event.pos) == (a, b):
                    if event.button == 1:
                        blocks[a][b].left_button_up()
                        if blocks[a][b].dangers == 0:
                            safe_zone = find_safe_zone(a, b, blocks)
                            for (x, y) in safe_zone:
                                blocks[x][y].status = -1
                        # fail
                        if blocks[a][b].prop == 1:
                            t = time.time()
                            while time.time()-t < 4:
                                for _ in pygame.event.get():
                                    pass
                                message('You Failed!', RED)
                            pygame.quit()
                        detected.add((a, b))
                        if detected == whole:
                            print('success')
                            message('You Win!', BLUE)
                    elif event.button == 3:
                        blocks[a][b].right_button_up()
                else:
                    blocks[a][b].press = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                a, b = get_pressed(event.pos)
                blocks[a][b].button_down()

        # draw the background
        screen.fill(BLACK)

        # draw the blocks
        for row in blocks:
            for block in row:
                block.draw()
                if block.status == -1:
                    if block.dangers > 0 and block.prop == 0:
                        block.text()

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
