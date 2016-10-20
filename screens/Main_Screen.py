from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from Brains.Hexagon import HexagonRoot

class Main_Screen(Screen):
    def __init__(self, **kwargs):                       ##Override Screen's constructor
        Logger.info('Main_Screen init Fired')
        super(Main_Screen, self).__init__(**kwargs)     ##but also run parent class constructor (__init__)
        Logger.info('Size - ' + str(self.ids['rootFloat'].size))
        COLS=12
        ROWS=12
        rootFloat = self.ids['rootFloat']
        self.HexGrid = HexagonRoot()
        rootFloat.add_widget(self.HexGrid)

    def make_odd_r(self):
        self.HexGrid.hexagon.set_odd_r()
        self.HexGrid.render_canvas()

    def make_odd_q(self):
        self.HexGrid.hexagon.set_odd_q()
        self.HexGrid.render_canvas()

    def make_even_r(self):
        self.HexGrid.hexagon.set_even_r()
        self.HexGrid.render_canvas()

    def make_even_q(self):
        self.HexGrid.hexagon.set_even_q()
        self.HexGrid.render_canvas()

    def make_pointy_topped(self):
        KivyHexagon.set_hexagon_pointy_topped()
        self.render_canvas()

    def make_flat_topped(self):
        KivyHexagon.set_hexagon_flat_topped()
        self.render_canvas()