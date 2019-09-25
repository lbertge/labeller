import Tkinter as tk
from PIL import Image, ImageTk
import glob
import os 
import csv
import logging

class Labeller:
    def __init__(self, datadir):
        self.choice = None
        self.datadir = datadir
        self.quit = False
    
    def getNotAnnotatedDirs(self):
        annotatedDirs = set()
        try:
            with open("annotations.csv", "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    annotatedDirs.add(row[0])
        except IOError:
            pass

        walker = os.walk(self.datadir)
        dirs = next(walker)
        allDirs = set([dirs[0] + d for d in dirs[1]])
        notAnnotatedDirs = allDirs - annotatedDirs

        return list(notAnnotatedDirs)

    def display(self, dirname):
        root = tk.Tk()
        w = tk.Canvas(root)

        imgs = glob.glob(dirname + "/*.png")
        imgs.sort()

        photos = []
        for img in imgs:
            image = Image.open(img)
            photo = ImageTk.PhotoImage(image)
            photos.append(photo)

        def on_click(i, event=None):
            logging.info("Selected image " + str(i))
            root.destroy()
            self.choice = imgs[i]

        def key_press(event):
            if event.char == 'q':
                self.quit = True
                root.destroy()
        
        def bad_data():
            logging.info("Marking as bad data - skipping")
            self.choice = dirname + "/"
            root.destroy()
        
        t = tk.Text(root, height=2, width=50)
        t.pack()
        t.insert(tk.END, "Click on the correctly rotated image. \n Press 'q' to quit")

        for i, img in enumerate(imgs):
            l = tk.Label(root, image=photos[i])
            l.pack(side=tk.LEFT)
            l.bind('<Button-1>', lambda event, i=i: on_click(i, event))

        b = tk.Button(root, text="Bad data", command=bad_data)
        b.pack()

        root.bind("<Key>", key_press)
        root.mainloop()
    
    def loop(self):
        dirs = self.getNotAnnotatedDirs()
        with open("annotations.csv", "a") as f:
            writer = csv.writer(f)
            for d in dirs:
                logging.info("Processing " + d)
                self.display(d)
                if self.quit:
                    return 
                if self.choice:
                    dirname, fname = os.path.split(self.choice)
                    writer.writerow([dirname, fname])


def main():
    logging.basicConfig(
        level=logging.INFO,
        format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    labeller = Labeller("data/")
    labeller.loop()

if __name__ == '__main__':
    main()
