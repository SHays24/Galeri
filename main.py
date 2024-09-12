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
        self.thumblist = []

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
        f = open("settings.txt", "r")

    def load_images(self, directory):
        p = Path(directory)
        image_files = list(p.glob('*.jpg'))
        return image_files


class ImageGrid:
    def __init__(self, root):
        # Create a canvas to hold the grid of images
        self.win = root
        self.canvas = tk.Canvas(root, width=root.winfo_width(),
                                height=root.winfo_height(),
                                scrollregion=(0, 0, 0, 9000))
        self.frame = tk.Frame(self.canvas)
        self.ys = ttk.Scrollbar(self.canvas, orient='vertical',
                                command=self.canvas.yview)
        self.ys.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.ys.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw",
                                  tags="self.canvas")
        self.frame.bind("<Configure>", self.FrameConfig)
        # Iterate over the image files and create ImageTk.PhotoImage objects
        self.Thumbs = []
        self.Imgs = []
        self.Exif = []
        for file in image_files:
            img = Image.open(file)
            img = ImageOps.exif_transpose(img)
            exif = img.getexif()
            img.thumbnail((img.width, 150))  # Resize the image
            photo = ImageTk.PhotoImage(img)
            imgref = ImageRef(self, photo, img, exif)
            self.Imgs.append(imgref)
            self.Thumbs.append(photo)
        self.ShowGrid(self.Imgs)
        # Create a grid of labels and display the images
        root.bind('<Button-4>', lambda e: self.canvas.yview_scroll(int(-1*e.num),
                                                                   'units'))
        root.bind('<Button-5>', lambda e: self.canvas.yview_scroll(int(1*e.num),
                                                                   'units'))

    def getImgs(self, root):
        return root.Imgs

    def ShowGrid(root, Thumbs):
        root.ClearGrid()
        x = 0
        for i, photo in enumerate(Thumbs):
            image = photo.getImage()
            label = ttk.Label(root.frame, image=image)
            label.grid(row=(x+1), column=(i % 4))
            if i % 4 == 3:
                x = x + 1
            # Keep a reference to the image to prevent garbage collection
            # label.image = photo

    def RowScale(root, Percent=100):
        root.ClearGrid()
        Thumbs = []
        row = root.canvas.grid_slaves(0)
        i = 0
        for i, column in enumerate(row):
            img = root.Imgs[int(i)]
            img.thumbnail((img.width, Percent))
            photo = ImageTk.PhotoImage(img)
            Thumbs.append(photo)

        root.ShowGrid(Thumbs)

    def FrameConfig(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def ClearGrid(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


class MenuBar:
    def __init__(self, root):
        self.win = root
        self.menubar = tk.Menu(self.win)
        self.win['menu'] = self.menubar
        # options
        self.menu_file = tk.Menu(self.menubar)
        self.menu_filter = tk.Menu(self.menubar)
        self.menu_filter.year = tk.Menu(self.menu_filter)
        self.menu_filter.month = tk.Menu(self.menu_filter)
        self.menubar.add_cascade(menu=self.menu_file, label='File')

        def setFolder():
            MainApplication.setFolder()
        self.menu_file.add_command(label='Select', command=setFolder)
        self.menubar.add_cascade(menu=self.menu_filter, label='Filter')
        self.menu_filter.add_cascade(menu=self.menu_filter.year, label='Year')
        self.menu_filter.year.option = tk.StringVar()
        self.menu_filter.year.option.set("All")
        self.menu_filter.add_cascade(menu=self.menu_filter.month, label='Month')
        self.menu_filter.month.option = tk.StringVar()
        self.menu_filter.year.option.set("All")
        # self.option.set("All")

    def addSubmenu(self, menu, upmenu, oplist, command):
        if (command == "Year"):
            var = menu.menu_filter.year.option

            def find():
                fdr = ImageRef.findYears(self.win.ImageGrid.getImgs(
                                        self.win.ImageGrid),
                                        str(menu.menu_filter.year.option.get())
                                        )
                # fdr = self.win.ImageGrid.getImgs(self.win.ImageGrid)
                self.win.ImageGrid.ShowGrid(fdr)
        elif (command == "Month"):
            var = menu.menu_filter.month.option

            def find():
                fdr = ImageRef.findMonths(self.win.ImageGrid.getImgs(
                                        self.win.ImageGrid),
                                        str(
                                            menu.menu_filter.month.option.get()
                                        ))
                # fdr = self.win.ImageGrid.getImgs(self.win.ImageGrid)
                self.win.ImageGrid.ShowGrid(fdr)

        upmenu.add_radiobutton(label="All", variable=var, value="All",
                               command=lambda: find())

        for option in oplist:
            upmenu.add_radiobutton(label=option, variable=var, value=option,
                                   command=lambda: find())


class ImageRef:
    def __init__(self, root, image, thumbnail, exif):
        self.image = image
        self.img = thumbnail
        self.data = exif
        self.date = exif[306]
        self.root = root

    def getDate(self):

        return self.date

    def getImage(self):

        return self.image

    def getMonths(imglist):
        monthlist = []
        i = 0
        for img in imglist:
            monthlist.append(imglist[i].getDate().split(":")[1])
            i += 1
        return (list(set(monthlist)))

    def getYears(imglist):
        yearlist = []
        i = 0
        for img in imglist:
            yearlist.append(imglist[i].getDate().split(":")[0])
            i += 1
        yearlist = sorted(list(set(yearlist)))
        ["All"].extend(yearlist)
        return (yearlist)

    def findYears(imglist, year):
        foundY = []
        if (str(year) == "All"):
            foundY = imglist
        else:
            for img in imglist:
                if (img.getDate().split(":")[0] == str(year)):
                    foundY.append(img)
        return foundY

    def findMonths(imglist, Month):
        foundM = []
        if (str(Month) == "All"):
            foundM = imglist
        else:
            for img in imglist:
                if (img.getDate().split(":")[1] == str(Month)):
                    foundM.append(img)
        return foundM


if __name__ == '__main__':
    app = MainApplication()
    app.attributes('-zoomed', True)
    # Create the image grid
    f = open("settings.txt", "r")
    directory = re.search(r"(?<=folder:)\/[^;]+", f.read())
    '''try:
        dskl = directory.group(0)
    except:
        app.setFolder()'''
    image_files = app.load_images(directory.group(0))  # image file list stored here
    app.menubar = MenuBar(app)
    app.ImageGrid = ImageGrid(app)

    def YearMenu():
        app.menubar.addSubmenu(app.menubar, app.menubar.menu_filter.year,
                               ImageRef.getYears(app.ImageGrid.getImgs(app.ImageGrid)),
                               "Year")

    def MonthMenu():
        app.menubar.addSubmenu(app.menubar, app.menubar.menu_filter.month,
                               ImageRef.getMonths(
                                                    app.ImageGrid.getImgs(app.ImageGrid)),
                               "Month")
    YearMenu()
    MonthMenu()
    # ImageGrid.RowScale(root=app.ImageGrid, 1)
    app.mainloop()
