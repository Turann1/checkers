import pygame
import sys
import datetime

def restart_game(): # Рестарт игры
    global pieces, select_piece, highlighted_moves, white_score, black_score, current_player, start_time

    pieces = []
    select_piece = None
    highlighted_moves = []
    white_score, black_score = 10, 0
    current_player = 'white'
    start_time = datetime.datetime.now()

    index_pieces = 0
    for row in range(ROWS):
        for col in range(COLS):
            index_pieces += 1
            if (row + col) % 2 != 0:
                x, y = rect_x + col * SQUARE_WIDTH + SQUARE_WIDTH // 2, rect_y + row * SQUARE_HEIGHT + SQUARE_HEIGHT // 2
                if row < 3:
                    pieces.append({'id': index_pieces, 'x': x, 'y': y, 'color': gray_piece, 'original_color': gray_piece, 'type': 'black', 'row': row, 'col': col, 'king': False})
                elif row > 4:
                    pieces.append({'id': index_pieces, 'x': x, 'y': y, 'color': white_piece, 'original_color': white_piece, 'type': 'white', 'row': row, 'col': col, 'king': False})

pygame.init()

WIDTH, HEIGHT = 1000, 700 # Размеры фрейма
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Шашки") # Заголовок

background = (36, 36, 36)
white_square = (255, 255, 255)
black_square = (0, 0, 0)
gray_piece = (60, 57, 57)
white_piece = (255, 255, 255)
highlight_color = (0, 255, 0)
king_border_color = (255, 0, 0)

clock = pygame.time.Clock()
FPS = 144

# Размеры игровой доски
ROWS = 8
COLS = 8
BOARD_WIDTH = 700
BOARD_HEIGHT = 600

SQUARE_WIDTH, SQUARE_HEIGHT = BOARD_WIDTH // COLS, BOARD_HEIGHT // ROWS
PIECE_RADIUS = min(SQUARE_WIDTH, SQUARE_HEIGHT) // 2 - 10

rect_x, rect_y = (WIDTH - BOARD_WIDTH) // 2, (HEIGHT - BOARD_HEIGHT) // 2
pieces, select_piece, highlighted_moves = [], None, []
white_score, black_score = 0, 0

current_player = 'white'
start_time = datetime.datetime.now()
end_game = datetime.datetime.now()
restart_game()

def get_play_time(stop:bool=None) -> str:
    if stop:
        elapsed_time = end_game - start_time
        elapsed_formatted = (datetime.datetime(1, 1, 1) + elapsed_time).strftime('%H:%M:%S')
        return elapsed_formatted
    current_time = datetime.datetime.now()
    elapsed_time = current_time - start_time
    elapsed_formatted = (datetime.datetime(1, 1, 1) + elapsed_time).strftime('%H:%M:%S')
    return elapsed_formatted

def get_piece_at_position(row, col):
    for piece in pieces:
        if piece['row'] == row and piece['col'] == col:
            return piece
    return None

def get_valid_moves(piece):
    moves = []
    if piece['type'] == 'black':
        directions = [(1, -1), (1, 1)]
        capture_directions = [(2, -2), (2, 2)]
    elif piece['type'] == 'white':
        directions = [(-1, -1), (-1, 1)]
        capture_directions = [(-2, -2), (-2, 2)]
    else:
        return moves

    if piece['king']:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        capture_directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]

    for dr, dc in directions:
        new_row, new_col = piece['row'] + dr, piece['col'] + dc
        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
            if not get_piece_at_position(new_row, new_col):
                x = rect_x + new_col * SQUARE_WIDTH + SQUARE_WIDTH // 2
                y = rect_y + new_row * SQUARE_HEIGHT + SQUARE_HEIGHT // 2
                moves.append({'row': new_row, 'col': new_col, 'x': x, 'y': y, 'capture': None})

    for (dr, dc), (cr, cc) in zip(capture_directions, directions):
        capture_row, capture_col = piece['row'] + cr, piece['col'] + cc
        new_row, new_col = piece['row'] + dr, piece['col'] + dc
        if 0 <= new_row < ROWS and 0 <= new_col < COLS and 0 <= capture_row < ROWS and 0 <= capture_col < COLS:
            enemy_piece = get_piece_at_position(capture_row, capture_col)
            if enemy_piece and enemy_piece['type'] != piece['type'] and not get_piece_at_position(new_row, new_col):
                x = rect_x + new_col * SQUARE_WIDTH + SQUARE_WIDTH // 2
                y = rect_y + new_row * SQUARE_HEIGHT + SQUARE_HEIGHT // 2
                moves.append({'row': new_row, 'col': new_col, 'x': x, 'y': y, 'capture': enemy_piece})
    return moves

def promote_to_king(piece):
    if piece['type'] == 'white' and piece['row'] == 0:
        piece['king'] = True
    elif piece['type'] == 'black' and piece['row'] == ROWS - 1:
        piece['king'] = True

running, show_victory_screen = True, False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if show_victory_screen:
                restart_game()
                show_victory_screen = False
                continue

            mouse_x, mouse_y = event.pos
            for move in highlighted_moves:
                distance = ((mouse_x - move['x'])**2 + (mouse_y - move['y'])**2)**0.5
                if distance < PIECE_RADIUS:
                    if select_piece['type'] != current_player:
                        break
                    select_piece['row'], select_piece['col'] = move['row'], move['col']
                    select_piece['x'], select_piece['y'] = move['x'], move['y']

                    if move['capture']:
                        pieces.remove(move['capture'])
                        if select_piece['type'] == 'white':
                            white_score += 1
                        else:
                            black_score += 1

                    promote_to_king(select_piece)
                    current_player = 'black' if current_player == 'white' else 'white'
                    highlighted_moves, select_piece = [], None

                    if white_score == 12 or black_score == 12:
                        end_game = datetime.datetime.now()
                        show_victory_screen = True
                    break
            else:
                for piece in pieces:
                    distance = ((mouse_x - piece['x'])**2 + (mouse_y - piece['y'])**2)**0.5
                    if distance < PIECE_RADIUS:
                        if select_piece == piece:
                            select_piece, highlighted_moves = None, []
                        else:
                            if piece['type'] == current_player:
                                select_piece, highlighted_moves = piece, get_valid_moves(piece)
                        break

    screen.fill(background)

    if show_victory_screen:
        font = pygame.font.SysFont(None, 72)
        victory_text = font.render(f"{'Белые' if white_score == 12 else 'Чёрные'} выиграли!", True, (255, 255, 255))
        screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - 50))

        font = pygame.font.SysFont(None, 48)
        restart_text = font.render("Нажмите для перезапуска", True, (255, 255, 255))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

        elapsed_formatted = get_play_time(stop=True)

        time_text = font.render(f"Время игры: {elapsed_formatted}", True, (255, 255, 255))
        screen.blit(time_text, (WIDTH - 675, 660))

        pygame.display.flip()
        continue

    for row in range(ROWS):
        for col in range(COLS):
            color = white_square if (row + col) % 2 == 0 else black_square
            pygame.draw.rect(screen, color, (
                rect_x + col * SQUARE_WIDTH,
                rect_y + row * SQUARE_HEIGHT,
                SQUARE_WIDTH,
                SQUARE_HEIGHT
            ))

    for move in highlighted_moves:
        pygame.draw.circle(screen, highlight_color, (move['x'], move['y']), PIECE_RADIUS // 3)

    for piece in pieces:
        pygame.draw.circle(screen, piece['color'], (piece['x'], piece['y']), PIECE_RADIUS)
        if piece['king']:
            pygame.draw.circle(screen, king_border_color, (piece['x'], piece['y']), PIECE_RADIUS + 5, 3)

    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Белые: {white_score} | Чёрные: {black_score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    player_text = font.render(f"Ходит: {current_player.capitalize()}", True, (255, 255, 255))
    screen.blit(player_text, (WIDTH - 200, 20))

    elapsed_formatted = get_play_time()

    time_text = font.render(f"Время игры: {elapsed_formatted}", True, (255, 255, 255))
    screen.blit(time_text, (WIDTH - 645, 660))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
