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
    except:
      setFolder() 
    self.title("Galeri")
    chatterbox = PhotoImage(file = "./chatterbox.png")
    self.iconphoto(False, chatterbox)
    self.nb = ttk.Notebook(self)
    sv_ttk.set_theme("dark")
    
  def IndexFoto(directory, pos):
    index = os.listdir(directory)
    index.sort()
    if pos < 0 | pos >= len(index):
      return None
    name = index[pos]
    path = os.path.join(directory, name)
    return path
    
    
  def setFolder():
    folder = filedialog.askdirectory()
    f = open("settings.txt", "wt")
    f.write("folder:" + folder + ";")
    f.close()
  try:
    open("settings.txt", "r")
  except:
    setFolder()
  def load_images(self, directory):
    p = Path(directory)
    image_files = list(p.glob('*.jpg'))
    return image_files
class ImageGrid:
  def __init__(self, root):
      # Create a canvas to hold the grid of images
      self.canvas = tk.Canvas(root, width = root.winfo_width(), height = 100, scrollregion=(0,0,0,5000))
      #self.frame = tk.Frame(self.canvas)
      self.ys = tk.Scrollbar(self.canvas, orient = 'vertical')
      self.canvas.configure(yscrollcommand=self.ys.set)
      self.canvas.grid(row=1, rowspan=10, column=1, columnspan=4)
      self.ys.grid(row=1, column=11, rowspan=4, sticky='n')
      #self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.canvas")
      # Iterate over the image files and create ImageTk.PhotoImage objects
      self.Thumbs = []
      self.Imgs = []
      for file in image_files:
          img = Image.open(file)
          img = ImageOps.exif_transpose(img)
          self.Imgs.append(img)
          img.thumbnail((img.width, 150))  # Resize the image
          photo = ImageTk.PhotoImage(img)
          self.Thumbs.append(photo)
      self.ShowGrid(self.Thumbs)
      # Create a grid of labels and display the images
  def ShowGrid(root, Thumbs):
      x=0
      for i, photo in enumerate(Thumbs):
          label = ttk.Label(root.canvas, image=photo)
          label.grid(row=(x+1), column=(i%4))
          if i%4==3:
            x=x+1
            print("bazoopa"+ str(x))
          # Keep a reference to the image to prevent garbage collection
          label.image = photo
        
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
if __name__ == '__main__':
  app = MainApplication()
  app.attributes('-zoomed', True)
  # Create the image grid
  f = open("settings.txt", "r")
  directory = re.search(r"(?<=folder:)\/[^;]+", f.read())
  print(directory.group(0))
  image_files = app.load_images(directory.group(0)) # image file list stored here
  print(image_files)
  app.ImageGrid = ImageGrid(app)
  def command():
    ImageGrid.RowScale(app.ImageGrid)
  bt = ttk.Button(app, command=command)
  bt.grid()
  #ImageGrid.RowScale(root=app.ImageGrid, 14)
  app.mainloop()

