#!/usr/bin/env python3
#
# Pipenv
#  pipenv run MapEditor.py 
#
# https://github.com/TomSchimansky/TkinterMapView
#
#
# 1. add new marker by clicking
# 2. add polygon

from tkinter import *
from tkintermapview import TkinterMapView, convert_coordinates_to_address


class MapEditor(Frame):
    def __init__(self, root):
        self.tile_server = 0
        self.markers = {}
        Frame.__init__(self)
        # create map widget
        map_widget = TkinterMapView(root, width=800, height=600, corner_radius=0)
        map_widget.place(relx=0.5, rely=0.5, anchor=CENTER)
        # set current widget position and zoom
        # map_widget.set_position(48.860381, 2.338594)  # Paris, France
        # map_widget.set_zoom(15)
        # set current widget position by address
        map_widget.set_address("Bangkok, Thailand")
        map_widget.add_right_click_menu_command(label="Add Marker",
                                        command=self.add_marker_event,
                                        pass_coords=True)
        map_widget.add_right_click_menu_command(label="Switch Tile Server",
                                        command=self.switch_tile_server,
                                        pass_coords=True)
        # add left click event
        map_widget.add_left_click_map_command(self.left_click_event)

        self.map_widget = map_widget

    def left_click_event(self, coordinates_tuple):
        print("Left click event with coordinates:", coordinates_tuple)
        lat, lng = coordinates_tuple
        adr = convert_coordinates_to_address(lat, lng)
        print(adr.street, adr.housenumber, adr.postal, adr.city, adr.state, adr.country, adr.latlng)


    def add_marker_event(self, coords):
        print("Add marker:", coords)
        self.markers[(coords[0], coords[1])] = self.map_widget.set_marker(coords[0], coords[1], text="new marker")
    def switch_tile_server(self, coords):
        """
        https://github.com/TomSchimansky/TkinterMapView?tab=readme-ov-file#use-other-tile-servers
        """
        if self.tile_server == 0:
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite
            self.tile_server = 1
        else:
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")  # OpenStreetMap (default)
            self.tile_server = 0

def main():
    """Map Editor tool with UTM"""
    # create tkinter window
    root = Tk()
    root.geometry(f"{500}x{320}")
    root.title("Map Editor: smoothstreets-core")
    editor = MapEditor(root)
    root.mainloop()

if __name__ == '__main__':
    main()