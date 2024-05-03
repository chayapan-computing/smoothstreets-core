#!/usr/bin/env python3
#
# Pipenv
#  pipenv run MapEditor.py 
#
# https://github.com/TomSchimansky/TkinterMapView
# https://www.pythontutorial.net/tkinter/tkinter-treeview/
# https://www.tutorialspoint.com/python/tk_entry.htm
#
#  map_widget.fit_bounding_box((<lat1>, <long1>), (<lat2>, <long2>))
#  marker_1.set_position(48.860381, 2.338594)  # change position
#  marker_1.delete()
#  marker_1.set_text("Colosseo in Rome")  # set new text
#
# 1. add new marker by clicking right-mouse
# 2. add polygon
# 3. get geocode by left click on map

from tkinter import *
from tkinter import ttk
from tkintermapview import TkinterMapView, convert_coordinates_to_address
import pygeohash as pgh
from utm import utm_zones, from_latlon, UTMZone

class MapEditor(Frame):
    def __init__(self, root, width, height):
        self._root = root
        self.tile_server = 0
        self.markers = {}
        Frame.__init__(self)
        # create map widget
        # map_widget = TkinterMapView(self, width=800, height=400, corner_radius=0)
        map_widget = TkinterMapView(self, width=width, height=height, corner_radius=0)
        # map_widget.place(relx=0.5, rely=0.8, anchor=CENTER)
        map_widget.pack(fill=BOTH,side=TOP)
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
        self._root.event_list.update("Get address %s" % adr)

    def add_marker_event(self, coords):
        print("Add marker:", coords)
        self.markers[(coords[0], coords[1])] = self.map_widget.set_marker(coords[0], coords[1], text="new marker")
        self._root.event_list.update("Add marker %s" % str(coords))

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

class UTMCoordinateConverter(Frame):
    def __init__(self, root):
        Frame.__init__(self)
        # lat,lng
        self.lat, self.lng = DoubleVar(self), DoubleVar(self)
        self.zoom, self.utm_coord = IntVar(self), Variable(self)
        self.geohash_6 = Variable(self)

        # row 1

        # zoom_conf_input = Entry(self, width=4, textvariable=self.zoom, font=('Calibri 10'))
        zoom_conf_input = Scale(self, label='Zoom:', from_=0, to=20, variable=self.zoom, orient=HORIZONTAL, digits=1, length=100)    
        zoom_conf_input.grid(row=0,column=0)

        label = Label(self, text='UTM')
        label.grid(row=0,column=1)

        utm_coord_input = Entry(self, width=40, textvariable=self.utm_coord, font=('Calibri 16'))
        utm_coord_input.grid(row=0,column=2)

        convert_btn = Button(self,text='Convert <Enter>', command=lambda : self.convert({}))
        convert_btn.grid(row=0, column=3)

        # row 2

        lat_scale = Scale(self, label='Latitude:', from_=-90, to=90, variable=self.lat, orient=HORIZONTAL, digits=8, length=210)
        lat_scale.grid(row=2, column=1)
        lat_input = Entry(self, textvariable=self.lat, font=('Calibri 10'))
        lat_input.grid(row=2,column=2)

        # row 3

        server_toggle_btn = Button(self,text='Toggle Tile Server', command=lambda : self.change_tile_server({}))
        server_toggle_btn.grid(row=3, column=0)

        long_scale = Scale(self, label='Longitude:', from_=-180, to=180, variable=self.lng, orient=HORIZONTAL, digits=9, length=210)
        long_scale.grid(row=3, column=1)
        lng_input = Entry(self, textvariable=self.lng, font=('Calibri 10'))
        lng_input.grid(row=3,column=2)

        # row 4
        Label(self, text='Geohash', font=('Calibri 16')).grid(row=4,column=0)

        geohash_input = Entry(self, width=12, textvariable=self.geohash_6, font=('Calibri 10'))
        geohash_input.grid(row=4,column=1)

        self.grid_list = Listbox(self)
        for g in utm_zones:
            self.grid_list.insert(0, g)
        self.grid_list.grid(row=4,column=3)

        # row 5
        self.map_widget = TkinterMapView(self, width=800, height=300, corner_radius=0)
        self.map_widget.grid(row=5,column=0,columnspan=4)
        self.map_widget.set_zoom(15)
        self.zoom.set(15)
        self.map_widget.set_position(13.9051778, 100.4880157)  # Bangkok, Thailand
        self.map_widget.add_right_click_menu_command(label="Add Marker",
                                        command=self.add_marker, pass_coords=True)
        self.tile_server = 0 # id of tile server

        # self.pack()
        # self.place(relx=0.5, rely=0.5, anchor=CENTER)
        root.utm_widget = self
        root.bind('<Return>',self.convert)
        self._root = root

    def change_tile_server(self, params=None):
        """
        https://github.com/TomSchimansky/TkinterMapView?tab=readme-ov-file#use-other-tile-servers
        """
        print("Change tile server.")
        if self.tile_server == 0:
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite
            self.tile_server = 1
        else:
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")  # OpenStreetMap (default)
            self.tile_server = 0
    
    def convert(self, e):
        pos = self.map_widget.get_position()
        self._root.event_list.update("UTM Convert. Map center is %s" % str(pos))
        self.lat.set(pos[0])
        self.lng.set(pos[1])

        # 
        lat = float(self.lat.get())
        lng = float(self.lng.get())
        coord = self.utm_coord.get()
        # print(coord)
        output = from_latlon(lat,lng)
        zone = "%s%s" % (output[-2], output[-1])
        z = UTMZone(zone)
        print(z)
        print(z.N)
        print(output[-2], output[-1])
        self.utm_coord.set(output)
        print(e)
        geohash_val = pgh.encode(lat,lng, precision=6)
        self._root.event_list.update("Geohash: %s" % geohash_val)
        self.geohash_6.set(geohash_val)
        print(geohash_val)

        gx = int(output[0])
        gy = int(output[1])
        txt = f'{zone} / {geohash_val} / {pos}\nx={gx} y={gy}'
        # self.map_widget.set_marker(self.lat.get(), self.lng.get(), text=txt)


    def add_marker(self, coords):
        print("Add marker:", coords)
        self.lat.set(coords[0])
        self.lng.set(coords[1])
        output = from_latlon(self.lat.get(),self.lng.get())
        zone = "%s%s" % (output[-2], output[-1])
        gx = int(output[0])
        gy = int(output[1])
        self._root.event_list.update("UTM Add marker %s %s" % (zone, str(coords)))
        self.map_widget.set_marker(coords[0], coords[1], text=f'{coords[0],coords[1]}\n{zone} x={gx} y={gy}')
        self.lat.set(coords[0])
        self.lng.set(coords[1])

class EventList(Frame):
    def __init__(self, root):
        Frame.__init__(self)
        self.events = Listbox(self, width=80)
        self.events.insert(0, "Hello")
        self.events.pack()
        self.pack()
        self.place(relx=0.5, rely=0.2, anchor=CENTER)
        root.event_list = self
    def update(self, msg):
        self.events.insert(0, msg)

def main():
    """Map Editor tool with UTM"""
    root = Tk() # create tkinter window
    root.geometry(f"{1200}x{800}+0+0")
    root.title("Map Editor: smoothstreets-core")
    notebook = ttk.Notebook(root)
    notebook.pack(fill=BOTH, pady=10, expand=True)
    # create frames
    frame1 = ttk.Frame(notebook)
    frame2 = MapEditor(notebook, width=1200, height=800)
    frame3 = UTMCoordinateConverter(notebook)
    frame4 = EventList(notebook)
    frame1.pack(fill='both', expand=True)
    frame2.pack(fill='both', padx=0, pady=0, expand=True)
    frame3.pack(fill='both', expand=True)
    frame4.pack(fill='both', expand=True)
    # add frames to notebook
    notebook.add(frame1, text='General Information')
    notebook.add(frame2, text='Map View')
    notebook.add(frame3, text='Convert UTM')
    notebook.add(frame4, text='Event List')
    
    btn_1 = Button(frame1, text='1').place(relx=0.1, rely=0.0, anchor=N)
    btn_2 = Button(frame1, text='2').place(relx=0.3, rely=0.0, anchor=N)
    btn_3 = Button(frame1, text='3').place(relx=0.5, rely=0.0, anchor=N)

    root.mainloop()

if __name__ == '__main__':
    main()