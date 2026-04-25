import chess
import random

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

PAWN_TABLE = [
      0,   0,   0,   0,   0,   0,   0,   0,
     50,  50,  50,  50,  50,  50,  50,  50,
     10,  10,  20,  30,  30,  20,  10,  10,
      5,   5,  10,  25,  25,  10,   5,   5,
      0,   0,   0,  20,  20,   0,   0,   0,
      5,  -5, -10,   0,   0, -10,  -5,   5,
      5,  10,  10, -20, -20,  10,  10,   5,
      0,   0,   0,   0,   0,   0,   0,   0
]

KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]

ROOK_TABLE = [
      0,   0,   5,  10,  10,   5,   0,   0,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
      5,  10,  10,  10,  10,  10,  10,   5,
      0,   0,   5,  10,  10,   5,   0,   0
]

QUEEN_TABLE = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   0,   0,   0,   5,   0, -10,
    -10,   0,   5,   5,   5,   5,   5, -10,
     -5,   0,   5,   5,   5,   5,   0,  -5,
      0,   0,   5,   5,   5,   5,   0,  -5,
    -10,   5,   5,   5,   5,   5,   0, -10,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20
]

KING_TABLE = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
     20,  20,   0,   0,   0,   0,  20,  20,
     20,  30,  10,   0,   0,  10,  30,  20
]

PIECE_SQUARE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE
}

MAX, MIN = float('inf'), float('-inf')

def evaluate_board(board):
    score = 0
    if board.is_checkmate():
        return -99999999 if board.turn == chess.WHITE else 99999999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    for piece_type in PIECE_VALUES:
        for square in board.pieces(piece_type, chess.WHITE):
            piece_value = PIECE_VALUES[piece_type]
            piece_table = PIECE_SQUARE_TABLES[piece_type]
            weight = piece_table[square]
            score += piece_value + weight

        for square in board.pieces(piece_type, chess.BLACK):
            piece_value = PIECE_VALUES[piece_type]
            piece_table = PIECE_SQUARE_TABLES[piece_type]
            weight = piece_table[chess.square_mirror(square)]
            score -= piece_value + weight

    return score

def score_move(board, move):
    if board.is_capture(move):
        victim = board.piece_type_at(move.to_square)
        attacker = board.piece_type_at(move.from_square)
        if victim is None:
            return 10 + PIECE_VALUES[chess.PAWN] - PIECE_VALUES[attacker]
        if attacker is None:
            return 0
        return PIECE_VALUES[victim] - PIECE_VALUES[attacker]
    return 0

def evaluate_move(board, move):
    attacker_type = board.piece_type_at(move.from_square)
    if attacker_type is None:
        return 0

    piece = board.piece_at(move.from_square)
    color = piece.color
    table = PIECE_SQUARE_TABLES[attacker_type]

    if color == chess.WHITE:
        before = table[move.from_square]
        after = table[move.to_square]
        sign = 1
    else:
        before = table[chess.square_mirror(move.from_square)]
        after = table[chess.square_mirror(move.to_square)]
        sign = -1

    delta = after - before

    if board.is_capture(move):
        victim_type = board.piece_type_at(move.to_square)

        if victim_type is None:
            victim_value = PIECE_VALUES[chess.PAWN]  # en passant
        else:
            victim_value = PIECE_VALUES[victim_type]

        delta += victim_value

    return sign * delta

def min_max_move_with_alpha_beta(board, evaluation, alpha=MIN, beta=MAX, depth=3):
    if depth == 0 or board.is_game_over():
        return evaluation

    moves = list(board.legal_moves)
    moves.sort(key=lambda m: score_move(board, m), reverse=True)

    if board.turn:
        best_score = MIN

        for move in moves:
            delta = evaluate_move(board, move)
            board.push(move)
            best_score = max(best_score, min_max_move_with_alpha_beta(board, evaluation + delta, alpha, beta, depth-1))
            alpha = max(best_score, alpha)
            board.pop()
            if beta <= alpha:
                break

        return best_score
    else:
        best_score = MAX
        for move in moves:
            delta = evaluate_move(board, move)
            board.push(move)
            best_score = min(best_score, min_max_move_with_alpha_beta(board, evaluation + delta, alpha, beta, depth-1))
            beta = min(best_score, beta)
            board.pop()
            if beta <= alpha:
                break

        return best_score

def find_best_move(board):
    if board.turn:
        best_score = float('-inf')
    else:
        best_score = float('inf')
    best_move = []
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: board.is_capture(m), reverse=True)

    current_eval = evaluate_board(board)
    for move in moves:
        delta = evaluate_move(board, move)
        board.push(move)
        score = min_max_move_with_alpha_beta(board, current_eval + delta)
        board.pop()
        if board.turn:
            if score > best_score:
                best_score = score
                best_move = [move]
            elif score == best_score:
                best_move.append(move)
        else:
            if score < best_score:
                best_score = score
                best_move = [move]
            elif score == best_score:
                best_move.append(move)

    return random.choice(best_move)

BOARD = chess.Board()
BOARD.push(chess.Move.from_uci("e2e4"))

