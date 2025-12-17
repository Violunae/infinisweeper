import tkinter as tk
import game
from utils import *
from globals import Globals

def move(event):
    global map

    map.camera.pos = Vec(-event.x, -event.y)
    map.update()
    map.draw()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x500")
    Globals.canvas = tk.Canvas(root, width=500, height=500)
    Globals.canvas.pack()

    map = game.Map()

    Globals.canvas.bind("<B1-Motion>", move)

    map.update()
    map.draw()

    root.mainloop()