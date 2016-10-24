from kivyparticle import ParticleSystem
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.logger import Logger
from copy import copy

class Particle(Widget):

    def __init__(self, **kwargs):
        super(Particle, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        self.pSys.emitter_x = float(touch.x)
        self.pSys.emitter_y = float(touch.y)

    def on_touch_move(self, touch):
        self.pSys.emitter_x = float(touch.x)
        self.pSys.emitter_y = float(touch.y)

    def show(self, **kwargs):
        self.pSys = kwargs.get('effect')
        coor = kwargs.get('coor')
        self.pSys.emitter_x = float(kwargs.get('x',coor[0]))
        self.pSys.emitter_y = float(kwargs.get('y',coor[1]))
        kwargs.get('layout').add_widget(self.pSys)
        self.pSys.start()

    def replace(self, **kwargs):
        lo = kwargs.get('layout')
        x = copy(self.pSys.emitter_x)
        y = copy(self.pSys.emitter_y)
        self.pSys.emitter_x = -1000
        self.pSys.emitter_y = -1000
        def doNext(dt):
            self.show(coor = (x,y), layout = lo, effect = kwargs.get('effect'))
        Clock.schedule_once(doNext, kwargs.get('transitionTime', 0.5))

    def unshow(self, **kwargs):
        lo = kwargs.get('layout')
        self.pSys.emitter_x = -1000
        self.pSys.emitter_y = -1000
        def done(dt):
            self.pSys.stop()
            lo.remove_widget(self.pSys)
        Clock.schedule_once(done, 3)

    def __exit__(self, typ, val, tb):
        pass

