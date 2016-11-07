from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from Brains.Hexagon import HexagonRoot
from Brains.Particle import Particle
from kivyparticle import ParticleSystem
from kivy.graphics import Color

class Main_Screen(Screen):
    def __init__(self, **kwargs):                       ##Override Screen's constructor
        Logger.info('Main_Screen init Fired')
        super(Main_Screen, self).__init__(**kwargs)     ##but also run parent class constructor (__init__)
        Logger.info('Size - ' + str(self.ids['HexGrid'].size))
        COLS=12
        ROWS=12
        self.puddingDict = {}

    def startPart(self):
        #self.ids['HexGrid'].hexagon.set_odd_r()
        #self.ids['HexGrid'].render_canvas()
        hex = self.ids['HexGrid'].returnHexLab(2)
        pa = Particle()
        pa.show(effect = ParticleSystem('./effects/royal.pex'), coor = hex.center, layout = self.ids['rootFloat'])
        self.part = pa
        Logger.info(str(hex.text) + ' = ' + str(hex.center))
        Logger.info(str(self.part.pSys.capacity))

    def changeHex(self):
        #self.ids['HexGrid'].hexagon.set_odd_q()
        #self.ids['HexGrid'].render_canvas()
        #self.part.pSys.pause()
        #self.HexGrid.changeHexColor(2, hexCulu = Color(1, 0, 1), edgeCulu = Color(0, 0, 0))
        self.ids['HexGrid'].cube_reachable(2, 4)

    def Flash_Box(self, message):
        Logger.info('Flash_Box FIRED')
        self.flashText = message
        if Configed_Bool("General", "sound") is True:
            self.glitch_sound.play()
        self.flashTrigger()

    def changePart(self):
        #self.HexGrid.hexagon.set_even_r()
        #self.HexGrid.render_canvas()
        self.part.replace(effect = ParticleSystem('./effects/royal.pex'), layout = self.ids['rootFloat'])

    def allPart(self):
        #self.HexGrid.hexagon.set_even_q()
        #self.HexGrid.render_canvas()
        for lab in self.ids['HexGrid'].returnHexLables():
            pa = Particle()
            pa.show(effect = ParticleSystem('./effects/royal.pex'), coor = lab.center, layout = self.ids['rootFloat'])
            self.puddingDict[lab.text] = pa
            Logger.info(str(lab.text) + ' = ' + str(lab.center))

    def drawLine(self):
        self.HexGrid.drawLine(2, 3)