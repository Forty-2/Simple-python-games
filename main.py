import sys
import random
import pygame
import time


# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
GRAY = (60, 60, 60)
DARKGRAY = (30, 30, 30)
YELLOW = (255, 255, 0)
RED_DARK = (150, 0, 0)
BLUE = (0, 0, 255)
BLUE_DARK = (0, 0, 150)
CYAN = (0, 255, 255)
BROWN = (115, 74, 18)

CELL_SIZE = 20

flag = "flag.png"
mine = "mine.png"


class Block:

    def __init__(self, prop, x, y, screen):
        self.screen = screen
        self.prop = prop
        self.status = 0  # 0: undetected, -1: detected, 1: flagged
        self.press = 0
        self.position = x, y
        self.dangers = 0
        self.scanned = 0

    def draw(self):
        # pressed
        if self.press == 1 and self.status == 0:
            pygame.draw.rect(
                self.screen,
                DARKGREEN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                0
            )
        # undetected
        elif self.status == 0:
            pygame.draw.rect(
                self.screen,
                GREEN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                0
            )
            pygame.draw.rect(
                self.screen,
                DARKGREEN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                2
            )
        # detected
        elif self.status == -1:
            pygame.draw.rect(
                self.screen,
                BROWN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                0
            )
            pygame.draw.rect(
                self.screen,
                DARKGRAY,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1),
                1
            )
            if self.prop == 1:
                self.show_pic(mine)
        # marked
        elif self.status == 1:
            pygame.draw.rect(
                self.screen,
                GREEN,
                (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                0
            )
            pygame.draw.rect(
                self.screen,
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
        self.screen.blit(te, textpos)

    def show_pic(self, pic):
        background = pygame.image.load(pic).convert_alpha()
        background = pygame.transform.scale(background, (16, 16))
        self.screen.blit(background, (self.position[0] * CELL_SIZE + 1, self.position[1] * CELL_SIZE + 1))

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

    def right_left_down(self, blocks):
        around = get_around_cor(self.position[0], self.position[1])
        for (x, y) in around:
            if 0<=x<len(blocks) and 0<=y<len(blocks[0]):
                blocks[x][y].press = 1

    def right_left_up(self, blocks):
        around = get_around_cor(self.position[0], self.position[1])
        for (x, y) in around:
            if 0<=x<len(blocks) and 0<=y<len(blocks[0]):
                blocks[x][y].press = 0


def get_pressed_cor(pos):
    x, y = pos
    a = x // CELL_SIZE
    b = y // CELL_SIZE
    return a, b


def get_mines_around(blocks, a, b, M, N):
    count = 0
    cors = get_around_cor(a, b)
    for cor in cors:
        if M-1 >= cor[0] >= 0 and N-1 >= cor[1] >= 0:
            if blocks[cor[0]][cor[1]].prop == 1:
                count += 1
    return count


def generate_mine(M, N, n=10):
    mine_set = set()
    while True:
        x = random.randint(0, M-1)
        y = random.randint(0, N-1)
        mine_set.add((x, y))
        if len(mine_set) == n:
            break
    return mine_set


def message(words, color, screen, width, height):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 90)
    te = font.render(words, 0, color)
    te_rect = te.get_rect()
    center = [width / 2, height / 2]
    te_rect.center = center
    screen.blit(te, te_rect)
    pygame.display.flip()


def find_safe_zone(a, b, M, N, blocks):
    cor = (a, b)
    safe_zone = set()
    blocks[a][b].scanned = 1
    if blocks[a][b].dangers > 0:
        safe_zone.add(cor)
    else:
        safe_zone.add(cor)
        around = get_around_cor(a, b)
        for (x, y) in around:
            if 0<=x<M and 0<=y<N and blocks[x][y].scanned == 0:
                set_t = find_safe_zone(x, y, M, N, blocks)
                safe_zone = safe_zone.union(set_t)
    return safe_zone


def get_around_cor(a, b):
    return ([a - 1, b - 1], [a, b - 1], [a + 1, b - 1],
            [a - 1, b],                 [a + 1, b],
            [a - 1, b + 1], [a, b + 1], [a + 1, b + 1])


def main():
    # initialize
    pygame.init()
    M, N = 30, 20
    mines_number = 40
    size = width, height = M * CELL_SIZE, N * CELL_SIZE
    screen = pygame.display.set_mode(size)

    blocks = [[] for i in range(M)]
    mines = generate_mine(M, N, mines_number)
    detected = set()
    whole = set((x,y) for x in range(M) for y in range(N))
    whole = whole.difference(mines)
    flagged = set()
    # generate minefield
    for i in range(M):
        for j in range(N):
            if (i, j) in mines:
                blocks[i].append(Block(1, i, j, screen))
            else:
                blocks[i].append(Block(0, i, j, screen))
    # calculate bombs around the blocks
    for i in range(M):
        for j in range(N):
            blocks[i][j].dangers = get_mines_around(blocks, i, j, M, N)
    pygame.display.set_caption('Mine Sweeper')
    a, b = 0, 0
    right_mouse_down, left_mouse_down, both_down = 0, 0, 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if get_pressed_cor(event.pos) == (a, b):
                    if left_mouse_down and right_mouse_down:
                        blocks[a][b].press = 0
                        blocks[a][b].right_left_up(blocks)
                        if event.button == 1:
                            left_mouse_down = 0
                        elif event.button == 3:
                            right_mouse_down = 0
                        around = get_around_cor(a, b)
                        around_set = set()
                        for item in around:
                            around_set.add(tuple(item))
                        flagged_around = flagged.intersection(around_set)
                        if len(flagged_around) == blocks[a][b].dangers:
                            for (x, y) in around:
                                if 0<=x<M and 0<=y<N and blocks[x][y].status == 0:
                                    blocks[x][y].status = -1
                                    detected.add((x, y))
                    elif event.button == 1:
                        if both_down == 1:
                            both_down = 0
                        else:
                            blocks[a][b].left_button_up()
                            if blocks[a][b].dangers == 0:
                                safe_zone = find_safe_zone(a, b, M, N, blocks)
                                for (x, y) in safe_zone:
                                    blocks[x][y].status = -1
                                    detected.add((x, y))
                            # fail
                            if blocks[a][b].prop == 1:
                                t = time.time()
                                while time.time()-t < 4:
                                    for _ in pygame.event.get():
                                        pass
                                    message('You Lose!', RED, screen, width, height)
                                pygame.quit()
                            detected.add((a, b))
                            if detected == whole:
                                while True:
                                    for _ in pygame.event.get():
                                        pass
                                    message('You Win!', BLUE, screen, width, height)
                        left_mouse_down = 0
                    elif event.button == 3:
                        if both_down == 1:
                            both_down = 0
                        else:
                            blocks[a][b].right_button_up()
                            if blocks[a][b].status == 1:
                                flagged.add((a, b))
                            else:
                                if (a, b) in flagged:
                                    flagged.remove((a, b))
                        right_mouse_down = 0
                else:
                    blocks[a][b].press = 0
                    if both_down:
                        blocks[a][b].right_left_up(blocks)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                a, b = get_pressed_cor(event.pos)
                blocks[a][b].button_down()
                if event.button == 1:
                    left_mouse_down = 1
                elif event.button == 3:
                    right_mouse_down = 1
                if left_mouse_down and right_mouse_down:
                    both_down = 1
                    blocks[a][b].right_left_down(blocks)

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
