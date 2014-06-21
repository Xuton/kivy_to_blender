import socket

from kivy.app import App
from kivy.properties import OptionProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox


class CanvasWidget(BoxLayout):
    """
    This is black box that captures all the input and sends it to blender.
    """
    def __init__(self, **kwargs):
        super(CanvasWidget, self).__init__(**kwargs)
        global app
        self.app = app
        self._touch_count = 0
        self.mode = None

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            touch.grab(self)
            self._touch_count += 1

            if self._touch_count == 1:
                self.mode = 'ROTATE'
            elif self._touch_count == 2:
                self.mode = 'MOVE'

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            print(touch.dsx, touch.dsy)
            print(self.app.axis)

            if touch.dsx != 0:
                action = self.mode + '_' + self.app.axis[0]
                unit = touch.dsx * app.slider.value
                print('Y, action, unit = {}, {}'.format(action, unit))
                self.app.send(action, unit)

            if touch.dsy != 0:
                action = self.mode + '_' + self.app.axis[1]
                unit = touch.dsy * app.slider.value
                print('Y, action, unit = {}, {}'.format(action, unit))
                self.app.send(action, unit)

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        self._touch_count -= 1


class Tester(App):
    state = OptionProperty('OBJECT',
                           options=['OBJECT', 'SCREEN'])
    axis = OptionProperty('XY',
                          options=['XY', 'XZ', 'YZ'])

    def __init__(self, **kwargs):
        super(Tester, self).__init__(**kwargs)
        # This is the magic bit that connects kivy to the
        # blender socket (Blender should already have binded to the port)
        # and sends the info. Port 6682 = ord(B) + ord(R)
        host = ''
        port = 6682

        self.address = (host, port)
        self.s = socket.socket()  # socket.AF_INET, socket.SOCK_STREAM)

        self.slider = None

    def build(self):
        # Should have done it in kv. Oops
        box = BoxLayout(orientation='vertical')
        self.slider = Slider(size_hint=(1, .1))
        self.slider.value = 1
        self.slider.min = 1
        self.slider.max = 100

        self.btn1 = ToggleButton(group='selection',
                                 text='Move object',
                                 state='down',
                                 on_touch_down=self.update_state)

        self.btn2 = ToggleButton(group='selection',
                                 text='Move screen',
                                 on_touch_down=self.update_state)

        b = BoxLayout(size_hint_y=.2,
                      padding=10,
                      spacing=10)
        self.opt1 = CheckBox(text='xy', group='axis', active=True,
                             on_touch_down=self.update_axis)
        self.opt2 = CheckBox(text='xz', group='axis', active=False,
                             on_touch_down=self.update_axis)
        self.opt3 = CheckBox(text='yz', group='axis', active=False,
                             on_touch_down=self.update_axis)

        b.add_widget(self.btn1)
        b.add_widget(self.btn2)
        b1 = BoxLayout(size_hint_x=.2,
                       padding=10,
                       spacing=10)
        b1.add_widget(self.opt1)
        b1.add_widget(self.opt2)
        b1.add_widget(self.opt3)
        b.add_widget(b1)

        box.add_widget(CanvasWidget())
        box.add_widget(b)
        box.add_widget(self.slider)
        return box

    def update_state(self, *args):
        """
        The state tells it to update the view or object.
        So Object would make the Cube move.
        Screen would make the screen pan and rotate (Rotate still broken)
        """
        if args[0].state == 'down':
            self.state = str(args[0].text.replace('Move ', '')).upper()
        print(self.state)

    def update_axis(self, *args):
        """
        Only used in the Object mode. Makes the object move / rotate
        on the XY, XZ or YZ axis.
        """
        if self.opt1.active:
            self.axis = 'XY'
        if self.opt2.active:
            self.axis = 'XZ'
        if self.opt3.active:
            self.axis = 'YZ'
        print(self.axis)

    def send(self, action, unit):
        """
        This actually sends the info to Blender
        Called from within the Canvas Widget
        """
        s = socket.socket()
        s.connect(self.address)
        s.send('{}: {}\n'.format(self.state+'_'+action, unit))
        s.close()


if __name__ == '__main__':
    app = Tester()
    app.run()
