from traceback import print_exc
from kivy.app import App
from screens.Main_Screen import Main_Screen
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger
from kivy.uix.settings import SettingsWithTabbedPanel

class MutantPuddingApp(App):
    def build(self):
        Logger.info('App build FIRED')
        sm = ScreenManager()
        sm.add_widget(Main_Screen(name='mainScreen'))
        self.settings_cls = SettingsWithTabbedPanel
        self.use_kivy_settings = False
        return sm

if __name__ == '__main__':
    try:
        MutantPuddingApp().run()
    except:
        print_exc()