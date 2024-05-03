from tkinter import *
from MapEditor import UTMCoordinateConverter
from MapEditor import on_quit

def configure_menubar(root):
    root.option_add('*tearOff', FALSE)
    menubar = Menu(root)
    root['menu'] = menubar
    menu_file = Menu(menubar)
    menu_edit = Menu(menubar)
    menubar.add_cascade(menu=menu_file, label='File')
    menu_file.add_command(label='About', command=on_quit)
    menu_file.add_separator()
    menu_file.add_command(label='Quit/Exit <Ctrl-Q>', command=on_quit)
    menubar.add_cascade(menu=menu_edit, label='Edit')

if __name__ == '__main__':
    root = Tk()
    root.geometry(f"{960}x{640}")
    root.title("UTM Grid: smoothstreets-core")
    scrollbar = Scrollbar(root)
    scrollbar.pack( side = RIGHT, fill=Y )
    app = UTMCoordinateConverter(root)
    app.pack(fill=BOTH,side=LEFT)
    app.bind("Control-q", on_quit)
    app.bind("Control-x", on_quit)
    # Menu
    configure_menubar(root)
    root.mainloop()