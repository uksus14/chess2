from functools import reduce
from math import sin, cos
from time import time
from math import exp
import pygame as pg

PIX_PER_CELL = 87
BOARD_OFFSET = 100
HEIGHT, WIDTH = [8*PIX_PER_CELL+2*BOARD_OFFSET]*2
FPS = 60
antiBLUE = (155, 55, 0)
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

def diff(pos1, pos2):
    return tuple([i1-i2 for i1, i2 in zip(pos2, pos1)])

def hflip(*ls):
    answers = []
    for l in ls:
        answers.append([(x,-y) for x,y in l])
    return answers

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
    def shake(pos, start, speed, duration):
        if duration is None:
            return Animations.shake(pos, start, speed, time()-start+1)
        elif time()<start+duration:
            countdown = (time()-start)*speed
            pos[0] += 10*sin(countdown)
        return pos
    def rise(pos, start, speed, duration):
        if duration is None:
            return Animations.rise(pos, start, speed, time()-start+1)
        elif time()<start+duration:
            countdown = (time()-start)*speed
            pos[1] -= 5*(1-exp(-countdown))
        return pos
    def spin(pos, start, speed, duration):
        if duration is None:
            return Animations.spin(pos, start, speed, time()-start+1)
        elif time()<start+duration:
            countdown = (time()-start)*speed
            pos[0] += 3*cos(countdown)
            pos[1] += 3*sin(countdown)
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
        [[pg.draw.rect(screen, tuple([255-_1*_2 for _1, _2 in zip([(x+y)%2]*3, antiBLUE)]), (x*PIX_PER_CELL+BOARD_OFFSET, y*PIX_PER_CELL+BOARD_OFFSET, PIX_PER_CELL, PIX_PER_CELL)) for x in range(8)] for y in range(8)]
        [[cell.draw() for cell in row if cell] for row in self.grid]
    def is_piece_selected(self):
        is_selected = {}
        [[is_selected.update({piece.selected:piece}) for piece in row if piece] for row in self.grid]
        if True in is_selected.keys():
            return is_selected[True]
        return None
    def is_danger(self, pos):
        danger = set()
        [[danger.union(*piece.atacks()) for piece in row if piece] for y, row in enumerate(self.grid)]
        print(danger)
class Piece:
    def __init__(self, board:Map, position:list[int], side:bool):
        self.board = board
        self.pos = position
        self.side = side
        self.animations = {}
        self.sprite = placeholder
        self.selected = False
        self.to_move = [(0, 0)]
        self.is_important = False
        self.to_take = [(0, 0)]

    def select(self):
        if Animations.spin in self.animations.keys():
            self.animations.pop(Animations.spin)
        [self.animations.update({anim:(time(), speed, duration)}) for anim, speed, duration in SELECT_ANIMS]
        self.selected = True
    def deselect(self):
        [self.animations.pop(anim) for anim, speed, duration in SELECT_ANIMS]
        self.selected = False
    def move(self, target):
        shift = diff(self.pos, target)
        take = self.board.get_piece(target)
        if between(self.board, self.pos, target):
            return False
        if take:
            if take.side == self.side or shift not in self.to_take:
                return False
        elif shift not in self.to_move:
            return False
        
        if self.is_important:
            danger = self.board.is_danger(target)
            if danger:
                danger.animations.update({Animations.shake: (time(), 14, 0.5)})
        grid, pos = self.board.grid, self.pos
        take = self.board.get_piece(target)
        if take:
            if take.is_important:
                self.board.add_to_jail(take)
        grid[target[1]][target[0]] = self
        grid[pos[1]][pos[0]] = None
        self.pos = target
        self.deselect()
    def draw(self):
        draw_pos = reduce(lambda pos,anim:anim[0](pos, *anim[1]), [grid_to_pix(self.pos)]+list(self.animations.items()))
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

class King(Piece):
    def init(self):
        self.sprite = king[int(self.side)]
        self.animations.update({Animations.spin:(time(), 3, None)})
        self.to_move = [
            (-1, 1),(0, 1),(1, 1),
            (-1, 0),(0, 0),(1, 0),
            (-1,-1),(0,-1),(1,-1),
        ]
        self.to_take = self.to_move
        self.is_important = True
        return self
class Castle(Piece):
    def init(self):
        self.sprite = castle[int(self.side)]
        self.to_move = [(x,0) for x in range(-7,7)]+[(0,y) for y in range(-7,7)]
        self.to_take = self.to_move
        return self
class Fish(Piece):
    def init(self):
        self.sprite = fish[int(self.side)]
        self.to_move = [
            (-1,1),(0,1),(1,1),
            (-1,0),(0,0),(1,0),
        ]
        self.to_take = [
            (-1,1),     (1,1),
                   (0,0),
        ]
        if self.side:
            self.to_take, self.to_move = hflip(self.to_take, self.to_move)
        return self
    def move(self, target):
        answer = super().move(target)
        if self.pos[1] == int(not self.side)*7:
            self.board.grid[self.pos[1]][self.pos[0]] = QFish(self.board, target, self.side).init()
        return answer

class QFish(Piece):
    def init(self):
        self.sprite = qfish[int(self.side)]
        self.animations.update({Animations.spin:(time(), 3, None)})
        self.to_move = [(x,0) for x in range(-7,7)]+[(0,y) for y in range(-7,7)]+[(i,-i) for i in range(-7,7)]+[(i,i) for i in range(-7, 7)]
        self.to_take = self.to_move
        return self

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
    grid[0][4], grid[-1][4] = King(board, [4, 0], False), King(board, [4, 7], True)
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


SELECT_ANIMS = [(Animations.shake, 7, None), (Animations.rise, 5, None)]
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
                elif piece!="out" and piece:
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