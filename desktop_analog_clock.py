import gi.repository
gi.require_version('Budgie', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Budgie, GObject, Gtk, GdkPixbuf, GLib, Gio, Gdk
import os
import subprocess

"""
    Desktop Clock Applet for the Budgie Panel

    Copyright © 2020 Samuel Lane
    http://github.com/samlane-ma/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
CLOCK_CMD = os.path.join(os.path.dirname(os.path.abspath(__file__)),"desktop-clock.py")
app_settings = Gio.Settings.new("com.github.samlane-ma.desktop-analog-clock")

class DesktopAnalogClock(GObject.GObject, Budgie.Plugin):
    """ This is simply an entry point into your Budgie Applet implementation.
        Note you must always override Object, and implement Plugin.
    """
    # Good manners, make sure we have unique name in GObject type system
    __gtype_name__ = "DesktopAnalogClock"

    def __init__(self):
        """ Initialisation is important.
        """
        GObject.Object.__init__(self)

    def do_get_panel_widget(self, uuid):

        """ This is where the real fun happens. Return a new Budgie.Applet
            instance with the given UUID. The UUID is determined by the
            BudgiePanelManager, and is used for lifetime tracking.
        """
        return DesktopAnalogClockApplet(uuid)


class DesktopAnalogClockSettings(Gtk.Grid):

    def __init__(self, setting):
        super().__init__()

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        self.grid_desktop = Gtk.Grid()
        self.grid_desktop.set_column_spacing(6)
        self.grid_desktop.set_row_spacing(6)
        self.grid_appearance = Gtk.Grid()
        self.grid_appearance.set_column_spacing(6)
        self.grid_appearance.set_row_spacing(6)

        self.stack.add_titled(self.grid_desktop, "desktop", "Desktop")
        self.stack.add_titled(self.grid_appearance, "appearance", "Appearance")

        self.label_show = Gtk.Label(label="Show on Desktop")
        self.label_show.set_halign(Gtk.Align.START)

        labels = ["", "X Position", "Y Position", "Scale"]  
        for i in range(4):
            label = Gtk.Label(label = labels[i])
            label.set_halign(Gtk.Align.START)
            self.grid_desktop.attach(label, 0, i, 1, 1)
        
        adj1 = Gtk.Adjustment(lower=1, upper=10000, step_incr=1)
        adj2 = Gtk.Adjustment(lower=1, upper=10000, step_incr=1)
        adj3 = Gtk.Adjustment(lower=1, upper=10000, step_incr=1)
        adj4 = Gtk.Adjustment(lower=1, upper=4, step_incr=1)
        
        self.spinx = Gtk.SpinButton()
        self.spinx.set_adjustment(adj1)
        self.spinx.set_halign(Gtk.Align.END)

        self.spiny = Gtk.SpinButton()
        self.spiny.set_adjustment(adj2)
        self.spiny.set_halign(Gtk.Align.END)

        self.spinscale = Gtk.SpinButton()
        self.spinscale.set_halign(Gtk.Align.END)
        self.spinscale.set_adjustment(adj3)
        self.spinclock = Gtk.SpinButton()
        self.spinclock.set_adjustment(adj4)
        self.grid_desktop.attach(self.spinx, 1, 1, 1, 1)
        self.grid_desktop.attach(self.spiny, 1, 2, 1, 1)
        self.grid_desktop.attach(self.spinscale, 1, 3, 1, 1)
        
        self.switchonoff = Gtk.Switch()
        self.switchonoff.set_halign(Gtk.Align.START)
        self.switchonoff.set_active(app_settings.get_boolean("show-desktop"))
        
        transp = app_settings.get_double("transparency")        
        
        self.scaletransp = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, .05)
        self.scaletransp.set_value(transp)
        self.scaletransp.connect("value-changed",self.on_transp_change)

        labels = ["", "Transparency", "Clock Face", "Face Color", "Hand Color", "Second Hand Color", "Show Seconds"]
        for i in range(7):
            label = Gtk.Label(label = labels[i])
            label.set_halign(Gtk.Align.START)
            self.grid_appearance.attach(label, 0, i, 1, 1)
        
        self.grid_appearance.attach(self.scaletransp, 1, 1, 1, 1)
        self.grid_appearance.attach(self.spinclock, 1, 2, 1, 1)

        self.setting_name = ["color-face", "color-hands", "color-seconds"]
        self.colorbuttons = []
        for n in range(3):
            load_color = app_settings.get_string(self.setting_name[n])
            color = Gdk.RGBA()
            if load_color == "none":
                color.parse("rgba(0,0,0,0)")
            else:
                color.parse(load_color)
            button = Gtk.ColorButton.new_with_rgba(color)
            button.connect("color_set",self.on_color_changed,self.setting_name[n])
            self.colorbuttons.append(button)
            self.grid_appearance.attach(self.colorbuttons[n], 1, n+3, 1, 1)
        
        self.switch_seconds = Gtk.Switch()
        self.switch_seconds.set_halign(Gtk.Align.END)
        self.switch_seconds.set_active(app_settings.get_boolean("show-seconds"))

        self.grid_appearance.attach(self.switch_seconds, 1, 6, 1, 1)

        app_settings.bind("x",self.spinx,"value",Gio.SettingsBindFlags.DEFAULT)
        app_settings.bind("y",self.spiny,"value",Gio.SettingsBindFlags.DEFAULT)
        app_settings.bind("scale",self.spinscale,"value",Gio.SettingsBindFlags.DEFAULT)     
        app_settings.bind("show-desktop",self.switchonoff,"active",Gio.SettingsBindFlags.DEFAULT)
        app_settings.bind("clock-number",self.spinclock,"value",Gio.SettingsBindFlags.DEFAULT)
        app_settings.bind("show-seconds",self.switch_seconds,"active",Gio.SettingsBindFlags.DEFAULT)

        self.switcher = Gtk.StackSwitcher()
        self.switcher.set_stack(self.stack)
        self.attach(self.label_show, 0, 0, 1, 1)
        self.attach(self.switchonoff,1, 0, 1, 1)
        self.attach(Gtk.Label(label=""), 0, 1, 2, 1)
        self.attach(self.switcher, 0, 2, 2, 1)
        self.attach(self.stack, 0, 3, 2, 1)
        self.show_all()
        
    def on_transp_change(self,event):
        app_settings.set_double("transparency",self.scaletransp.get_value())


    def on_settings_change (self, settings, name):
        if name == "show-desktop":
            self.switchonoff.set_active(app_settings.get_boolean("show-desktop"))

    def on_color_changed(self, button, clock_part):
        color = button.get_color()
        hex_code = "#{:02x}{:02x}{:02x}".format(int(color.red/256),
                                                int(color.green/256),
                                                int(color.blue/256))
        app_settings.set_string(clock_part, hex_code)
      

class DesktopAnalogClockApplet(Budgie.Applet):
    """ Budgie.Applet is in fact a Gtk.Bin """
    manager = None

    def __init__(self, uuid):

        Budgie.Applet.__init__(self)

        self.uuid = uuid
        self.runclock = app_settings.get_boolean("show-desktop")
        if self.runclock:
            try:
                p = subprocess.Popen([CLOCK_CMD])
            except:
                print("Could not start clock")    
        
        app_settings.connect("changed",self.on_settings_change)
        
    def on_settings_change(self, setting, name):
        if name == "show-desktop":
            show_clock = app_settings.get_boolean("show-desktop")
            if show_clock:
                try:
                    p = subprocess.Popen([CLOCK_CMD])
                except:
                    print("Could not start clock")
            else:
                try:
                    p = subprocess.Popen([cmd,"--quit"])
                    p = subprocess.Popen(["pkill","desktop-clock.py"])
                except:
                    pass

    def do_supports_settings(self):
        """Return True if support setting through Budgie Setting,
        False otherwise.
        """
        return True

    def do_get_settings_ui(self):
        """Return the applet settings with given uuid"""
        return DesktopAnalogClockSettings(self.get_applet_settings(self.uuid))
