#! python3
from tkinter import *
from tkinter import ttk
from time import perf_counter, sleep

import random
import os

from common import ExperimentFrame, InstructionsFrame
from gui import GUI


################################################################################


lotteryinstructions = """
V následující úloze můžete vyhrát peníze.

Můžete se rozhodnout, zda hodíte virtuální kostkou.

Vaše počáteční výhra je 5 Kč a tato výhra se zdvojnásobí pokaždé, když vám padne sudé číslo.
Pokud padne liché číslo, úloha končí a výhru v úloze ztrácíte.
Maximálně můžete takto vyhrát 1280 Kč.

Kdykoli můžete zmáčknout tlačítko 'Ukončit házení', a tím úlohu ukončit a odnést si dosaženou výhru.
"""

instructions = """Můžete se rozhodnout, že hodíte kostkou.
Vaše počáteční výhra je {} Kč a tato výhra se zdvojnásobí pokaždé, když vám padne sudé číslo.
Pokud padne liché číslo, úloha končí a výhru ztrácíte.
Maximálně můžete takto vyhrát {} Kč.
Pokud zmáčknete tlačítko 'Ukončit házení', úlohu ukončíte a odnesete si dosaženou výhru.
"""

winningText = "Vaše současná výhra je: {} Kč"
losingText = "Tímto úloha končí. Výhru jste ztratil(a)."
maximumText = "Více již vyhrát nemůžete. Tímto úloha končí. Vyhrál(a) jste: {} Kč"

################################################################################


class DiceLottery(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        #######################
        # adjustable parameters
        self.displayNum = self.createDots # self.createDots or self.createText
        self.fakeRolling = True # False for testing
        self.diesize = 240
        self.startingReward = 5
        self.maximumReward = 1280
        #######################

        self.width = self.root.screenwidth
        self.height = self.root.screenheight

        self.file.write("Dice Lottery\n")

        self.upperText = Text(self, height = 7, width = 80, relief = "flat", font = "helvetica 15",
                              wrap = "word")
        self.upperText.insert("1.0", instructions.format(self.startingReward, self.maximumReward))
        self.upperText["state"] = "disabled"
        self.die = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                          background = "white", width = self.diesize, height = self.diesize)
        self.bottomText = Text(self, height = 3, width = 80, relief = "flat", font = "helvetica 15",
                               wrap = "word")
        self.currentReward = self.startingReward
        self.bottomText.insert("1.0", winningText.format(self.currentReward))
        self.bottomText["state"] = "disabled"
        ttk.Style().configure("TButton", font = "helvetica 15")
        self.nextRoll = ttk.Button(self, text = "Hodit kostkou", command = self.roll, width = 14)
        self.endRolls = ttk.Button(self, text = "Ukončit házení", command = self.end, width = 14)
         
        self.upperText.grid(column = 1, row = 1, columnspan = 2)
        self.die.grid(column = 1, row = 3, pady = 40, columnspan = 2)
        self.bottomText.grid(column = 1, row = 4, columnspan = 2)
        self.nextRoll.grid(row = 5, column = 1, sticky = E, padx = 50)
        self.endRolls.grid(row = 5, column = 2, sticky = W, padx = 50)

        self["highlightbackground"] = "white"
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(0, weight = 3)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 1)
        self.rowconfigure(4, weight = 1)
        self.rowconfigure(5, weight = 1)
        self.rowconfigure(6, weight = 4)

        self.numberOfRolls = 0


    def roll(self):
        self.numberOfRolls += 1
        self.nextRoll["state"] = "disabled"
        self.endRolls["state"] = "disabled"
        self.die.create_rectangle((5, 5, self.diesize - 5, self.diesize - 5),
                                  fill = "white", tag = "die", outline = "black", width = 5)
        # fake rolling
        if self.fakeRolling:
            for roll in range(random.randint(4,6)):         
                self.displayNum(self.diesize/2, self.diesize/2, random.randint(1, 6))
                self.update()
                sleep(0.2)
                self.die.delete("dots")
        self.currentRoll = random.randint(1, 6)
        self.displayNum(self.diesize/2, self.diesize/2, self.currentRoll)
        self.bottomText["state"] = "normal"
        self.bottomText.delete("1.0", "end")
        if self.currentRoll % 2 == 0:
            self.currentReward *= 2
            if self.currentReward < self.maximumReward:
                self.bottomText.insert("1.0", winningText.format(self.currentReward))
                self.nextRoll["state"] = "!disabled"
            elif self.currentReward >= self.maximumReward:
                self.bottomText.insert("1.0", maximumText.format(self.maximumReward))        
        elif self.currentRoll % 2 == 1:
            self.currentReward = 0
            self.bottomText.insert("1.0", losingText)
            self.endRolls["text"] = "Pokračovat"
        self.bottomText["state"] = "disabled"
        self.update()        
        self.endRolls["state"] = "!disabled"


    def end(self):
        self.root.status["results"] += [f"V loterii jste vydělal(a) {self.currentReward} Kč."]
        self.root.status["reward"] += self.currentReward
        self.nextFun()


    def createDots(self, x0, y0, num):
        positions = {"1": [(0,0)],
                     "2": [(-1,-1), (1,1)],
                     "3": [(-1,-1), (0,0), (1,1)],
                     "4": [(-1,-1), (-1,1), (1,-1), (1,1)],
                     "5": [(-1,-1), (-1,1), (0,0), (1,-1), (1,1)],
                     "6": [(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0)]}
        for x, y in positions[str(num)]:
            d = self.diesize/4
            coords = [x0 + x*d + d/3, y0 - y*d + d/3,
                      x0 + x*d - d/3, y0 - y*d - d/3]
            self.die.create_oval(tuple(coords), fill = "black", tag = "dots")


    def createText(self, x0, y0, num):
        self.die.create_text(x0, y0, text = str(num), font = "helvetica 70", tag = "die")
        
                   
    def write(self):
        self.file.write("\t".join([self.id, str(self.numberOfRolls), str(self.currentReward)]) + "\n")
        

LotteryInstructions = (InstructionsFrame, {"text": lotteryinstructions, "height": 12})

if __name__ == "__main__":
    from intros import Ending
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([LotteryInstructions,
         DiceLottery,
         Ending
         ])
