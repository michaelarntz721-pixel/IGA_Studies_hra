#! python3
# -*- coding: utf-8 -*- 

from tkinter import *
from tkinter import ttk
from time import perf_counter, sleep

import random
import os
import urllib.request
import urllib.parse

from common import ExperimentFrame, InstructionsFrame
from gui import GUI
from constants import TESTING, URL



################################################################################
# TEXTS
NUMGROUPS = 5

closeText = f"""<center>Ze skupin níže vyberte kliknutím na tlačítko {NUMGROUPS} skupin, které jsou Vám nejbližší.
(Dalším kliknutím na tlačítko můžete volbu zrušit.)</center>"""

distantText = f"""<center>Nyní ze skupin níže vyberte kliknutím na tlačítko {NUMGROUPS} skupin, které jsou Vám nejvzdálenější.
(Dalším kliknutím na tlačítko můžete volbu zrušit.)</center>"""

remainingText = "Zbývá vybrat skupin: {}"

introGroups = """V následující úloze bude Vaším úkolem vybrat z uvedených skupin, které jsou Vám nejbližší a následně ty, které jsou Vám nejvzdálenější."""

################################################################################



class Groups(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = closeText, height = 2, font = 15, width = 80, proceed = True)

        with open(os.path.join(os.getcwd(), "Stuff", "groups.txt"), "r", encoding="utf-8") as file:
            self.groups = [line.strip() for line in file if line.strip()]
        random.shuffle(self.groups)

        columns = 3
        rows = 10

        self.chosen = set()
        self.distant = set()

        ttk.Style().configure("Padded.TButton", padding = (2,2)) 
        
        self.groupFrame = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.buttons = {}
        for i, group in enumerate(self.groups):
            self.buttons[group] = ttk.Button(self.groupFrame, text = group, command = lambda g = group: self.clicked(g), width = 35)
            self.buttons[group].config(style="Padded.TButton")    
            self.buttons[group].grid(row = i // columns, column = i % columns, padx = 10, pady = 10)

        self.remaining = ttk.Label(self, text = remainingText.format(NUMGROUPS), font = "helvetica 15", background = "white")

        self.groupFrame.grid(row = 2, column = 1)
        self.remaining.grid(row = 3, column = 1, sticky = N)
        self.next.grid(row = 4, column = 1)

        self.rowconfigure(0, weight = 2)
        self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 0)
        self.rowconfigure(4, weight = 1)
        self.rowconfigure(5, weight = 2)

        self.next["state"] = "disabled"
        self.next["command"] = self.changeToDistant

        self.close = True

        self.file.write("Groups\n")


    def nextFun(self):
        self.file.write(self.id + "\t" + "_".join(self.chosen) + "\t" + "_".join(self.distant) + "\n\n")
        data = {'id': self.id, 'round': "groups", 'offer': "_".join(self.chosen) + "|" + "_".join(self.distant)}
        if URL != "TEST":
            self.sendData(data)
        super().nextFun()


    def clicked(self, group):
        if group in self.chosen:
            self.buttons[group].config(style="Padded.TButton")        
            self.chosen.remove(group)
        elif group in self.distant:
            self.buttons[group].config(style="Padded.TButton")        
            self.distant.remove(group)           
        else:
            if self.close:
                ttk.Style().configure("Clicked.TButton", background="green", foreground="blue", font=("Helvetica", 15, "underline", "bold"), padding = (2, 1))
                self.buttons[group].config(style="Clicked.TButton")
                self.chosen.add(group)
            else:
                ttk.Style().configure("Distant.TButton", background="red", foreground="red", font=("Helvetica", 15, "underline", "bold"), padding = (2, 1))
                self.buttons[group].config(style="Distant.TButton")
                self.distant.add(group)            
        self.remaining["text"] = remainingText.format(NUMGROUPS - len(self.chosen)) if self.close else remainingText.format(NUMGROUPS - len(self.distant))

        if self.close:
            if NUMGROUPS == len(self.chosen):
                newstate = "disabled" 
                self.next["state"] = "normal"
            else:
                newstate = "normal"
                self.next["state"] = "disabled"
            for group, button in self.buttons.items():            
                if group not in self.chosen:                
                    button["state"] = newstate
        else:
            if NUMGROUPS == len(self.distant):
                newstate = "disabled" 
                self.next["state"] = "normal"
            else:
                newstate = "normal"
                self.next["state"] = "disabled"
            for group, button in self.buttons.items():  
                if group in self.chosen:
                    button["state"] = "disabled"
                elif group not in self.distant:                
                    button["state"] = newstate
        

    def changeToDistant(self):
        self.next["command"] = self.nextFun
        self.next["state"] = "disabled"
        self.close = False
        self.changeText(distantText)
        for group, button in self.buttons.items():            
            if group not in self.chosen:                
                button["state"] = "normal"
            else:
                button["state"] = "disabled"
        self.remaining["text"] = remainingText.format(NUMGROUPS)

        

InstructionsGroups = (InstructionsFrame, {"text": introGroups, "height": 5})



if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([#InstructionsGroups,
         Groups
         ])
