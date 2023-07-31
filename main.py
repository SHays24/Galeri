from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import sv_ttk
import re
import os
from pathlib import Path
from PIL import ImageTk, Image, ImageOps


class MainApplication(Tk):
	def __init__(self):
		self.started = False
		super().__init__()
		try:
			open("settings.txt", "r")
		except FileNotFoundError:
			setFolder()
		self.title("Galeri")
		chatterbox = PhotoImage(file="./chatterbox.png")
		self.iconphoto(False, chatterbox)
		sv_ttk.set_theme("dark")
		self.option_add('*tearOff', False)

	def IndexFoto(directory, pos):
		index = os.listdir(directory)
		index.sort()
		if pos < 0 | pos >= len(index):
			return None
		name = index[pos]
		path = os.path.join(directory, name)
		return path

	def setFolder(bug="fdfkd"):
		folder = filedialog.askdirectory()
		if folder:
			f = open("settings.txt", "wt")
			f.write("folder:" + folder + ";")
			f.close()
	try:
		f = open("settings.txt", "r")
	except FileNotFoundError:
		setFolder()
		f = open("setting.txt", "r")

	def load_images(self, directory):
		p = Path(directory)
		image_files = list(p.glob('*.jpg'))
		return image_files


class ImageGrid:
	def __init__(self, root):
		# Create a canvas to hold the grid of images
		self.canvas = tk.Canvas(root, width=root.winfo_width(), height=root.winfo_height(), scrollregion=(0, 0, 0, 9000))
		self.frame = tk.Frame(self.canvas)
		self.ys = ttk.Scrollbar(self.canvas, orient='vertical', command=self.canvas.yview)
		self.ys.pack(side="right", fill="y")
		self.canvas.configure(yscrollcommand=self.ys.set)
		self.canvas.pack(side="left", fill="both", expand=True)
		self.canvas.create_window((4, 4), window=self.frame, anchor="nw", tags="self.canvas")
		self.frame.bind("<Configure>", self.FrameConfig)
		# Iterate over the image files and create ImageTk.PhotoImage objects
		self.Thumbs = []
		self.Imgs = []
		self.Exif = []
		for file in image_files:
			img = Image.open(file)
			img = ImageOps.exif_transpose(img)
			exif = img.getexif()
			img.thumbnail((img.width, 150))	 # Resize the image
			photo = ImageTk.PhotoImage(img)
			imgref = ImageRef(self, photo, img, exif)
			self.Imgs.append(imgref)
			print(imgref.getDate())
			self.Thumbs.append(photo)
		print(ImageRef.getMonths(self.Imgs))
		self.ShowGrid(self.Thumbs)
		# Create a grid of labels and display the images
		root.bind('<Button-4>', lambda e: self.canvas.yview_scroll(int(-1*e.num), 'units'))
		root.bind('<Button-5>', lambda e: self.canvas.yview_scroll(int(1*e.num), 'units'))

	def ShowGrid(root, Thumbs):
		x=0
	for i, photo in enumerate(Thumbs):
		label = ttk.Label(root.frame, image=photo)
		label.grid(row=(x+1), column=(i%4))
		if i%4==3:
			x=x+1
			print("bazoopa"+ str(x))
		# Keep a reference to the image to prevent garbage collection
		# label.image = photo

	def RowScale(root, Percent=100):
		Thumbs = []
		row = root.canvas.grid_slaves(0)
		i = 0
		for i, column in enumerate(row):
			img = root.Imgs[int(i)]
			img.thumbnail((img.width, Percent))
			photo = ImageTk.PhotoImage(img)
			Thumbs.append(photo)
		print("yolo")
		root.ShowGrid(Thumbs)
	def FrameConfig(self, event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))
	def ClearGrid(self):
		for widget in self.frame.winfo_children():
			widget.destroy()
			
class MenuBar:
	def __init__(self, root):
		win = root
		self.menubar = tk.Menu(win)
		win['menu'] = self.menubar
		#options
		self.menu_file = tk.Menu(self.menubar)
		self.menu_filter = tk.Menu(self.menubar)
		self.menu_filter.year = tk.Menu(self.menu_filter)
		self.menubar.add_cascade(menu=self.menu_file, label='File')
		def setFolder():
			MainApplication.setFolder()
		self.menu_file.add_command(label='Select', command=setFolder)
		self.menubar.add_cascade(menu=self.menu_filter, label='Filter')
		self.menu_filter.add_cascade(menu=self.menu_filter.year, label='Year')
	def addSubmenu(upmenu, oplist):
		for option in oplist:
			upmenu.add_command(label=option.__name__, command=option)
class ImageRef:
	def __init__(self, root, image, thumbnail, exif):
		self.image = image
		self.thumbnail = thumbnail
		self.data = exif
		self.date = exif[306]
	def getDate(self):
		return self.date
	def getImage(self):
		return self.image
	def getMonths(imglist):
		monthlist = []
		i = 0
		for img in imglist:
			monthlist.append(imglist[i].getDate().split(":")[1])
			i+=1
		return (list(set(monthlist)))
	def getYears(imglist):
		yearlist = []
		i = 0
		for img in imglist:
			yearlist.append(imglist[i].getDate().split(":")[0])
			i+=1
		return (list(set(yearlist)))
if __name__ == '__main__':
	app = MainApplication()
	app.attributes('-zoomed', True)
	# Create the image grid
	f = open("settings.txt", "r")
	directory = re.search(r"(?<=folder:)\/[^;]+", f.read())
	try:
		print(directory.group(0))
	except:
		app.setFolder()
	image_files = app.load_images(directory.group(0)) # image file list stored here
	print(image_files)
	app.menubar = MenuBar(app)
	app.ImageGrid = ImageGrid(app)
	#app.menubar = MenuBar(app)
	def hello():
		print("hello")
	def hello1():
		print("hell1o")
	def command():
		MenuBar.addSubmenu(app.menubar.menu_filter.year, [hello, hello1])
	bt = ttk.Button(app, command=command)
	bt.pack()
	#ImageGrid.RowScale(root=app.ImageGrid, 14)
	app.mainloop()
