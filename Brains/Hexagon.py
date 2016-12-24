## - credit -     https://github.com/myevan/kivy-hexagonal-grids
#                 http://www.redblobgames.com/grids/hexagons/
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Line, Mesh, Rectangle, Callback
from kivy.graphics.instructions import InstructionGroup
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty
from kivy.logger import Logger
from kivy.core.window import Window

from math import pi, cos, sin, sqrt

class Cube(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.ID = (self.x, self.y, self.z)

    def Neighbor(self, dirIndex):
        def _cube_add (op):
            return Cube(op[0](self.x), op[1](self.y), op[2](self.z))
        directions = (
           (lambda x:x+1, lambda x:x-1, lambda x:x+0),
           (lambda x:x+1, lambda x:x+0, lambda x:x-1),
           (lambda x:x+0, lambda x:x+1, lambda x:x-1),
           (lambda x:x-1, lambda x:x+1, lambda x:x+0),
           (lambda x:x-1, lambda x:x+0, lambda x:x+1),
           (lambda x:x+0, lambda x:x-1, lambda x:x+1)
        )
        return _cube_add(directions[dirIndex])

class Position(object):
    def __init__(self, *args, **kwargs):
        if args:
            if type(args[0]) is Position:
                src = args[0]
                self.x = src.x
                self.y = src.y
            else:
                self.x, self.y = args[:2]
        else:
            self.x = kwargs['x']
            self.y = kwargs['y']

    def __repr__(self):
        return 'Position(x={0:.2f}, y={1:.2f})'.format(self.x, self.y)

    def to_tuple(self):
        return (self.x, self.y)

class Vertex(object):
    def __init__(self, *args, **kwargs):
        if args:
            self.x, self.y, self.u, self.v = args[:4]
        else:
            self.x = kwargs['x']
            self.y = kwargs['y']
            self.u = kwargs['u']
            self.v = kwargs['v']

    def __repr__(self):
        return 'Vertex(x={0:.2f}, y={1:.2f}, u={2:.2f}, v={3:.2f})'.format(self.x, self.y, self.u, self.v)


class Hexagon(object):
    WEDGE_ANGLE_DEG = 60

    def __init__(self):
        self.rest = 1
        self.base_angle_deg = 30
        self.edge_len = 100
        self.dir_x = 1
        self.dir_y = 1

    def set_odd_r(self):
        self.set_rest(1)
        self.set_pointy_topped()

    def set_odd_q(self):
        self.set_rest(1)
        self.set_flat_topped()

    def set_even_r(self):
        self.set_rest(0)
        self.set_pointy_topped()

    def set_even_q(self):
        self.set_rest(0)
        self.set_flat_topped()

    def set_edge_len(self, edge_len):
        self.edge_len = edge_len

    def set_rest(self, rest):
        self.rest = rest

    def set_dir(self, x, y):
        self.dir_x = x
        self.dir_y = y

    def set_pointy_topped(self):
        self.base_angle_deg = 30

    def set_flat_topped(self):
        self.base_angle_deg = 0

    def is_pointy_topped(self):
        return self.base_angle_deg % 60 == 30

    def is_flat_topped(self):
        return self.base_angle_deg % 60 == 0

    def get_corner_angle_deg(self, i):
        return self.base_angle_deg + self.WEDGE_ANGLE_DEG * i

    def get_corner_angle_rad(self, i):
        return pi / 180 * self.get_corner_angle_deg(i)

    def create_corner_position(self, center, i):
        angle_rad = self.get_corner_angle_rad(i)
        return Position(
                center.x + self.edge_len * cos(angle_rad),
                center.y + self.edge_len * sin(angle_rad))

    def create_corner_vertex(self, center, i):
        angle_rad = self.get_corner_angle_rad(i)
        cos_angle_rad = cos(angle_rad)
        sin_angle_rad = sin(angle_rad)
        return Vertex(
                center.x + self.edge_len * cos_angle_rad,
                center.y + self.edge_len * sin_angle_rad,
                cos_angle_rad,
                sin_angle_rad)

    def create_corner_angles(self):
        return [self.get_corner_angle_deg(i) for i in xrange(6)]

    def create_corner_positions(self, center):
        return [self.create_corner_position(center, i) for i in xrange(6)]

    def create_corner_vertices(self, center):
        return [self.create_corner_vertex(center, i) for i in xrange(6)]

    def get_long_len(self):
        return 2 * self.edge_len

    def get_short_len(self):
        return sqrt(3.0) / 2.0 * self.get_long_len()

    def get_long_step(self):
        return self.get_long_len() / 4.0 * 3.0

    def get_short_step(self):
        return self.get_short_len()

    def get_size(self):
        if self.is_pointy_topped():
            return (self.get_short_len(), self.get_long_len())
        else:
            return (self.get_long_len(), self.get_short_len())

    def get_step(self):
        if self.is_pointy_topped():
            return (self.get_short_step(), self.get_long_step())
        else:
            return (self.get_long_step(), self.get_short_step())

    def get_div(self):
        if self.is_pointy_topped():
            return (2, 4)
        else:
            return (4, 2)

    def gen_grid_positions(self, origin_position, row_count, col_count):
        size_x, size_y = self.get_size()
        step_x, step_y = self.get_step()

        step_x = step_x * self.dir_x
        step_y = step_y * self.dir_y

        base_position = Position(origin_position)
        base_position.x += size_x * 0.5 * self.dir_x
        base_position.y += size_y * 0.5 * self.dir_y

        line_position = Position(base_position)

        if self.base_angle_deg == 30:
            for row in xrange(0, row_count):
                each_position = Position(line_position)
                if row % 2 == self.rest:
                    each_position.x += step_x * 0.5

                for col in xrange(0, col_count):
                    yield (col, row, each_position)
                    each_position.x += step_x

                line_position.y += step_y
        else:
            for col in xrange(0, col_count):
                each_position = Position(line_position)
                if col % 2 == self.rest:
                    each_position.y += step_y * 0.5

                for row in xrange(0, row_count):
                    yield (col, row, each_position)
                    each_position.y += step_y

                line_position.x += step_x



class KivyHexagon(Hexagon):
    def gen_position_sequences(self, positions):
        for position in positions:
            yield position.x
            yield position.y

    def gen_closed_position_sequences(self, positions):
        for position in positions:
            yield position.x
            yield position.y

        yield positions[0].x
        yield positions[0].y

    def gen_vertex_sequences(self, vertexs):
        for vertex in vertexs:
            yield vertex.x
            yield vertex.y
            yield vertex.u
            yield vertex.v

    def convert_line_points(self, positions):
        return [e for e in self.gen_position_sequences(positions)]

    def convert_closed_line_points(self, positions):
        return [e for e in self.gen_closed_position_sequences(positions)]

    def convert_mesh_vertices(self, vertices):
        return [e for e in self.gen_vertex_sequences(vertices)]

    def make_mesh(self, center_position):
        corner_vertices = self.create_corner_vertices(center_position)
        return Mesh(vertices=self.convert_mesh_vertices(corner_vertices), indices=xrange(len(corner_vertices)), mode='triangle_fan')

    def make_outline(self, center_position):
        corner_positions = self.create_corner_positions(center_position)
        return Line(points=self.convert_closed_line_points(corner_positions), width=1)

    def make_circle(self, center_position, radius):
        return Ellipse(pos=(center_position.x - radius, center_position.y - radius), size=(radius * 2, radius * 2))
