import chess
import pygame
import engine
import random
from pygame.locals import *
import threading

pygame.init()

size = 800
sidebar_size = 250
screen = pygame.display.set_mode((size + sidebar_size, size))
pygame.display.set_caption("Chess")

clock = pygame.time.Clock()
white_time = 300
black_time = 300

engine_delay = random.uniform(0.3, 0.8)
engine_timer = 0
engine_played = False
engine_thinking = False
engine_result = None

board = chess.Board()
field = size//8
pieces = {
    "wp": pygame.transform.scale(pygame.image.load("assets/Pieces/White/wp.png"), (field, field)),
    "wr": pygame.transform.scale(pygame.image.load("assets/Pieces/White/wr.png"), (field, field)),
    "wn": pygame.transform.scale(pygame.image.load("assets/Pieces/White/wn.png"), (field, field)),
    "wb": pygame.transform.scale(pygame.image.load("assets/Pieces/White/wb.png"), (field, field)),
    "wq": pygame.transform.scale(pygame.image.load("assets/Pieces/White/wq.png"), (field, field)),
    "wk": pygame.transform.scale(pygame.image.load("assets/Pieces/White/wk.png"), (field, field)),

    "bp": pygame.transform.scale(pygame.image.load("assets/Pieces/Black/bp.png"), (field, field)),
    "br": pygame.transform.scale(pygame.image.load("assets/Pieces/Black/br.png"), (field, field)),
    "bn": pygame.transform.scale(pygame.image.load("assets/Pieces/Black/bn.png"), (field, field)),
    "bb": pygame.transform.scale(pygame.image.load("assets/Pieces/Black/bb.png"), (field, field)),
    "bq": pygame.transform.scale(pygame.image.load("assets/Pieces/Black/bq.png"), (field, field)),
    "bk": pygame.transform.scale(pygame.image.load("assets/Pieces/Black/bk.png"), (field, field)),
}

running = True
promotion_pending = None
selected_square = None
last_move = None
legal_targets = []
game_ongoing = True
first_move = False

def draw_board():
    for row in range(8):
        for col in range(8):
            board_color = (240, 217, 181) if (col + row) % 2 == 0 else (181, 136, 99)
            pygame.draw.rect(screen, board_color, (col * field, row * field, field, field))

def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)

        if piece:
            file = chess.square_file(square)
            rank = chess.square_rank(square)

            x = file * field
            y = (7 - rank) * field

            color = "w" if piece.color == chess.WHITE else "b"
            symbol = piece.symbol().lower()
            key = color + symbol

            image = pieces[key]
            screen.blit(image, (x, y))

def draw_selected(selected_square):
    file = chess.square_file(selected_square)
    rank = chess.square_rank(selected_square)
    x = file * field
    y = (7 - rank) * field
    pygame.draw.rect(screen, (246, 235, 114) if (file + rank) % 2 != 0 else (220, 195, 75), (x, y, field, field))

def draw_legal_moves(targets, capture_targets):
    for sq in targets:
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)

        x = file * field
        y = (7 - rank) * field

        surf = pygame.Surface((field, field), pygame.SRCALPHA)
        if not sq in capture_targets:
            pygame.draw.circle(surf, (120, 120, 120, 120), (field//2, field//2), field // 6)
        else:
            pygame.draw.circle(surf, (120, 120, 120, 120), (field//2, field//2), field // 2 , 9)
        screen.blit(surf, (x, y))

def get_legal_targets(from_square):
    targets = []
    capture_targets = []
    for move in board.legal_moves:
        if move.from_square == from_square:
            targets.append(move.to_square)
        if board.is_capture(move):
            capture_targets.append(move.to_square)
    return targets, capture_targets

def draw_last_move(last_move):
    if last_move:
        start_file = chess.square_file(last_move.from_square)
        start_rank = chess.square_rank(last_move.from_square)
        x_start = start_file * field
        y_start = (7 - start_rank) * field

        pygame.draw.rect(screen, (246, 235, 114) if (start_file + start_rank) % 2 != 0 else (220, 195, 75), (x_start, y_start, field, field))

        end_file = chess.square_file(last_move.to_square)
        end_rank = chess.square_rank(last_move.to_square)
        x_end = end_file * field
        y_end = (7 - end_rank) * field
        pygame.draw.rect(screen, (246, 235, 114) if (end_file + end_rank) % 2 != 0 else (220, 195, 75), (x_end, y_end, field, field))

def draw_check():
    if board.is_check():
        king_square = board.king(board.turn)

        if king_square is not None:
            file = chess.square_file(king_square)
            rank = chess.square_rank(king_square)

            x = file * field
            y = (7 - rank) * field

            pygame.draw.rect(screen, (255, 85, 60), (x, y, field, field))

def draw_sidebar():
    global game_ongoing
    sidebar_x = size
    sidebar_width = 250

    pygame.draw.rect(screen, (28, 28, 32), (sidebar_x, 0, sidebar_width, size))
    pygame.draw.line(screen, (70, 70, 75), (sidebar_x, 0), (sidebar_x, size), 2)

    title_font = pygame.font.SysFont("arial", 34, bold=True)
    font = pygame.font.SysFont("arial", 28, bold=True)
    small_font = pygame.font.SysFont("arial", 22)

    def format_time(t):
        minutes = int(t) // 60
        seconds = int(t) % 60
        return f"{minutes:02}:{seconds:02}"

    title = title_font.render("Chess", True, (255, 255, 255))
    screen.blit(title, (sidebar_x + 20, 25))

    turn_text = "White to move" if board.turn == chess.WHITE else "Black to move"
    turn_surface = font.render(turn_text, True, (230, 230, 230))
    screen.blit(turn_surface, (sidebar_x + 20, 90))

    if board.is_checkmate():
        if board.turn == chess.WHITE:
            status = "Black wins"
        else:
            status = "White wins"
        status_color = (90, 255, 90)
        game_ongoing = False
    elif board.is_stalemate():
        status = "Stalemate"
        status_color = (255, 210, 120)
        game_ongoing = False
    elif board.is_repetition(3):
        status = "Draw (repetition)"
        status_color = (255, 210, 120)
        game_ongoing = False
    elif board.is_check():
        status = "Check"
        status_color = (255, 120, 120)
    elif white_time == 0:
        status = "Black wins"
        status_color = (90, 255, 90)
    elif black_time == 0:
        status = "White wins"
        status_color = (90, 255, 90)
    else:
        status = "In progress"
        status_color = (180, 180, 180)

    status_label = small_font.render("Status", True, (150, 150, 150))
    status_value = font.render(status, True, status_color)
    screen.blit(status_label, (sidebar_x + 20, 145))
    screen.blit(status_value, (sidebar_x + 20, 170))
    pygame.draw.line(screen, (70, 70, 75), (sidebar_x + 20, 240), (sidebar_x + 230, 240), 1)

    white_label = small_font.render("White", True, (210, 210, 210))
    black_label = small_font.render("Black", True, (210, 210, 210))

    white_clock_color = (255, 255, 255) if board.turn == chess.WHITE else (170, 170, 170)
    black_clock_color = (255, 255, 255) if board.turn == chess.BLACK else (170, 170, 170)

    white_clock = title_font.render(format_time(white_time), True, white_clock_color)
    black_clock = title_font.render(format_time(black_time), True, black_clock_color)

    screen.blit(white_label, (sidebar_x + 20, size//2 + 15))
    screen.blit(white_clock, (sidebar_x + 20, size//2 + 40))

    screen.blit(black_label, (sidebar_x + 20, size//2 - 85))
    screen.blit(black_clock, (sidebar_x + 20, size//2 - 60))

def draw_promotion_menu():
    if promotion_pending is None:
        return

    from_square, to_square = promotion_pending
    moving_piece = board.piece_at(from_square)

    if moving_piece is None:
        return

    color = "w" if moving_piece.color == chess.WHITE else "b"
    options = ["q", "r", "b", "n"]

    panel_y = size // 2 - field // 2
    panel_x = size // 2 - 2 * field

    pygame.draw.rect(screen, (40, 40, 40), (panel_x - 10, panel_y - 10, 4 * field + 20, field + 20))

    for i, option in enumerate(options):
        x = panel_x + i * field

        # tło pojedynczej opcji
        pygame.draw.rect(screen, (230, 230, 230), (x, panel_y, field, field))
        pygame.draw.rect(screen, (80, 80, 80), (x, panel_y, field, field), 1)

        image = pieces[color + option]
        screen.blit(image, (x, panel_y))

def handle_promotion_click(pos):
    global promotion_pending, last_move

    if not promotion_pending:
        return False

    from_square, to_square = promotion_pending
    moving_piece = board.piece_at(from_square)

    if moving_piece is None:
        promotion_pending = None
        return False

    panel_y = size // 2 - field // 2
    panel_x = size // 2 - 2 * field

    x, y = pos

    if not (panel_x <= x < panel_x + 4 * field and panel_y <= y < panel_y + field):
        return False

    index = (x - panel_x) // field
    promotion_map = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]

    chosen_piece = promotion_map[index]
    move_to_handle = chess.Move(from_square, to_square, promotion=chosen_piece)

    if move_to_handle in board.legal_moves:
        board.push(move_to_handle)
        last_move = move_to_handle

    promotion_pending = None
    return True

def drawing():
    draw_board()
    draw_last_move(last_move)
    draw_check()
    if selected_square is not None and game_ongoing:
        draw_selected(selected_square)
        if board.turn:
            draw_legal_moves(legal_targets, capture_targets)
    draw_pieces()
    draw_sidebar()
    if promotion_pending:
        draw_promotion_menu()
    pygame.display.update()

def handle_engine(board):
    global engine_result, engine_thinking
    engine_result = engine.find_best_move(board)
    engine_thinking = False

while running:
    dt = clock.tick(60) / 1000

    for e in pygame.event.get():
        if e.type == pygame.MOUSEBUTTONDOWN:
            if promotion_pending is not None:
                if handle_promotion_click(pygame.mouse.get_pos()):
                    selected_square = None
                    legal_targets = []
                    capture_targets = []
                continue

            pos = pygame.mouse.get_pos()
            board_col = chr(min(ord('a') + (pos[0] // field), ord('h')))
            board_row = min(8 - (pos[1] // field), 8)
            square = chess.parse_square(board_col + str(board_row))
            piece = board.piece_at(square)

            if selected_square is None:
                if piece and piece.color == board.turn:
                    selected_square = square
                    legal_targets, capture_targets = get_legal_targets(square)

            elif selected_square is not None and square in legal_targets and game_ongoing and board.turn:
                if board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(square) in [0, 7]:
                    promotion_pending = (selected_square, square)
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        board.push(move)
                        last_move = move
                    first_move = True
                selected_square = None
                legal_targets = []
                capture_targets = []

            elif piece and piece.color == board.turn:
                selected_square = square
                legal_targets, capture_targets = get_legal_targets(square)

            else:
                selected_square = None
                legal_targets = []
                capture_targets = []

        if e.type == QUIT:
            running = False
        if e.type == KEYDOWN:
            if e.key == K_BACKSPACE:
                running = False

    if board.turn == chess.BLACK and game_ongoing and promotion_pending is None and not board.is_game_over():
        if not engine_thinking and not engine_played and engine_result is None:
            engine_timer += dt

            if engine_timer >= engine_delay:
                engine_thinking = True
                engine_timer = 0
                position_copy = board.copy()
                threading.Thread(target=handle_engine, args=(position_copy,), daemon=True).start()
    else:
        engine_timer = 0

    if engine_result is not None and board.turn == chess.BLACK:
        if engine_result in board.legal_moves:
            board.push(engine_result)
            last_move = engine_result
            first_move = True

        engine_result = None
        engine_played = True

    if board.turn == chess.WHITE:
        engine_played = False

    if not board.is_game_over() and game_ongoing and first_move and promotion_pending is None:
        if board.turn == chess.WHITE:
            white_time = max(0, white_time - dt)
        else:
            black_time = max(0, black_time - dt)

    if white_time == 0 or black_time == 0:
        game_ongoing = False

    drawing()

pygame.quit()