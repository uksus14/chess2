from functools import reduce
from math import sin, cos
from time import time
from math import exp
import pygame as pg

PIX_PER_CELL = 87
BOARD_OFFSET = 100
HEIGHT, WIDTH = [8*PIX_PER_CELL+2*BOARD_OFFSET]*2
FPS = 60
BG_COLOR = (100, 100, 100)

def l(path):
    try:
        surf = pg.image.load(f"media/{path}_t.bmp")
        pg.Surface.set_colorkey(surf, (255, 255, 255))
    except:
        surf = pg.image.load("media/test.bmp")
    surf = pg.transform.scale(surf, (PIX_PER_CELL, PIX_PER_CELL))
    return surf
placeholder = l("")
banana = l("banana")
king =   [l(s+"king")    for s in"bw"]
qfish =  [l(s+"qfish")   for s in"bw"]
queen =  [l(s+"queen")   for s in"bw"]
elephant=[l(s+"elephant")for s in"bw"]
fish =   [l(s+"fish")    for s in"bw"]
monke =  [l(s+"monke")   for s in"bw"]
rook =   [l(s+"rook")    for s in"bw"]

def grid_to_pix(pos):
    return [pos[i]*PIX_PER_CELL+BOARD_OFFSET for i in range(2)]

def between(board, pos1, pos2):
    diff = [int(i1<i2)*2-1 if i1!=i2 else 0 for i1, i2 in zip(pos1, pos2)]
    pos1 = [pos1[i]+diff[i]if diff[i]else pos1[i]for i in[0,1]]
    while pos1 != pos2:
        if board.get_piece(pos1):
            return True
        pos1 = [pos1[i]+diff[i]if diff[i]else pos1[i]for i in[0,1]]
    return False

def pix_to_grid(pos):
    coord = list(map(lambda i:(i-BOARD_OFFSET)//PIX_PER_CELL, pos))
    return coord

class Animations:
    def shake(pos, start, speed):
        countdown = (time()-start)*speed
        pos[0] += 10*sin(countdown)
        return pos
    def rise(pos, start, speed):
        countdown = (time()-start)*speed
        pos[1] -= 5*(1-exp(-countdown))
        return pos

class Map:
    def __init__(self, jail:bool):
        self.grid = get_layout(board=self, jail=jail)
        [[piece.init() for piece in row if piece] for row in self.grid]
    def get_piece(self, pos):
        if all(map(lambda i:abs(i-3.5)<4, pos)):
            return self.grid[pos[1]][pos[0]]
        return "out"
    def draw(self):
        screen.fill(BG_COLOR)
        [[cell.draw() for cell in row if cell] for row in self.grid]
    def is_piece_selected(self):
        is_selected = {}
        [[is_selected.update({piece.selected:piece}) for piece in row if piece] for row in self.grid]
        if True in is_selected.keys():
            return is_selected[True]
        return None

class Piece:
    def __init__(self, board:Map, position:list[int], side:bool):
        self.board = board
        self.pos = position
        self.side = side
        self.animations = {}
        self.sprite = placeholder
        self.selected = False

    def select(self):
        [self.animations.update({anim:(time(), speed)}) for anim, speed in SELECT_ANIMS]
        self.selected = True
    def deselect(self):
        [self.animations.pop(anim) for anim, speed in SELECT_ANIMS]
        self.selected = False
    def move(self, target):
        grid, pos = self.board.grid, self.pos
        grid[target[1]][target[0]] = grid[pos[1]][pos[0]]
        grid[pos[1]][pos[0]] = None
        self.pos = target
        self.deselect()
    def draw(self):
        draw_pos = reduce(lambda pos,anim:anim[0](pos, anim[1][0], anim[1][1]), [grid_to_pix(self.pos)]+list(self.animations.items()))
        screen.blit(self.sprite, self.sprite.get_rect(topleft=draw_pos))

"""
v1.0
c = Castle
b = Bishop
q = Queen
k = King
p = Pawn
h = Horse

v2.0
r = Rook
m = Monke
f = Fish
F = SuperFish
e = Elephant
"""

class Castle(Piece):
    def init(self):
        self.sprite = castle
    def move(self, target):
        if all([target[i] not in self.pos for i in range(2)]):
            return self, Animations.shake
        self.pos = target

class Fish(Piece):
    def init(self):
        self.sprite = fish[int(self.side)]
    def move(self, target):
        diff = tuple([i1-i2 for i1, i2 in zip(target, self.pos)])
        to_move = [
            (-1,1),(0,1),(1,1),
            (-1,0),(0,0),(1,0),
        ]
        to_take = [
            (-1,1),     (1,1),
                   (0,0),
        ]
        if self.side:
            to_take, to_move = [[(x,-y) for x,y in l] for l in (to_take, to_move)]
        take = self.board.get_piece(target)
        go = False
        if take:
            if take.side != self.side and diff in to_take:
                go = True
        elif diff in to_move:
            go = True
        if go:
            super().move(target)
            if target[1] == int(not self.side)*7:
                self.board.grid[target[1]][target[0]] = QFish(self.board, target, self.side).init()
            return "end-move"

class QFish(Piece):
    def init(self):
        self.sprite = qfish[int(self.side)]
        return self
    def move(self, target):
        diff = tuple([i1-i2 for i1, i2 in zip(target, self.pos)])
        to_move = [(x,0) for x in range(-7,7)]+[(0,y) for y in range(-7,7)]+[(i,-i) for i in range(-7,7)]+[(i,i) for i in range(-7, 7)]
        take = self.board.get_piece(target)
        go = False
        if take:
            if take.side != self.side and diff in to_move and not between(self.board, self.pos, target):
                go = True
        elif diff in to_move and not between(self.board, self.pos, target):
            go = True
        if go:
            super().move(target)
            return "end-move"


def get_setup_file():
    try:
        with open("./setup.txt", "r", encoding="utf-8") as f: setup = f.read()
    except FileNotFoundError:
        setup = None
    assert setup, "setup file not found or it is empty"
    return setup


def get_layout(board, jail):
    setup = get_setup_file()
    grid = []
    grid = [[Fish(board, [x, y], bool(y//4)) if abs(y-3.5)>2 else None for x in range(8)] for y in range(8)]
    try:
        12/0
        pieces, layout = setup.split("layout")
        pieces = dict([(piece[0], globals()[piece[1]]) for piece in filter(lambda line: "=" in line, pieces.split("\n"))])
        layout = [[cell.strip() for cell in row.split("|")] for row in layout.split("\n") if "-" not in row]
        for y in range(8):
            grid.append([])
            for x in range(8):
                cell = layout[y][x]
                if cell:
                    grid[-1].append(pieces[cell[-1]](board, [x, y], cell[0]))
                else:
                    grid[-1].append(None)
    except: pass
    assert grid, "setup file is edited poorly..."
    return grid


SELECT_ANIMS = [(Animations.shake, 10), (Animations.rise, 5)]
board = Map(jail=False)

clock = pg.time.Clock()
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
run = True
while run:
    for event in pg.event.get():
        if event.type in [pg.QUIT, pg.K_ESCAPE]:
            run = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = pg.mouse.get_pos()
                pos = pix_to_grid(pos)
                piece = board.get_piece(pos)
                is_selected = board.is_piece_selected()
                if is_selected:
                    if is_selected == piece:
                        piece.deselect()
                        print("piece deselected")
                    elif piece != "out":
                        is_selected.move(pos)
                        print("piece moved")
                    else:
                        print("target is out")
                elif piece:
                    piece.select()
                    print("piece selected")
    board.draw()
    pg.display.update()
    clock.tick(FPS)

"""
1 1 1
0 1 1
1 0 1
0 0 0
"""