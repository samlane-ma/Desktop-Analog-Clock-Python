#!/usr/bin/env bash
sudo cp com.github.samlane-ma.desktop-analog-clock.gschema.xml /usr/share/glib-2.0/schemas
sudo glib-compile-schemas /usr/share/glib-2.0/schemas
sudo mkdir /usr/lib/budgie-desktop/plugins/DesktopAnalogClock/
sudo cp *.png /usr/lib/budgie-desktop/plugins/DesktopAnalogClock/
sudo chmod +x desktop-clock.py
sudo cp *.py /usr/lib/budgie-desktop/plugins/DesktopAnalogClock/
sudo cp *.plugin /usr/lib/budgie-desktop/plugins/DesktopAnalogClock/
