#!/usr/bin/python3

import gi
import sys
import time
import datetime
import os
from math import sin, cos, pi
import cairo
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
import random

app_settings = Gio.Settings.new("com.github.samlane-ma.desktop-analog-clock")
roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

class DesktopAnalogWindow(Gtk.ApplicationWindow):

    def __init__(self):
        super( ).__init__()
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual != None and screen.is_composited():
            self.set_visual(visual)
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
        self.set_decorated(False)
        self.connect("delete-event", Gtk.main_quit)
        self.clock_area = Gtk.DrawingArea()
        #self.clock = Gtk.Image()
        self.update("","initial")
        GLib.timeout_add_seconds(1,self.load_clock)
        self.show_all()
        app_settings.connect("changed",self.update)
        self.init_ui()

    def init_ui(self):

        self.clock_area.connect("draw", self.on_draw)
        self.add(self.clock_area)
        self.resize(self.scale, self.scale)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def on_draw(self, wid, cr):

        color = Gdk.RGBA()
        self.hour_x, self.hour_y, self.min_x, self.min_y, self.sec_x, self.sec_y = self.get_coords()
        center_x = self.scale / 2
        center_y = self.scale / 2

        # Face of clock (just a white circle)
        color.parse(self.facecolor)
        cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)
        cr.arc(center_x, center_y, (self.scale - 2) / 2, 0, 2 * pi)
        cr.fill()

        color.parse("black")
        cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)
        cr.set_line_width(self.scale / 50)
        cr.arc(center_x, center_y, (self.scale - self.scale / 50) / 2, 0, 2 * pi)
        cr.stroke()

        number_offset = 0.85

        # Draw tick marks on odd numbered clocks
        if self.clock_number % 2 == 1:
            number_offset = 0.77
            for i in range(60):
                radians = i * (pi * 2) / 60
                if i % 5 == 0:
                    len = .12
                    linewid = self.scale / 90 + 1
                else:
                    len = .08
                    linewid = self.scale / 180 + 1
                cr.set_line_width(linewid)
                m_x = round (center_x + (center_y * (1.0 - len)) * cos(radians))
                m_y = round (center_y + (center_y * (1.0 - len)) * sin(radians))
                s_x = round (center_x + center_y * cos(radians))
                s_y = round (center_y + center_y * sin(radians))
                cr.move_to (m_x, m_y)
                cr.line_to (s_x, s_y)
                cr.stroke()
        else:
            number_offset = 0.85

        # Draw numbers - regular on odd clock number, roman on even clock number
        for i in range(12):
            radians = i * (pi * 2) / 12
            cr.set_font_size(self.scale / 13)
            cr.select_font_face("", cairo.FontSlant.NORMAL, cairo.FontWeight.BOLD)
            number = i + 3
            if number > 12:
                number -= 12
            if self.clock_number > 2:
                cr.set_font_size(self.scale / 16)
                dtxt = roman[number-1]
            else:
                dtxt = str(number)
            (xx, yy, ww, hh, dx, dy) = cr.text_extents(dtxt)
            t_x = round (center_x + (center_y * number_offset) * cos(radians))
            t_y = round (center_y + (center_y * number_offset) * sin(radians))
            cr.move_to(t_x - ww/2 , t_y + hh/2)
            cr.show_text(dtxt)

        # Load and draw background clock image
        # Gdk.cairo_set_source_pixbuf(cr, self.pb, 0, 0)
        # cr.paint()

        # Make the hands have rounded ends
        cr.set_line_cap(1)

        # Draw the hour / minute hands
        color.parse(self.handcolor)
        cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)
        cr.set_line_width(self.scale / 80 + 1)
        cr.move_to(self.scale/2, self.scale/2)
        cr.line_to(self.hour_x, self.hour_y)
        cr.stroke()
        cr.move_to(self.scale/2, self.scale/2)
        cr.line_to(self.min_x, self.min_y)
        cr.stroke()

        # Draw the Seconds hand
        if self.show_seconds:
            color.parse(self.secondcolor)
            cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)
            if (self.scale / 70 - 2) < 1:
                cr.set_line_width(1)
            else:
                cr.set_line_width(self.scale / 70 - 1)
            cr.move_to(self.scale/2, self.scale/2)
            cr.line_to(self.sec_x, self.sec_y)
            cr.stroke()

        # Draw a small dot in the circle, so hands dont look weird in the center
        cr.arc(self.scale / 2, self.scale / 2, self.scale / 120 + 2, 0, 2 * pi)
        cr.fill()

    def update(self, setting, key):
        # Maybe fix this up a bit and bind the settings... right now everything
        # gets reloaded when one setting changes...
        self.x =  app_settings.get_int("x")
        self.y =  app_settings.get_int("y")
        self.scale = app_settings.get_int("scale")
        self.show_clock = app_settings.get_boolean("show-desktop")
        self.transp = app_settings.get_double("transparency")
        self.handcolor = app_settings.get_string("color-hands")
        self.secondcolor = app_settings.get_string("color-seconds")
        self.facecolor = app_settings.get_string("color-face")
        self.show_seconds = app_settings.get_boolean("show-seconds")
        self.clock_area.set_opacity(self.transp)
        self.clock_number = app_settings.get_int("clock-number")

        #clock_image = "ci" + str(self.clock_number)+".png"
        #CLOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),clock_image)

        if not self.show_clock:
             quit()
        # Don't need to reload image unless the image or scale changes
        #if key in ["scale","initial","clock-number"]:
        #    if os.path.isfile(CLOCK_FILE):
        #        self.pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(CLOCK_FILE, self.scale, self.scale, True)
        #    else:
        #        self.pb = GdkPixbuf.Pixbuf()
        #        print("unable to open ",CLOCK_FILE)
        self.move(self.x,self.y)
        self.resize(self.scale,self.scale)

    def load_clock(self):
        self.current_time = datetime.datetime.now()
        self.queue_draw()
        return True

    def get_coords(self):
        clock_time = datetime.datetime.now()
        hours = clock_time.hour
        if hours > 12:
            hours -= 12
        mins = clock_time.minute
        seconds = clock_time.second
        hours = hours * 60 + mins

        # mins = mins * 12 + (seconds / 5) # 1) Min hand moves constantly
        mins = mins * 12                   # 2) Min hand moves when min changes
        seconds = seconds * 12

        hours -= 180
        mins -= 180
        seconds -=180

        if hours < 0:
            hours = hours + 720
        if mins < 0:
            mins = mins + 720
        if seconds < 0:
            seconds = seconds + 720

        center_x = self.scale / 2
        center_y = self.scale / 2
        radians = (hours * (pi * 2) / 720)
        h_x = round (center_x + (center_x * .55) * cos(radians))
        h_y = round (center_y + (center_x * .55) * sin(radians))
        radians = (mins * (pi * 2) / 720)
        m_x = round (center_x + (center_y * .76) * cos(radians))
        m_y = round (center_y + (center_y * .76) * sin(radians))
        radians = (seconds * (pi * 2) / 720)
        s_x = round (center_x + (center_y * .81) * cos(radians))
        s_y = round (center_y + (center_y * .81) * sin(radians))

        return h_x, h_y, m_x, m_y, s_x, s_y


class DesktopAnalogClock(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="com.github.samlane-ma.desktop-analog-clock",
            **kwargs,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)

        self.window = None
        self.add_main_option("quit", ord("q"), GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "Quit Desktop Clock", None)

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        if options.contains("quit"):
            # This is printed on the main instance
            if Gtk.main_level() > 0:
                Gtk.main_quit()
            else:
                print("clock not active")
                quit()
        self.activate()
        return 0

    def do_activate(self):
        if not self.window:
            self.window = DesktopAnalogWindow()
            Gtk.main()


if __name__ == "__main__":
    desktop_clock = DesktopAnalogClock()
    desktop_clock.run(sys.argv)
