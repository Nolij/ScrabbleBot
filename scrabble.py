import json as JSON
import re as RegExp
import sys
import time as Time
import threading as Threading
from watchdog.observers import Observer
import multiprocessing as MultiProcessing
import tkinter as Tk
from PIL import Image, ImageTk
import random as Random
from random import random as RNG
from random import shuffle as Shuffle
from copy import copy as Copy
from copy import deepcopy as DeepCopy
import wordlib as WordLib

WORDLIST = tuple()

class UpdateWordList():
	def dispatch(self):
		global WORDLIST
		Time.sleep(0.05)
		WORDFILE = open("words.json", "r")
		WORDLIST = tuple(JSON.loads(WORDFILE.read()))
		WORDFILE.close()

WordListUpdater = Observer()
WordListUpdater.schedule(UpdateWordList, "words.json")
WordListUpdater.start()
UpdateWordList().dispatch()

LETTERS = WordLib.LETTERS

BLANKS = WordLib.BLANKS

VALUES = WordLib.VALUES

TILE = 0
DOUBLEWORD = 1
TRIPLEWORD = 2
DOUBLELETTER = 3
TRIPLELETTER = 4
CENTER = 5
LETTER = 6

BOARD = (
	(TRIPLEWORD, TILE, TILE, DOUBLELETTER, TILE, TILE, TILE, TRIPLEWORD, TILE, TILE, TILE, DOUBLELETTER, TILE, TILE, TRIPLEWORD),
	(TILE, DOUBLEWORD, TILE, TILE, TILE, TRIPLELETTER, TILE, TILE, TILE, TRIPLELETTER, TILE, TILE, TILE, DOUBLEWORD, TILE),
	(TILE, TILE, DOUBLEWORD, TILE, TILE, TILE, DOUBLELETTER, TILE, DOUBLELETTER, TILE, TILE, TILE, DOUBLEWORD, TILE, TILE),
	(DOUBLELETTER, TILE, TILE, DOUBLEWORD, TILE, TILE, TILE, DOUBLELETTER, TILE, TILE, TILE, DOUBLEWORD, TILE, TILE, DOUBLELETTER),
	(TILE, TILE, TILE, TILE, DOUBLEWORD, TILE, TILE, TILE, TILE, TILE, DOUBLEWORD, TILE, TILE, TILE, TILE),
	(TILE, TRIPLELETTER, TILE, TILE, TILE, TRIPLELETTER, TILE, TILE, TILE, TRIPLELETTER, TILE, TILE, TILE, TRIPLELETTER, TILE),
	(TILE, TILE, DOUBLELETTER, TILE, TILE, TILE, DOUBLELETTER, TILE, DOUBLELETTER, TILE, TILE, TILE, DOUBLELETTER, TILE, TILE),
	(TRIPLEWORD, TILE, TILE, DOUBLELETTER, TILE, TILE, TILE, CENTER, TILE, TILE, TILE, DOUBLELETTER, TILE, TILE, TRIPLEWORD),
	(TILE, TILE, DOUBLELETTER, TILE, TILE, TILE, DOUBLELETTER, TILE, DOUBLELETTER, TILE, TILE, TILE, DOUBLELETTER, TILE, TILE),
	(TILE, TRIPLELETTER, TILE, TILE, TILE, TRIPLELETTER, TILE, TILE, TILE, TRIPLELETTER, TILE, TILE, TILE, TRIPLELETTER, TILE),
	(TILE, TILE, TILE, TILE, DOUBLEWORD, TILE, TILE, TILE, TILE, TILE, DOUBLEWORD, TILE, TILE, TILE, TILE),
	(DOUBLELETTER, TILE, TILE, DOUBLEWORD, TILE, TILE, TILE, DOUBLELETTER, TILE, TILE, TILE, DOUBLEWORD, TILE, TILE, DOUBLELETTER),
	(TILE, TILE, DOUBLEWORD, TILE, TILE, TILE, DOUBLELETTER, TILE, DOUBLELETTER, TILE, TILE, TILE, DOUBLEWORD, TILE, TILE),
	(TILE, DOUBLEWORD, TILE, TILE, TILE, TRIPLELETTER, TILE, TILE, TILE, TRIPLELETTER, TILE, TILE, TILE, DOUBLEWORD, TILE),
	(TRIPLEWORD, TILE, TILE, DOUBLELETTER, TILE, TILE, TILE, TRIPLEWORD, TILE, TILE, TILE, DOUBLELETTER, TILE, TILE, TRIPLEWORD)
)
HEIGHT, WIDTH = len(BOARD), len(BOARD[0])

TILE_COLOR = {
	LETTER : "#ddddee",
	TILE : "#eeeedd",
	DOUBLEWORD : "#ffb1c4",
	TRIPLEWORD : "#ff4040",
	DOUBLELETTER : "#c3d2fe",
	TRIPLELETTER : "#3091d8"
}
TILE_COLOR[CENTER] = TILE_COLOR[DOUBLEWORD]
TILE_COLOR[LETTER] = "#%.6x" % (int(TILE_COLOR[TILE][1:], 16) - int("111111", 16))

TILE_TEXT = {
	DOUBLEWORD : "DOUBLE\nWORD\nSCORE",
	TRIPLEWORD : "TRIPLE\nWORD\nSCORE",
	DOUBLELETTER : "DOUBLE\nLETTER\nSCORE",
	TRIPLELETTER : "TRIPLE\nLETTER\nSCORE"
}

TILESIZE = 50

Window = Tk.Tk()
Window.title("Scrabble")
Window.wm_resizable(False, False)
Canvas = Tk.Canvas(Window, width = WIDTH * TILESIZE, height = (HEIGHT + 1) * TILESIZE)

Images = []

def create_rectangle(x1, y1, x2, y2, **kwargs):
	I = None
	if ("alpha" in kwargs):
		alpha = int(kwargs.pop("alpha") * 255)
		fill = kwargs.pop("fill")
		fill = Window.winfo_rgb(fill) + (alpha,) 
		image = Image.new("RGBA", (x2 - x1, y2 - y1), fill)
		Images.append(ImageTk.PhotoImage(image))
		I = Canvas.create_image(x1, y1, image = Images[-1], anchor = "nw")
	R = Canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
	return (R, I)

Inputs = []

MousePos = (-1, -1)
MousePressed = 0
def Click(Event):
	global MousePressed
#	print("RAW POSITION:\t" + str(Event.x) + ", " + str(Event.y))
#	print("BOARD POSITION:\t" + str((Event.y // TILESIZE, Event.x // TILESIZE)))
	Inputs.append((Event.num, Event.x // TILESIZE, Event.y // TILESIZE))
	MousePressed += 2 ** (Event.num - 1)
def Release(Event):
	global MousePressed
	MousePressed -= 2 ** (Event.num - 1)
def Move(Event):
	global MousePos
	MousePos = (Event.x // TILESIZE, Event.y // TILESIZE)
def WaitForInput(WaitForRelease = True):
	while (len(Inputs) == 0 or (WaitForRelease and MousePressed > 0)):
		Window.update_idletasks()
		Window.update()
		Time.sleep(0.01)
	return Inputs.pop(0)

Canvas.bind("<Button>", Click)
Canvas.bind("<ButtonRelease>", Release)
Canvas.bind("<Motion>", Move)
Canvas.pack()

for Y in range(len(BOARD)):
	Row = BOARD[Y]
	for X in range(len(Row)):
		Column = Row[X]
		create_rectangle(X * TILESIZE, Y * TILESIZE, (X + 1) * TILESIZE, (Y + 1) * TILESIZE, fill = TILE_COLOR[Column])
		if (Column in TILE_TEXT.keys()):
			Canvas.create_text((X + 0.5) * TILESIZE, (Y + 0.5) * TILESIZE, fill = "#000000", font = "Storopia %d bold" % (TILESIZE / 5.6), text = TILE_TEXT[Column], justify = "center")
		elif (Column == CENTER):
			_X, _Y = (X + 0.5) * TILESIZE, (Y + 0.5) * TILESIZE
			Canvas.create_polygon(
				_X - TILESIZE / 3, _Y - TILESIZE / 16, 
				_X - TILESIZE / 8, _Y - TILESIZE / 16, 
				_X, _Y - TILESIZE / 3, 
				_X + TILESIZE / 8, _Y - TILESIZE / 16,
				_X + TILESIZE / 3, _Y - TILESIZE / 16,
				_X + TILESIZE / 6, _Y + TILESIZE / 12,
				_X + TILESIZE / 4, _Y + TILESIZE / 3,
				_X, _Y + TILESIZE / 6,
				_X - TILESIZE / 4, _Y + TILESIZE / 3,
				_X - TILESIZE / 6, _Y + TILESIZE / 12
			)

PlacedTiles = {}
Bag = list(LETTERS.keys())
Shuffle(Bag)
Bank = []

Middle = TILESIZE * len(BOARD[0]) / 2

def DrawTile(Letter, Location = None):
	if (Location == None):
		Letter, Location = '.', Letter
	Position = (Location[0] + TILESIZE * 0.05, Location[1] + TILESIZE * 0.05, Location[0] + TILESIZE * 0.95 - 1, Location[1] + TILESIZE * 0.95 - 1)
	return (
		*create_rectangle(*Position, fill = TILE_COLOR[LETTER]), 
		Canvas.create_text((Position[0] + Position[2]) / 2, (Position[1] + Position[3]) / 2, fill = "#000000", font = "Storopia %d bold" % (TILESIZE / 2), text = Letter != '.' and Letter.upper() or ' ', justify = "center"), 
		Canvas.create_text((Position[0] + Position[2]) / 2 + TILESIZE / 3, (Position[1] + Position[3]) / 2 + TILESIZE / 3, fill = "#000000", font = "Storopia %d bold" % (TILESIZE / 7), text = Letter != '.' and str(VALUES[Letter]) or ' ', justify = "center"))

BankImages = []
def DrawBank(Bank):
	for ImageSet in BankImages:
		for Image in ImageSet:
			if (Image != None): Canvas.delete(Image)
	while (len(BankImages) > 0):
		del BankImages[0]
	Location = Start = Middle - TILESIZE * len(Bank) / 2
	for Letter in Bank:
		BankImages.append(DrawTile(Letter, (Location, TILESIZE * len(BOARD))))
		Location += TILESIZE

for i in range(7):
	Bank.append(Bag.pop())

DrawBank(Bank)
while True:
	Button, X, Y = WaitForInput(False)

	Init = DrawTile((X * TILESIZE, Y * TILESIZE))
	Tiles = []

	while (MousePressed > 0):
		for ImageSet in Tiles:
			for Image in ImageSet:
				if (Image != None): Canvas.delete(Image)
		EndX, EndY = MousePos

		Offset = -1
		if (abs(EndY - Y) <= abs(EndX - X)):
			EndY = Y
			Offset = EndX - X
		else:
			EndX = X
			Offset = EndY - Y

	#	_X, EndX = min(X, EndX), max(X, EndX)
	#	_Y, EndY = min(Y, EndY), max(Y, EndY)
		
		for i in range((Offset < 0 and -1 or 1), Offset + (Offset < 0 and -1 or 1), (Offset < 0 and -1 or 1)):
			if (EndY == Y):
				Tiles.append(DrawTile(((X + i) * TILESIZE, Y * TILESIZE)))
			else:
				Tiles.append(DrawTile((X * TILESIZE, (Y + i) * TILESIZE)))

		Window.update_idletasks()
		Window.update()
		Time.sleep(0.01)
	for ImageSet in Tiles:
		for Image in ImageSet:
			if (Image != None): Canvas.delete(Image)
	EndX, EndY = MousePos

	for Image in Init:
		if (Image != None): Canvas.delete(Image)
	