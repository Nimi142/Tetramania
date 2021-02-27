import enum
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
import numpy as np


class ShapeType(enum.Enum):
    I = 0
    S = 1
    J = 2
    T = 3
    L = 4
    O = 5
    Z = 6


class Shape:
    board_upper_left = None
    tile_size = None
    stroke_size = None
    background_color = None
    base_pos = np.array([5, 4])
    
    def __init__(self, display, shape: ShapeType, is_silhouette=False):
        self.type = shape
        self.display = display
        if shape == ShapeType.I:
            self.block_pos = np.array([[-0.5, -1.5], [-0.5, -0.5], [-0.5, 0.5], [-0.5, 1.5]])
            self.color = "cyan"
            self.pos = Shape.base_pos - np.array([0.5, 0.5])
        elif shape == ShapeType.S:
            self.block_pos = np.array([[-1, 1], [-1, 0], [0, 0], [0, -1]])
            self.color = "green"
            self.pos = Shape.base_pos - np.array([0, 0])
        elif shape == ShapeType.J:
            self.block_pos = np.array([[-1, -1], [0, -1], [0, 0], [0, 1]])
            self.color = "blue"
            self.pos = Shape.base_pos - np.array([0, 0])
        elif shape == ShapeType.L:
            self.block_pos = np.array([[0, -1], [0, 0], [0, 1], [-1, 1]])
            self.color = "orange"
            self.pos = Shape.base_pos - np.array([0, 0])
        elif shape == ShapeType.Z:
            self.block_pos = np.array([[-1, -1], [-1, 0], [0, 0], [0, 1]])
            self.color = "red"
            self.pos = Shape.base_pos - np.array([0, 0])
        elif shape == ShapeType.O:
            self.block_pos = np.array([[-0.5, -0.5], [-0.5, 0.5], [0.5, -0.5], [0.5, 0.5]])
            self.color = "yellow"
            self.pos = Shape.base_pos - np.array([0.5, 0.5])
        elif shape == ShapeType.T:
            self.block_pos = np.array([[0, -1], [0, 0], [0, 1], [-1, 0]])
            self.color = "purple"
            self.pos = Shape.base_pos - np.array([0, 0])
        else:
            self.block_pos = np.array([[0, -1], [0, 0], [0, 1], [-1, 0]])
            self.color = "grey"
            self.pos = Shape.base_pos - np.array([0, 0])
        self.last_drawn_pos = np.copy(self.pos)
        self.is_silhouette = is_silhouette
        if is_silhouette:
            self.stroke_color = "grey"
            self.color = "black"


    def board_pos_to_canvas_pos(self, pos, block_pos) -> np.ndarray:
        return (pos + block_pos) * (Shape.tile_size + 1.5 * Shape.stroke_size) + Shape.board_upper_left[::-1] - np.array([0.5, 0.5])

    def clear(self):
        for block_position in self.block_pos:
            pos = self.board_pos_to_canvas_pos(self.last_drawn_pos, block_position)
            pygame.draw.rect(self.display, Shape.background_color,
                             pygame.Rect(pos[1], pos[0], Shape.tile_size + 2 * Shape.stroke_size, Shape.tile_size + 2 * Shape.stroke_size))

    def draw(self):
        self.clear()
        for block_pos in self.block_pos:
            pos = self.board_pos_to_canvas_pos(self.pos, block_pos)
            pygame.draw.rect(self.display, self.stroke_color,
                             pygame.Rect(pos[1], pos[0], Shape.tile_size + 2 * Shape.stroke_size, Shape.tile_size + 2 * Shape.stroke_size))
            pygame.draw.rect(self.display, self.color,
                             pygame.Rect(pos[1] + Shape.stroke_size, pos[0] + Shape.stroke_size, Shape.tile_size, Shape.tile_size))
            # Testing
        self.last_drawn_pos = np.copy(self.pos)

    def move_direction(self, direction):
        self.pos += direction

    def move_to(self, position):
        self.pos = np.copy(position)

    def rotate(self):
        self.clear()
        self.block_pos = self.pseudo_rotate()
        self.draw()

    def pseudo_rotate(self):
        if self.type == ShapeType.O:
            return self.block_pos
        new_pos = np.copy(self.block_pos)
        for loc_ind in range(len(new_pos)):
            new_pos[loc_ind] = np.array([new_pos[loc_ind, 1], -new_pos[loc_ind, 0]])
        return new_pos
        # return self.block_pos.dot(np.array([[0, 1], [-1, 0]])).astype(int)

    def draw_hold(self, upper_left, box_size):
        for block_pos in self.block_pos:
            pos = box_size / 2.5 + block_pos * (Shape.tile_size + 1.5 * Shape.stroke_size) + upper_left[::-1]
            pygame.draw.rect(self.display, self.stroke_color,
                             pygame.Rect(pos[1], pos[0], Shape.tile_size + 2 * Shape.stroke_size,
                                         Shape.tile_size + 2 * Shape.stroke_size))
            pygame.draw.rect(self.display, self.color,
                             pygame.Rect(pos[1] + Shape.stroke_size, pos[0] + Shape.stroke_size, Shape.tile_size,
                                         Shape.tile_size))

    def draw_preview(self, upper_left, position, size):
        for block_pos in self.block_pos:
            pos = upper_left[::-1] + np.array([size[1] * position / 3 + size[1] / 6, size[0] / 2]) + block_pos * (Shape.tile_size + 1.5 * Shape.stroke_size)
            pygame.draw.rect(self.display, self.stroke_color,
                             pygame.Rect(pos[1], pos[0], Shape.tile_size + 2 * Shape.stroke_size, Shape.tile_size + 2 * Shape.stroke_size))
            pygame.draw.rect(self.display, self.color,
                             pygame.Rect(pos[1] + Shape.stroke_size, pos[0] + Shape.stroke_size, Shape.tile_size, Shape.tile_size))
            # Testing
        self.last_drawn_pos = np.copy(self.pos)

    def return_pseudo_rotation(self):
        return (self.pseudo_rotate() + self.pos).astype(int)

    def get_block_location(self, offset=(0, 0)):
        offset = np.array(offset)
        return (self.pos + offset + self.block_pos).astype(int)
