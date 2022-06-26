def get_setup_file():
    try:
        with open("./setup.txt", "r", encoding="utf-8") as f: setup = f.read()
    except FileNotFoundError:
        setup = None
    assert setup, "setup file not found or it is empty"
    return setup


def get_layout(board, jail):
    setup = get_setup_file()
    try:
        pieces, layout = setup.split("layout")
        pieces = dict([(piece[0], globals()[piece[1]]) for piece in filter(lambda line: "=" in line, pieces.split("\n"))])
        layout = [[pieces[cell.strip()[-1]](board, [x, y], cell.strip()[0]) for cell in row.split("|") if cell] for row in filter(lambda line: "-" not in line and line, layout.split("\n"))]
    except: pass
    assert pieces and layout, "setup file is edited poorly..."
    return setup

class Map:
    def __init__(self, jail:bool):
        self.grid = get_layout(board=self, jail=jail)

class Piece:
    def __init__(self, board:Map, position:list[int], side:bool):
        self.board = board
        self.pos = position
        self.side = side

    def move(self, target):
        self.pos = target

class Fish(Piece):
    def move(self, target):
        self.pos = target

print(get_layout())
