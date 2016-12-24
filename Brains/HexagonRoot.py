from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Line, Mesh, Rectangle, Callback
from kivy.graphics.instructions import InstructionGroup
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty
from kivy.logger import Logger
from kivy.core.window import Window

from math import pi, cos, sin, sqrt
#from docutils.nodes import row
from copy import copy
#from cassandra.cqlengine.columns import Integer
#from Brains.Astar import heuristic, a_star_search, HexGrid
from Brains.Hexagon import *
from Brains.Astar import *

class HexagonRoot(FloatLayout):

    flashText = StringProperty('')  # #Text for the flash boxes

    def __init__(self, **kwargs):
        super(HexagonRoot, self).__init__(**kwargs)
        #self.bind(pos=self.render_canvas, size=self.render_canvas)
        self.size_hint = (1, 1)
        self.EDGE_LEN = kwargs.get('edgeLength', 1)
        self.EDGE_WIDTH = kwargs.get('edgeWidth', 1)
        self.ROWS =  kwargs.get('rows', 10)
        self.COLS = kwargs.get('cols', self.ROWS)
        self.CENTER_RADIUS = kwargs.get('centerRadius', 4)
        self.CORNER_RADIUS = kwargs.get('cornerRadius', 4)
        #self.AXIS_COLOR = kwargs.get('axisColor', (0.3, 0.3, 0.3))
        self.ROWCOUNT = self.ROWS * self.COLS
        tmpChar = Character(moveRange = 5, viewRange = 3, canFly = True)
        self.coord_labels = [HexLab(character=tmpChar, text="s", pos_hint={}, size_hint=(None, None)) for i in xrange(self.ROWCOUNT)]
        self.cubeIndex = {}
        self.hexagon = KivyHexagon()
        self.hexagon.set_edge_len(self.EDGE_LEN)
        self.hexagon.set_dir(+1, -1)
        self.X_AXIS_LEN = self.hexagon.get_short_len() * self.COLS
        self.Y_AXIS_LEN = self.hexagon.get_long_step() * self.ROWS
        self.centerish = (10,10)
        self.redrawTrigger = Clock.create_trigger(self.render_canvas)
        self.dragPath = kwargs.get('dragPath', True)
        self.dragPlotA = None
        self.dragPlotB = None
        self.dragPlotHitory = []
        self.flashTrigger = Clock.create_trigger(self._Flash_Box)

    def Widget_ToTop(self, widget):
        self.remove_widget(widget)
        self.add_widget(widget)
        return True

    def _Flash_Box(self, dt):
        Logger.info('_Flash_Box FIRED')
        fL = Label(text = 'AHH', font_size = '18sp', size_hint = (None,None))
        fL.pos = 100, 100
        fL.color = (1,1,1,1)
        self.Widget_ToTop(fL)

    def Flash_Box(self, message):
        Logger.info('Flash_Box FIRED')
        self.flashText = message
        self.flashTrigger()

    def on_touch_down(self, touch):
        for index in xrange(self.ROWCOUNT):
            if self.coord_labels[index].collide_point(*touch.pos):
                if self.dragPlotA is None and touch.is_double_tap:
                    Logger.info('DoubleTap at ' + self.coord_labels[index].id)
                    lab = self.changeHexColor(index, hexCulu = Color(1, 0, 0.8), edgeCulu = Color(0, 0, 0))
                    lab.makeWall()
                    Logger.info('coll -- ' + str(lab.collide_point_forhex))
                    self.Flash_Box('WALL')
                elif self.dragPath is True:
                    labA = self.coord_labels[index]
                    touch.grab(labA)
                    Logger.info('Grab at ' + labA.id)
                    labA.allReachableCubes = self.cube_reachable(labA.cube, labA.character.moveRange)
                    labA.hexGrid = HexGrid(self.coord_labels, self.cubeIndex, labA.allReachableCubes)
                    self.dragPlotA = index
                return False

    def on_touch_move(self, touch):
        for index in xrange(self.ROWCOUNT):
            lab = self.coord_labels[index]
            if self.dragPlotA is not None and self.dragPlotA != index and self.dragPlotB != index and lab.collide_point(*touch.pos):
                Logger.info('Move at ' + lab.id)
                self.dragPlotB = index
                try:
                    self.canvas.remove(self.linePlot)
                except:
                    Logger.error('AHHHHH ')
                    pass
                self.dragPlotHitory = self.drawLine(self.dragPlotA, self.dragPlotB)
                return False

    def on_touch_up(self, touch):
        if self.dragPlotA is not None:
            try:
                self.canvas.remove(self.linePlot)
            except:
                pass
        for index in xrange(self.ROWCOUNT):
            if self.dragPlotA is not None and self.coord_labels[index].collide_point_forhex(*touch.pos):
                touch.ungrab(self.coord_labels[index])
                Logger.info('ungrab at ' + self.coord_labels[index].id + '    - ' + str(self.coord_labels[index].collide_point_forhex))
                self.dragPlotA = None
                self.dragPlotB = None
                return False

    def returnHexLab(self, index):
        return self.coord_labels[index]

    def returnHexLables(self):
        return self.coord_labels

    def on_size(self, screen, size):
        height = size[1] / self.ROWS
        width = sqrt(3)/2 * height
        self.EDGE_LEN = (height / 2) * 1.18
        Logger.info('on_size fired -- size = ' + str(size) + ', height = ' + str(height) + ', width = ' + str(width) + 'COLS = ' + str(self.COLS) + ', ROWS = ' + str(self.ROWS))
        self.hexagon.set_edge_len(self.EDGE_LEN)
        self.X_AXIS_LEN = self.hexagon.get_short_len() * self.COLS
        self.Y_AXIS_LEN = self.hexagon.get_long_step() * self.ROWS
        self.centerish = (size[0] * 0.6, size[1] * 0.65)
        self.redrawTrigger()

    def cube_linePlot(self, a, b):

        def _cube_distance(a, b):
            return (abs(a.x - b.x) + abs(a.y - b.y) + abs(a.z - b.z)) / 2

        def _cube_lerp(a, b, t):
            return Cube(_lerp(a.x, b.x, t), _lerp(a.y, b.y, t), _lerp(a.z, b.z, t))

        def _lerp(a, b, t):
            return a + (b - a) * t

        def _cube_round(h):
            rx = round(h.x)
            ry = round(h.y)
            rz = round(h.z)
            x_diff = abs(rx - h.x)
            y_diff = abs(ry - h.y)
            z_diff = abs(rz - h.z)
            if x_diff > y_diff and x_diff > z_diff:
                rx = -ry-rz
            elif y_diff > z_diff:
                ry = -rx-rz
            else:
                rz = -rx-ry
            return Cube(rx, ry, rz)

        N = _cube_distance(a, b)
        results = []
        for i in range(0,N):
            results.append(_cube_round(_cube_lerp(a, b, 1.0 / N * i)))
        return results

#     def cubeID (self,cube):
#         return (cube.x, cube.y, cube.z)
#
#     def cube_neighbor(self, cube, dirIndex):
#         def _cube_add (cube, op):
#             return Cube(op[0](cube.x), op[1](cube.y), op[2](cube.z))
#         directions = (
#            (lambda x:x+1, lambda x:x-1, lambda x:x+0),
#            (lambda x:x+1, lambda x:x+0, lambda x:x-1),
#            (lambda x:x+0, lambda x:x+1, lambda x:x-1),
#            (lambda x:x-1, lambda x:x+1, lambda x:x+0),
#            (lambda x:x-1, lambda x:x+0, lambda x:x+1),
#            (lambda x:x+0, lambda x:x-1, lambda x:x+1)
#         )
#         return _cube_add(cube, directions[dirIndex])

    def cube_reachable(self, start, steps):
        visited = set()
        visited.add(start)
        fringes = []
        fringes.append([start])
        for k in range(1, steps):
            fringes.append([])
            for cube in fringes[k-1]:
                for dirIndex in range(0, 6):
                    Logger.info('dir index = ' + str(dirIndex) + ', coor = ' + str(self.coord_labels[ self.cubeIndex[cube.ID] ].id))
                    neighbor = cube.Neighbor(dirIndex)
                    if neighbor not in visited and neighbor.ID in self.cubeIndex and self.coord_labels[ self.cubeIndex[neighbor.ID] ].wall is False:
                        visited.add(neighbor)
                        fringes[k].append(neighbor)
        return visited

    def changeHexColor(self, index, **kwargs):
        lab = self.coord_labels[index]
        lab.prevHexCol = copy(lab.hexCulu)
        lab.hexCulu = kwargs.get('hexCulu', lab.hexCulu)
        lab.group.add(lab.hexCulu)
        lab.group.add(self.hexagon.make_mesh(lab.each_position))
        lab.group.add(lab.edgeCulu)
        return lab

    #should return whether indexB is visible from character at indexA
    def isVisible(self, indexA, indexB):
        labA = self.coord_labels[indexA]
        labB = self.coord_labels[indexB]
        result = self.cube_linePlot(labA.cube, labB.cube)
        result.append(labB.cube)
        for cube in result[:labA.character.viewRange]:
            if cube not in labA.allReachableCubes:
                return False
            if cube == labB.cube:
                return True
        return False

    def drawLine(self, indexA, indexB):
        labA = self.coord_labels[indexA]
        labB = self.coord_labels[indexB]
        ast = Astar()
        Logger.info('aStar = ' + str(ast.a_star_search(labA.hexGrid, labA.cube, labB.cube)))
        if labA.character.canFly is True:
            result = self.cube_linePlot(labA.cube, labB.cube)
            result.append(labB.cube)
            coors = []
            for cube in result[:labA.character.moveRange]:
                lab = self.coord_labels[ self.cubeIndex[(cube.x,cube.y,cube.z)] ]
                Logger.info('Plotting line at ' + str(lab.id) + ', Cube coords: x=' + str(cube.x) + ' y=' + str(cube.y) + ' z=' + str(cube.z))
                coors.append(lab.center[0])
                coors.append(lab.center[1])
            self.linePlot = InstructionGroup()
            self.linePlot.add(Color(1,1,1))
            self.linePlot.add(Line(points=coors, width=10))
        else:
            #begin attempt at aStar algorithm
            Logger.info('aStar = ' + str(Astar.a_star_search(labA.hexGrid, labA.cube, labB.cube)))
            newCoors = []
            for cube in labA.allReachableCubes:
                lab = self.coord_labels[ self.cubeIndex[(cube.x,cube.y,cube.z)] ]
                Logger.info('Plotting NEW line at ' + str(lab.id) + ', Cube coords: x=' + str(cube.x) + ' y=' + str(cube.y) + ' z=' + str(cube.z))
                newCoors.append(lab.center[0])
                newCoors.append(lab.center[1])
            self.linePlot.add(Color(1,1,0))
            self.linePlot.add(Line(points=newCoors, width=1))
            #end

        self.canvas.add(self.linePlot)
        return result[:labA.character.moveRange]

    def render_canvas(self, *args):
        origin_position = Position(*self.centerish)
        origin_position.x -= self.X_AXIS_LEN / 2
        origin_position.y += self.Y_AXIS_LEN / 2

        for lab in self.coord_labels:
            self.remove_widget(lab)

        width = sqrt(3)/2 * (self.EDGE_LEN * 2)
        for col, row, each_position in self.hexagon.gen_grid_positions(origin_position, row_count=self.ROWS, col_count=self.COLS):
            index = row * self.COLS + col
            id = "{0}x{1}".format(col, row)
            Logger.info(str(index) + ' each_position = ' + str(each_position) + ', ID = ' + id)
            lab = self.coord_labels[index]
            lab.id = id                                 #set ID
            cubex = col - (row - (row&1)) / 2           #get the
            cubez = row                                 #cube
            cubey = -cubex - cubez                      #coordinates
            self.cubeIndex[(cubex, cubey, cubez)] = index   #and use then to create an index
            lab.width = width                           #set the calculated width
            lab.height = self.EDGE_LEN                  #and height which = EDGE_LEN - note, size is a square within each hex not whole hex
            lab.color = (1,0,1,1)                       #
            lab.font_size = '10sp'
            lab.valign = 'middle'
            lab.markup = True
            lab.labText = id
            lab.cube = Cube(cubex, cubey, cubez)        #this can be later referenxed against the cubeIndex
            lab.center = each_position.to_tuple()
            lab.col = NumericProperty(col)
            lab.row = NumericProperty(row)
            lab.each_position = copy(each_position)
            lab.group = InstructionGroup()                                  #create Instruction group
            lab.group.add(lab.edgeCulu)                                     #so we can draw
            lab.group.add(self.hexagon.make_outline(lab.each_position))     #each hex
            lab.group.add(lab.hexCulu)
            lab.group.add(self.hexagon.make_mesh(lab.each_position))
            lab.group.add(Color(1, 0, 0, 1))
            lab.group.add(Rectangle(pos=lab.pos, size=lab.size))            #and the lab square canvas
            lab.collide_point_forhex = lab.collide_point                    #and set this so we know when a hex has been selected / touched

        for lab in self.coord_labels:
            self.remove_widget(lab)
            lab.canvas.clear()
            lab.canvas.add(lab.group)
            self.add_widget(lab)



class Character(Label):
    canFly = BooleanProperty(None)
    viewRange = NumericProperty(None)
    moveRange = NumericProperty(None)

    def __init__(self, **kwargs):
        super(Character, self).__init__(**kwargs)
        self.moveRange = kwargs.get('moveRange')
        self.viewRange = kwargs.get('viewRange')
        self.canFly = kwargs.get('canFly')

class HexLab(Label):
    hexCulu = Color(None)
    edgeCulu = Color(None)
    wall = BooleanProperty(None)
    character = ObjectProperty(None)
    weight = NumericProperty(None)

    def __init__(self, **kwargs):
        super(HexLab, self).__init__(**kwargs)
        self.hexCulu = kwargs.get('edgeCulu', Color(0.5, 0.5, 0.5))
        self.edgeCulu = kwargs.get('edgeCulu', Color(1, 1, 0.5))
        self.wall = kwargs.get('wall', False)
        self.weight = kwargs.get('weight', 1)
        self.character = kwargs.get('character', None)

    def makeWall(self):
        self.wall = True
        self.oldWeight = copy(self.weight)
        self.weight = 100

    def bustWall(self):
        self.wall = False
        self.weight = copy(self.oldWeight)