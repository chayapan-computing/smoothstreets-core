from MapEditor import UTMCoordinateConverter
from tkinter import *

if __name__ == '__main__':
    root = Tk()
    root.geometry(f"{960}x{640}")
    root.title("UTM Grid: smoothstreets-core")
    scrollbar = Scrollbar(root)
    scrollbar.pack( side = RIGHT, fill=Y )
    UTMCoordinateConverter(root).pack(fill=BOTH,side=LEFT)
    root.mainloop()