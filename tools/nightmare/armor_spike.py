"""Prototipo aislado: no forma parte del generador ni del juego.

9 = blindaje intacto, 10 = blindaje dañado. Una fila completa con 9
se agrieta y abre la primera celda normal; no cuenta como línea. El ataque
solo debe crear filas con nueve celdas blindadas y un hueco.
"""
WIDTH = 10
HEIGHT = 20
INTACT, DAMAGED = 9, 10


def resolve(board):
    if len(board) != HEIGHT or any(len(row) != WIDTH for row in board):
        raise ValueError('expected 20x10 board')
    out = []
    cleared = damaged = 0
    for row in board:
        row = list(row)
        if all(row):
            if INTACT in row:
                normal = next((i for i, cell in enumerate(row) if cell not in (INTACT, DAMAGED)), None)
                if normal is None:
                    raise ValueError('armored row lacks a removable normal cell')
                row = [DAMAGED if cell == INTACT else cell for cell in row]
                row[normal] = 0
                damaged += 1
                out.append(row)
            else:
                cleared += 1
        else:
            out.append(row)
    return [[0] * WIDTH for _ in range(cleared)] + out, cleared, damaged


def insert_armor(board, hole):
    if not 0 <= hole < WIDTH:
        raise ValueError('invalid hole')
    if any(board[0]):
        return [list(row) for row in board], True
    row = [INTACT] * WIDTH
    row[hole] = 0
    return [list(row) for row in board[1:]] + [row], False


def empty():
    return [[0] * WIDTH for _ in range(HEIGHT)]
