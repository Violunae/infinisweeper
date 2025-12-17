import tkinter as tk
from globals import Globals

from utils import * 

def clearScreen(color="black"):
    Globals.canvas.delete("all")
    Globals.canvas.config(background="blue")

def drawPolygon(camera: Camera, points, color="black"):
    trans_points = [camera.transform(point).getTuple() for point in points]
    flat_points = [coord for point in trans_points for coord in point]

    Globals.canvas.create_polygon(flat_points, fill=color, width=1)

def drawRect(camera: Camera, pos: Vec, size: Vec, color="black"):
    top_left = pos
    top_right = Vec(pos.x + size.x, pos.y)
    bottom_right = Vec(pos.x + size.x, pos.y + size.y)
    bottom_left = Vec(pos.x, pos.y + size.y)
    
    drawPolygon(camera, [top_left, top_right, bottom_right, bottom_left], color)