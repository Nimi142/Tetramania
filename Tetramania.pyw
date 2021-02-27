# TODO: Start using rect objects
# TODO: Fix Preview inconsistency, add combos (optional), use monospace font for score
"""
A Tetris board is 20x10, although 24x10 is preferred.
"""
import random
from sys import exit as sexit
from typing import List
import contextlib
with contextlib.redirect_stdout(None):
    import pygame


from Extras import *
import time
# Constants
inactive_color = "grey"
stroke_color = "black"
board_color = (64, 64, 64)
canvas_size = 600  # For both axis
board_dims = np.array([10, 24])
tile_size = 20
stroke_size = 2
board_size = board_dims * (tile_size + 1.5 * stroke_size) + stroke_size / 2
board_upper_left = [canvas_size / 2 - board_size[0] / 2, canvas_size / 2 - board_size[1] / 2]
# Global vars
board = [[0 for j in range(0, board_dims[0])] for i in range(0, board_dims[1])]
shapes = [ShapeType.I, ShapeType.J, ShapeType.L, ShapeType.O, ShapeType.Z, ShapeType.S, ShapeType.T]
block_packet: List[ShapeType] = shapes.copy()
random.shuffle(block_packet)
time_ground_left = -1
ground_moves = -1
ground_time = 0
held_shape = None
can_hold = True
score = 0
level = 1
clears_in_level = 0
should_silhouette = True
is_paused = False
# Static stuff
Shape.board_upper_left = board_upper_left
Shape.tile_size = tile_size
Shape.stroke_size = stroke_size
Shape.stroke_color = stroke_color
Shape.background_color = board_color
# Code

# Functions


def update_silhouette(should_clear=True, add_val=0):
    global sil_shape
    global score
    if not should_silhouette:
        return
    if should_clear and sil_shape is not None:
        sil_shape.clear()
    sil_shape = Shape(screen, current_shape.type, True)
    sil_shape.move_to(current_shape.pos)  # Copy position
    sil_shape.block_pos = np.copy(current_shape.block_pos)  # Copy rotation
    # Making Game crash:
    while move_with_checks(sil_shape, [1, 0]):
        score += add_val
    sil_shape.draw()


def draw_new_shape() -> ShapeType:
    global block_packet
    if len(block_packet) < 4:
        new_shapes = shapes.copy()
        random.shuffle(new_shapes)
        block_packet = new_shapes + block_packet
    # TODO: Update preview
    pygame.draw.rect(screen, board_color,
                     pygame.Rect(board_upper_left[0] + board_size[0] + 50, preview_text_rect[1] + preview_text_rect[3],
                                 preview_text_rect[2] / 1.5, preview_text_rect[2] * 2))
    for i in range(2, 5):
        Shape(screen, block_packet[-i]).draw_preview(np.array([board_upper_left[0] + board_size[0] + 50, preview_text_rect[1] + preview_text_rect[3]]), i - 2, np.array([preview_text_rect[2] / 2, preview_text_rect[2] * 2]))
    return block_packet.pop()

def move_with_checks(shape: Shape, direction: List[int], is_hard_drop=False) -> bool:
    global current_shape
    global sil_shape
    global touching_ground
    global ground_time
    global ground_moves
    global time_ground_left
    global can_hold
    global score
    global clears_in_level
    global level
    if is_paused:
        return False
    res = True
    new_locs = shape.get_block_location(direction)
    for loc in new_locs:
        if loc[0] < 0 or loc[0] >= board_dims[1] or loc[1] < 0 or loc[1] >= board_dims[0]:
            res = False
        elif board[loc[0]][loc[1]] != 0:
            res = False
    if res:
        # Movement
        shape.move_direction(direction)
        # Silhouette
        if shape.is_silhouette:
            return True
        update_silhouette()
        # Line clears
        is_clear = 0
        for row in board:
            if not 0 in row:
                board.remove(row)
                board.insert(0, [0 for i in range(board_dims[0])])
                is_clear += 1
        if is_clear != 0:
            # Rudimentary Scoring
            if is_clear == 1:
                score += 100 * level
            elif is_clear == 2:
                score += 300 * level
            elif is_clear == 3:
                score += 500 * level
            elif is_clear == 4:
                score += 800 * level
            # Leveling up
            clears_in_level += is_clear
            if clears_in_level > 10:
                level += 1
                clears_in_level = 0
            # Others
            # Clear!
            pygame.draw.rect(screen, board_color,
                             pygame.Rect(board_upper_left[0], board_upper_left[1], board_size[0], board_size[1]))
            for row in range(len(board)):
                for col in range(len(board[row])):
                    if board[row][col] != 0:
                        # Draw
                        pos = (np.array([row, col])) * (Shape.tile_size + 1.5 * Shape.stroke_size) + Shape.board_upper_left[::-1]
                        all_size = tile_size + stroke_size
                        color = board[row][col]
                        pygame.draw.rect(screen, stroke_color,
                                         pygame.Rect(pos[1], pos[0], Shape.tile_size + 2 * Shape.stroke_size,
                                                     Shape.tile_size + 2 * Shape.stroke_size))
                        pygame.draw.rect(screen, color,
                                         pygame.Rect(pos[1] + Shape.stroke_size, pos[0] + Shape.stroke_size,
                                                     Shape.tile_size, Shape.tile_size))
            update_silhouette()
            pygame.display.flip()
        return True
    else:
        if shape.is_silhouette:
            return False
        if direction != [1, 0] or shape.is_silhouette:
            return False
        if not is_hard_drop:
            if ground_moves == -1:
                ground_time = time.time_ns() / 1_000_000
                ground_moves += 1
            if ground_moves != -1:
                ground_moves += 1
                time_ground_left += 100 / (1.2 ** ground_moves)

            if time.time_ns() / 1_000_000 - ground_time >= time_ground_left:
                ground_time = -1
                ground_moves = -1
                time_ground_left = 0
            else:
                return False
        can_hold = True
        for loc in shape.get_block_location():
            board[loc[0]][loc[1]] = shape.color
        current_shape.draw()
        current_shape = Shape(screen, draw_new_shape())
        # Check if dead
        for pos in current_shape.get_block_location():
            if board[pos[0]][pos[1]] != 0:
                restart()
                return False
            update_silhouette(False)
        current_shape.draw()
        return False


def restart():
    global score
    global board
    global block_packet
    global held_shape
    global sil_shape
    global current_shape
    global level
    board = [[0 for j in range(0, board_dims[0])] for i in range(0, board_dims[1])]
    shapes_cpy = shapes.copy()
    random.shuffle(shapes_cpy)
    block_packet = shapes_cpy
    held_shape = None
    sil_shape = None
    # Drawing Preview
    current_shape = Shape(screen, draw_new_shape())
    # Drawing holding cell
    pygame.draw.rect(screen, board_color,
                     pygame.Rect(hold_text_rect[0], hold_text_rect[1] + hold_text_rect[3], hold_text_rect[2],
                                 hold_text_rect[2]))
    # Drawing empty board
    pygame.draw.rect(screen, board_color,
                     pygame.Rect(board_upper_left[0], board_upper_left[1], board_size[0], board_size[1]))
    score = 0
    level = 0

def is_vacant(positions):
    for pos in positions:
        if pos[0] < 0 or pos[0] >= board_dims[1] or pos[1] < 0 or pos[1] >= board_dims[0]:
            return False
        elif board[pos[0]][pos[1]] != 0:
            return False
    return True


# Configure screen
pygame.init()
screen = pygame.display.set_mode((canvas_size, canvas_size))
try:
    pygame.display.set_icon(pygame.image.load("logo.png"))
except FileNotFoundError:
    print("Couldn't find logo! Running anyway....")
pygame.display.set_caption('TetraMania')
clock = pygame.time.Clock()
pygame.draw.rect(screen, inactive_color, pygame.Rect(0, 0, 600, 600))
# Draw board background
pygame.draw.rect(screen, board_color,
                 pygame.Rect(board_upper_left[0], board_upper_left[1], board_size[0], board_size[1]))
# Setting holding cell
font = pygame.font.Font('Roboto-Black.ttf', 50)
hold_text = font.render('Hold', True, (64, 64, 64), "grey")
hold_text_rect = hold_text.get_rect()
screen.blit(hold_text, hold_text_rect)
pygame.draw.rect(screen, board_color,
                 pygame.Rect(hold_text_rect[0], hold_text_rect[1] + hold_text_rect[3], hold_text_rect[2], hold_text_rect[2]))
# Setting preview cell
preview_text = font.render('Preview', True, (64, 64, 64), "grey")
preview_text_rect = preview_text.get_rect()
screen.blit(preview_text, pygame.Rect(board_upper_left[0] + board_size[0], preview_text_rect[1], preview_text_rect[2], preview_text_rect[3]))
pygame.draw.rect(screen, board_color,
                 pygame.Rect(board_upper_left[0] + board_size[0] + 50, preview_text_rect[1] + preview_text_rect[3], preview_text_rect[2] / 2, preview_text_rect[2] * 2))
# Setting Score level
score_font = pygame.font.Font('RobotoMono.ttf', 15)
score_text = score_font.render("Score: 000000; Level: 00", True, (64, 64, 64), "grey")
screen.blit(score_text, pygame.Rect(board_upper_left[0], 0, score_text.get_rect()[2], score_text.get_rect()[3]))
# Update display
pygame.display.flip()

current_shape = Shape(screen, draw_new_shape())
sil_shape = None
is_up_pressed, is_down_pressed, is_left_pressed, is_right_pressed = 0, 0, 0, 0
input_period = 6
frame_num = -1  # To make first frame mod 60 be 0
while True:
    frame_num += 1
    if frame_num % (60 // (1.2 ** level)) == 0 and True:
        move_with_checks(current_shape, [1, 0])
    events = pygame.event.get()
    key_pressed = pygame.key.get_pressed()
    for event in events:
        if event.type == pygame.QUIT:
            sexit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                while move_with_checks(current_shape, [1, 0], True):
                    pass
            if event.key == pygame.K_c:
                if not can_hold:
                    continue
                if held_shape is None:
                    held_shape = draw_new_shape()
                ground_time = -1
                ground_moves = -1
                time_ground_left = 0
                current_shape.clear()
                temp_type = current_shape.type
                pygame.draw.rect(screen, board_color,
                                 pygame.Rect(hold_text_rect[0], hold_text_rect[1] + hold_text_rect[3], hold_text_rect[2], hold_text_rect[2]))
                Shape(screen, current_shape.type).draw_hold(np.array([hold_text_rect[0], hold_text_rect[1] + hold_text_rect[3]]), hold_text_rect[2])
                current_shape = Shape(screen, held_shape)
                # Check if dead
                for pos in current_shape.get_block_location():
                    if board[pos[0]][pos[1]] != 0:
                        restart()
                        break
                # Create Silhouette
                held_shape = temp_type
                can_hold = False
                update_silhouette()
            if event.key == pygame.K_s:
                should_silhouette = not should_silhouette
                if should_silhouette:
                    update_silhouette()
                else:
                    sil_shape.clear()
            if event.key == pygame.K_ESCAPE:
                sexit()
            if event.key == pygame.K_p:
                is_paused = not is_paused
            if event.key == pygame.K_UP:
                is_up_pressed = 0
            if event.key == pygame.K_DOWN:
                is_down_pressed = 0
            if event.key == pygame.K_LEFT:
                is_left_pressed = 0
            if event.key == pygame.K_RIGHT:
                is_right_pressed = 0
    if key_pressed[pygame.K_RIGHT] :
        if is_right_pressed % input_period == 0 and (is_right_pressed == 0 or is_right_pressed >= 10):
            move_with_checks(current_shape, [0, 1])
        is_right_pressed += 1
    else:
        is_right_pressed = 0
    if key_pressed[pygame.K_LEFT]:
        if is_left_pressed % input_period == 0 and (is_left_pressed == 0 or is_left_pressed >= 10):
            move_with_checks(current_shape, [0, -1])
        is_left_pressed += 1
    else:
        is_left_pressed = 0
    if key_pressed[pygame.K_DOWN]:
        if is_down_pressed % (input_period // 5) == 0:
            move_with_checks(current_shape, [1, 0])
            score += 1
        is_down_pressed += 1
    else:
        is_down_pressed = 0
    if key_pressed[pygame.K_UP]:
        if is_paused:
            continue
        if is_up_pressed % (input_period * 5) == 0 and (is_up_pressed == 0 or is_up_pressed >= 10):
            if is_vacant(current_shape.return_pseudo_rotation()):
                current_shape.rotate()
                update_silhouette()
        is_up_pressed += 1
    else:
        is_up_pressed = 0
    # Updating score + Level
    score_text = score_font.render("Score: {:06d}; Level: {:02d}".format(score, level), True, (64, 64, 64), "grey")
    screen.blit(score_text, pygame.Rect(board_upper_left[0], 0, score_text.get_rect()[2], score_text.get_rect()[3]))
    current_shape.draw()
    pygame.display.flip()
    clock.tick(60)
