## - credit -     https://github.com/myevan/kivy-hexagonal-grids
#                 http://www.redblobgames.com/grids/hexagons/

from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Line, Mesh, Rectangle
from kivy.graphics.instructions import InstructionGroup
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.logger import Logger

from math import pi, cos, sin, sqrt
from docutils.nodes import row
from copy import copy

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

    def make_mesh(self, center_position, group):
        corner_vertices = self.create_corner_vertices(center_position)
        if group is None:
            return Mesh(vertices=self.convert_mesh_vertices(corner_vertices), indices=xrange(len(corner_vertices)), mode='triangle_fan')
        else:
            group.add(Mesh(vertices=self.convert_mesh_vertices(corner_vertices), indices=xrange(len(corner_vertices)), mode='triangle_fan'))

    def make_outline(self, center_position, group, width=1):
        corner_positions = self.create_corner_positions(center_position)
        if group is None:
            return Line(points=self.convert_closed_line_points(corner_positions), width=width)
        else:
            group.add(Line(points=self.convert_closed_line_points(corner_positions), width=width))

    def make_circle(self, center_position, radius):
        return Ellipse(pos=(center_position.x - radius, center_position.y - radius), size=(radius * 2, radius * 2))

class HexagonRoot(FloatLayout):

    def __init__(self, **kwargs):
        super(HexagonRoot, self).__init__(**kwargs)
        self.bind(pos=self.render_canvas, size=self.render_canvas)
        self.size_hint = (1, 1)
        self.EDGE_LEN = kwargs.get('edgeLength', 1)
        self.EDGE_WIDTH = kwargs.get('edgeWidth', 1)
        self.ROWS =  kwargs.get('rows', 10)
        self.COLS = kwargs.get('cols', self.ROWS)
        self.CENTER_RADIUS = kwargs.get('centerRadius', 4)
        self.CORNER_RADIUS = kwargs.get('cornerRadius', 4)
        self.CENTER_COLOR = kwargs.get('centerColor', (0.5, 0.1, 0.1))
        self.CORNER_COLOR = kwargs.get('cornerColor', (0.5, 0.1, 0.1))
        self.EDGE_COLOR = kwargs.get('edgeColor', (0.3, 0.3, 0.3))
        self.AXIS_COLOR = kwargs.get('axisColor', (0.3, 0.3, 0.3))
        self.MESH_COLOR = kwargs.get('meshColor', (0.5, 0.5, 0.5))
        self.coord_labels = [Label(text="", pos_hint={}, size_hint=(None, None)) for i in xrange(self.ROWS * self.COLS)]
        self.gridInfo = {key: {'id': None, 'instGroup': None, 'prevInstGroup': None} for key in xrange(self.ROWS * self.COLS)}
        self.gridIndex = {}
        self.hexagon = KivyHexagon()
        self.hexagon.set_edge_len(self.EDGE_LEN)
        self.hexagon.set_dir(+1, -1)
        self.X_AXIS_LEN = self.hexagon.get_short_len() * self.COLS
        self.Y_AXIS_LEN = self.hexagon.get_long_step() * self.ROWS
        self.centerish = (10,10)

    def returnHexLab(self, index):
        return self.coord_labels[index]

    def returnHexLables(self):
        return self.coord_labels

    def on_size(self, screen, size):
        height = size[1] / self.ROWS
        width = sqrt(3)/2 * height
        self.EDGE_LEN = (height / 2) * 1.18
        Logger.info('size = ' + str(size) + ', height = ' + str(height) + ', width = ' + str(width) + 'COLS = ' + str(self.COLS) + ', ROWS = ' + str(self.ROWS))
        self.hexagon.set_edge_len(self.EDGE_LEN)
        self.X_AXIS_LEN = self.hexagon.get_short_len() * self.COLS
        self.Y_AXIS_LEN = self.hexagon.get_long_step() * self.ROWS
        self.centerish = (size[0] * 0.6, size[1] * 0.65)

    def changeHex(self, **kwargs):
        index = kwargs.get('index')
        lab = self.coord_labels[index]
        newGroup = InstructionGroup()
        colour = kwargs.get('meshColour', (0, 1, 1, 0.2))
        newGroup.add(Color(colour))
        self.hexagon.make_mesh(lab.each_position, newGroup)
        colour = kwargs.get('outlineColour', (0, 0, 1, 0.2))
        newGroup.add(Color(colour))
        self.hexagon.make_outline(lab.each_position, newGroup)
        self.gridInfo[index]['prevInstGroup'] = self.gridInfo[index]['instGroup']
        self.canvas.remove(self.gridInfo[index]['instGroup'])
        self.gridInfo[index]['instGroup'] = newGroup
        with self.canvas.before:
            self.canvas.add(self.gridInfo[index]['instGroup'])

    def restorHex(self, **kwargs):
        index = kwargs.get('index')
        self.canvas.remove(self.gridInfo[index]['instGroup'])
        self.gridInfo[index]['instGroup'] = self.gridInfo[index]['prevInstGroup']
        with self.canvas.before:
            self.canvas.add(self.gridInfo[index]['instGroup'])


    def render_canvas(self, *args):
        origin_position = Position(*self.centerish)
        origin_position.x -= self.X_AXIS_LEN / 2
        origin_position.y += self.Y_AXIS_LEN / 2
        #x_axis_position = Position(origin_position.x + self.X_AXIS_LEN, origin_position.y)
        #y_axis_position = Position(origin_position.x, origin_position.y - self.Y_AXIS_LEN)
        self.canvas.before.clear()

        with self.canvas.before:
            #Color(*self.AXIS_COLOR)
            #Line(points=self.hexagon.convert_line_points([x_axis_position, origin_position, y_axis_position]), width=self.EDGE_WIDTH)
            #Rectangle(pos=(100, 100), size=(100, 100))
            for each_label in self.coord_labels:
                self.remove_widget(each_label)

            for col, row, each_position in self.hexagon.gen_grid_positions(origin_position, row_count=self.ROWS, col_count=self.COLS):
                index = row * self.COLS + col
                self.gridInfo[index]['id'] = "{0}x{1}".format(col, row)
                self.gridIndex["{0}x{1}".format(col, row)] = index
                self.gridInfo[index]['instGroup'] = InstructionGroup()
                self.gridInfo[index]['instGroup'].add(Color(*self.MESH_COLOR))
                self.hexagon.make_mesh(each_position, self.gridInfo[index]['instGroup'])
                self.gridInfo[index]['instGroup'].add(Color(*self.EDGE_COLOR))
                self.hexagon.make_outline(each_position, self.gridInfo[index]['instGroup'])
                each_label = self.coord_labels[index]
                each_label.text = "{0}x{1}".format(col, row)    #to be removed from prod
                each_label.center = each_position.to_tuple()
                each_label.col = copy(col)
                each_label.row = copy(row)
                each_label.each_position = copy(each_position)
                self.add_widget(each_label)
