#! python3
# -*- coding: utf-8 -*- 

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import perf_counter, sleep
from collections import defaultdict

import random
import os
import urllib.request
import urllib.parse

from common import InstructionsFrame
from gui import GUI
from constants import TESTING, URL






class Login(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = "Počkejte na spuštění experimentu", height = 3, font = 15, width = 45, proceed = False)

        self.progressBar = ttk.Progressbar(self, orient = HORIZONTAL, length = 400, mode = 'indeterminate')
        self.progressBar.grid(row = 2, column = 1, sticky = N)

    def login(self):       
        count = 0
        while True:
            self.update()
            if count % 50 == 0:            
                data = urllib.parse.urlencode({'id': self.root.id, 'round': self.root.status["code"], 'offer': "login"})
                data = data.encode('ascii')
                if URL == "TEST":                                                       
                    bag = str(random.randint(1, 10)) if random.random() < 0.4 else "-1"
                    if random.random() < 0.5:
                        trustRoles = random.choice(["A", "B"]) + "X"
                        trustPairs = str(random.randint(1, 10)) + "_-1" 
                    else:
                        trustRoles = random.choice(["A", "B"]) + random.choice(["A", "B"])
                        trustPairs = "_".join([str(random.randint(1, 10)) for i in range(2)])
                    response = "|".join(["start", bag, trustPairs, trustRoles]) 
                else:
                    response = ""
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8") 
                    except Exception:
                        self.changeText("Server nedostupný")
                if "start" in response:
                    info, bag, trustPairs, trustRoles = response.split("|")              
                    self.root.status["bag"] = bag
                    self.root.status["trust_roles"] = list(trustRoles)
                    self.root.status["trust_pairs"] = trustPairs.split("_")         
                    self.progressBar.stop()
                    self.write(response)
                    self.nextFun()                      
                    break
                elif response == "login_successful" or response == "already_logged":
                    self.changeText("Přihlášen")
                    self.root.status["logged"] = True
                elif response == "ongoing":
                    self.changeText("Do studie se již nelze připojit")
                elif response == "no_open":
                    self.changeText("Studie není otevřena")
                elif response == "closed":
                    self.changeText("Studie je uzavřena pro přihlašování")
                elif response == "not_grouped":
                    self.changeText("V experimentu nezbylo místo. Zavolejte prosím experimentátora zvednutím ruky.")
            count += 1                  
            sleep(0.1)        

    def run(self):
        self.progressBar.start()
        self.login()  

    def write(self, response):
        self.file.write("Login" + "\n")
        self.file.write(self.id + "\t" + self.root.status["code"] + " \t" + response.replace("|", "\t").lstrip("start") + "\n\n")        

    def gothrough(self):
        self.run()