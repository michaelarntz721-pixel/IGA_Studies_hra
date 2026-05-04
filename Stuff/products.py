#! python3

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import time, localtime, strftime, sleep,  perf_counter
from itertools import chain
from collections import defaultdict

import random
import os.path
import os

from common import ExperimentFrame, InstructionsFrame, read_all, Measure
from gui import GUI
from constants import TESTING



##################################################################################################################
# TEXTS #
#########

questionText = """Který z dvojice výrobků byste si raději odnesl(a) domů?
Vyberte kliknutím na obrázek."""

intro = """Nyní Vám postupně ukážeme 15 párů výrobků. U každého páru klikněte na ten výrobek, který byste si raději odnesli domů. Máte pravděpodobnost 10%, že vyhrajete náhodně vybraných 5 výrobků z těch, které si vyberete. Vybírejte proto prosím pečlivě, později už není možné volbu změnit. 
"""

notChosenText = """V úloze s výběrem výrobků jste nebyl(a) vylosován(a)."""
chosenText = """V úloze s výběrem výrobků jste byl(a) vylosován(a). Obdržíte náhodně vybrané výrobky z těch, které jste si vybral(a) v úloze. <b>Zapamatujte si číslo tašky {}, které sdělte při vyplácení odměny výzkumným asistentům.</b>"""


##################################################################################################################


ProductsIntro = (InstructionsFrame, {"text": intro, "height": 7})


class Choices(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        with open(os.path.join(os.path.dirname(__file__), "products.txt"), encoding = "utf-8") as f:
            self.infos = [line.rstrip().split("\t") for line in f]
        random.shuffle(self.infos)

        self.file.write("Products\n")        

        self.selected = defaultdict(list)

        self.order = -1                      

        self.text = ttk.Label(self, font = "helvetica 15", justify = "center", background = "white", text = questionText)
        self.text.grid(row = 0, column = 0, sticky = S, pady = 35)
             
        self.twoProducts = TwoProducts(self)
        self.twoProducts.grid(row = 1, column = 0)

        self.trialText = ttk.Label(self, text = "", font = "helvetica 15", background = "white", justify = "left", width = 15)
        self.trialText.grid(column = 0, row = 0, pady = 30, padx = 10, sticky = NE)

        self.columnconfigure(0, weight = 1)      
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(2, weight = 1)

        self.proceed()
        
    def proceed(self):
        self.order += 1
        self.trialText["text"] = f"Produkt {self.order + 1:>3}/{len(self.infos)}"

        if self.order == len(self.infos):
            self.root.status["products"] = self.selected
            if self.root.status["bag"] == "-1":
                self.root.status["results"] += [notChosenText]
            else:
                self.root.status["results"] += [chosenText.format(self.root.status["bag"])]
            self.nextFun()
        else:
            self.twoProducts.changeImages(self.infos[self.order][0])
            self.t0 = time()            


    def nextFun(self):        
        if self.root.status["bag"] != "-1":
            data = "_".join([i for i in self.selected.keys()]) + "|" + "_".join([i for i in self.selected.values()])
            data = {'id': self.id, 'round': "products", 'offer': data}
            self.sendData(data)
        super().nextFun()




class TwoProducts(Canvas):
    def __init__(self, root):
        super().__init__(root, highlightbackground = "white", highlightcolor = "white", background = "white")

        self.root = root
        self.selected = self.root.selected
            
        self.leftProduct = OneProduct(self)
        self.leftProduct.grid(column = 1, row = 1, padx = 5, sticky = NSEW)

        self.rightProduct = OneProduct(self)
        self.rightProduct.grid(column = 3, row = 1, padx = 5, sticky = NSEW)
                            
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(4, weight = 1)

    def proceed(self):
        self.root.proceed()

    def changeImages(self, product):
        self.sides = ["Bio", "Nebio"]
        random.shuffle(self.sides)
        left = os.path.join(os.path.dirname(__file__), "Products", self.sides[0], product)
        right = os.path.join(os.path.dirname(__file__), "Products", self.sides[1], product)
        if self.sides[0] == "Bio":
            leftDescription = self.root.infos[self.root.order][1]
            rightDescription = self.root.infos[self.root.order][2]
        else:   
            leftDescription = self.root.infos[self.root.order][2]
            rightDescription = self.root.infos[self.root.order][1]
        self.leftProduct.changeImage(left, leftDescription)
        self.rightProduct.changeImage(right, rightDescription)


class OneProduct(Canvas):
    def __init__(self, root):
        super().__init__(root, highlightbackground = "white", highlightcolor = "white")

        self["background"] = "white"

        self.root = root
        self.selected = self.root.selected

        self.product = Product(self)
        self.product.grid(column = 1, row = 0)

        self.label = ttk.Label(self, text = "", background = "white", font = "helvetica 15 bold", width = 55, anchor = "center")
        self.label.grid(column = 1, row = 1, pady = 8)
        self.bottomLabel = ttk.Label(self, text = "", background = "white", font = "helvetica 15")
        self.bottomLabel.grid(column = 1, row = 2, pady = 4)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1) 

    def changeImage(self, product, description):        
        self.product.changeImage(product + ".png")        
        self.label["text"] = description
            
    def proceed(self):
        self.root.proceed()

    def highlight(self):
        self.product.highlight()

    def removeHighlight(self):
        self.product.removeHighlight()



class Product(Label):
    def __init__(self, root):
        super().__init__(root, background = "white", foreground = "white", relief = "flat", borderwidth = 10)
        self.config(width=460, height=460)
        self["anchor"] = "center"

        self.root = root
        self.selected = self.root.selected

        self.bind("<Enter>", self.entered)
        self.bind("<Leave>", self.left)
        self.bind("<1>", self.clicked)        

    def changeImage(self, file):
        file = os.path.join(os.path.dirname(__file__), "Products", file)        
        self.image = PhotoImage(file = file)
        self["image"] = self.image
        self.file = file
        self.t0 = perf_counter()        

    def entered(self, _):
        self.config(cursor = "hand2")

    def left(self, _):
        self.config(cursor = "arrow")

    def clicked(self, _):
        if not TESTING:
            if perf_counter() - self.t0 < 0.2:            
                return
        name = os.path.basename(self.file).rstrip(".png")
        folder = os.path.basename(os.path.dirname(self.file))
        self.selected[name] = folder
        self.root.root.root.file.write("\t".join([self.root.root.root.id,
                                                  str(self.root.root.root.order + 1),
                                                  self.root.label["text"],
                                                  #str(self.root.root.root.current[0]),
                                                  self.root.root.leftProduct.label["text"],
                                                  self.root.root.rightProduct.label["text"],
                                                  str(time() - self.root.root.root.t0)]
                                                 ) + "\n")
        self.root.proceed()

    def highlight(self):
        self["background"] = "red"

    def removeHighlight(self):
        self["background"] = "white"
        





def main():
    os.chdir(os.path.dirname(os.getcwd()))
    from login import Login
    from intros import Ending
    GUI([#ProductsIntro,
         Login,
         Choices,
         Ending
         ])


if __name__ == "__main__":
    main()

