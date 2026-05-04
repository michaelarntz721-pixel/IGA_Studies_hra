from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import perf_counter, sleep
from uuid import uuid4

import random
import os
import urllib.request
import urllib.parse

from common import ExperimentFrame, InstructionsFrame, Measure, MultipleChoice, InstructionsAndUnderstanding, read_all
from gui import GUI
from constants import TESTING, URL, TRUST, SAMENESS, FAVORITISM
from login import Login
from sameness import createSyntetic


################################################################################
# TEXTS
instructionsT0 = """Nyní začíná další úloha.

Vaše rozhodnutí v této úloze budou mít finanční důsledky pro Vás a pro dalšího přítomného účastníka v laboratoři. 

Pozorně si přečtěte pokyny na další obrazovce, abyste porozuměl(a) studii a své roli v ní."""


instructionsT1 = """V rámci této úlohy jste spárován(a) s dalším účastníkem studie. Oba obdržíte {} Kč.

Bude Vám náhodně přidělena jedna ze dvou rolí: budete buď hráčem A, nebo hráčem B.

<i>Hráč A:</i> Má možnost poslat hráči B od 0 do {} Kč (po {} Kč). Poslaná částka se ztrojnásobí a obdrží ji hráč B.
<i>Hráč B:</i> Může poslat zpět hráči A jakékoli množství peněz získaných v této úloze, tedy úvodních {} Kč a ztrojnásobenou částku poslanou hráčem A.

Předem nebudete vědět, jaká je Vaše role a uvedete tedy rozhodnutí pro obě role. Protože nebudete předem vědět, jak by se rozhodl druhý účastník jako hráč A, budete uvádět své volby pro různé možnosti jeho rozhodnutí.

Tuto úlohu budete hrát v rámci studie celkem sedmkrát. Vždy dostanete popis druhého hráče, s kterým hrajete (tj. informaci o tom, jaké skupiny jsou mu blízké a vzdálené). Alespoň jeden popis bude odpovídat skutečnému účastníkovi studie. Zbývající popisy budou uměle vytvořené. Vaše odměna za úlohu bude záviset pouze na Vaší hře v jednom kole úlohy se skutečným účastníkem studie. Ostatní hry Vaší konečnou odměnu nijak neovlivní.

Na konci studie se dozvíte, jaká byla Vaše role a jaký je celkový výsledek rozhodnutí Vás a druhého účastníka.

Pro ověření pochopení úlohy odpovězte na kontrolní otázky níže."""


intstuctionsT2a = "Pro účastníka studie, s kterým jste spárován(a), jsou blízké a vzdálené tyto skupiny:"


instructionsT2 = """On podobně bude vědět, jaké skupiny jsou blízké a vzdálené Vám.

<i>Hráč A:</i> Má možnost poslat hráči B od 0 do {} Kč (po {} Kč). Poslaná částka se ztrojnásobí a obdrží ji hráč B.
<i>Hráč B:</i> Může poslat zpět hráči A jakékoli množství peněz získaných v této úloze, tedy úvodních {} Kč a ztrojnásobenou částku poslanou hráčem A.

Předem nebudete vědět, jaká je Vaše role a uvedete tedy rozhodnutí pro obě role.

Svou volbu učiňte posunutím modrých ukazatelů níže.

{}"""

endA = "<b>Nejprve se rozhodněte, kolik peněz pošlete hráči B, pokud bude náhodně vybráno, že jste hráč A.</b>"
endPrediction = "<b>Nyní uveďte pomocí ukazatele, kolik očekáváte, že Vám pošle zpět hráč B, pokud bude náhodně vybráno, že jste hráč A.</b>"
endB = "<b>Nakonec u všech možností uveďte pomocí ukazatele, kolik pošlete zpět hráči A, pokud bude náhodně vybráno, že jste hráč B.</b>"


trustControl1 = "Jaká je role hráče A a hráče B ve studii?"
trustAnswers1 = ["Hráč A rozhoduje, kolik vezme hráči B peněz a hráč B se rozhoduje, kolik vezme hráči A peněz na oplátku.",
"Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči A\njakékoli množství dostupných peněz zpět.", 
"Hráči A a B se rozhodují, kolik si navzájem pošlou peněz. Transfer peněz mezi nimi je dán rozdílem poslaných peněz.", 
"Hráč A se rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí. Hráč B může vzít hráči A\njakékoli množství peněz, které hráči A zůstaly."]
trustFeedback1 = ["Chybná odpověď. Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči B jakékoli množství dostupných peněz zpět.", 
"Správná odpověď.", "Chybná odpověď. Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči B jakékoli množství dostupných peněz zpět.", 
"Chybná odpověď. Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči B jakékoli množství dostupných peněz zpět."]


trustControl2 = "Jakou odměnu obdrží hráč A, pokud hráči B pošle 40 Kč a ten mu pošle zpět 60 Kč?"
trustAnswers2 = ["40 Kč (100 - 3 × 40 + 60)", "120 Kč (100 - 40 + 60)", "160 Kč (100 + 3 × (60 - 40))", "240 Kč (100 - 40 + 3 × 60)"]
trustFeedback2 = ["Chybná odpověď. Hráč A obdrží 100 Kč, z kterých 40 Kč pošle hráči B, zbyde mu tedy 60 Kč, ke kterým obdrží od hráče B 60 Kč, tj. na konec obdrží 120 Kč (100 - 40 + 60).", "Správná odpověď.", "Chybná odpověď. Hráč A obdrží 100 Kč, z kterých 40 Kč pošle hráči B, zbyde mu tedy 60 Kč, ke kterým obdrží od hráče B 60 Kč, tj. na konec obdrží 120 Kč (100 - 40 + 60).", "Chybná odpověď. Hráč A obdrží 100 Kč, z kterých 40 Kč pošle hráči B, zbyde mu tedy 60 Kč, ke kterým obdrží od hráče B 60 Kč, tj. na konec obdrží 120 Kč (100 - 40 + 60)."]


trustControl3 = "Jakou odměnu obdrží hráč B, pokud hráč A pošle 40 Kč a hráč B mu pošle zpět 60 Kč?"
trustAnswers3 = ["80 Kč (100 + 40 - 60)", "160 Kč (100 + 3 × 40 - 60)", "240 Kč (100 + 3 × 60 - 40)", "280 Kč (100 + 3 × 40 + 60)"]
trustFeedback3 = ["Chybná odpověď. Hráč B obdrží 100 Kč, ke kterým obdrží 120 Kč od hráče A (poslaných 40 Kč se ztrojnásobí) a následně pošle hráči A 60 Kč, tj. na konec obdrží 160 Kč (100 + 3 × 40 - 60).", "Správná odpověď.", "Chybná odpověď. Hráč B obdrží 100 Kč, ke kterým obdrží 120 Kč od hráče A (poslaných 40 Kč se ztrojnásobí) a následně pošle hráči A 60 Kč, tj. na konec obdrží 160 Kč (100 + 3 × 40 - 60).", "Chybná odpověď. Hráč B obdrží 100 Kč, ke kterým obdrží 120 Kč od hráče A (poslaných 40 Kč se ztrojnásobí) a následně pošle hráči A 60 Kč, tj. na konec obdrží 160 Kč (100 + 3 × 40 - 60)."]


trustResultTextA = """V úloze s dělením peněz Vám byla při hře hrané se skutečným účastníkem studie náhodně vybrána role hráče A. Rozhodl(a) jste se poslat {} Kč. Tato částka byla ztrojnásobena na {} Kč. Ze svých {} Kč Vám poslal hráč B {} Kč. V této úloze jste tedy získal(a) {} Kč a hráč B {} Kč."""

trustResultTextB = """V úloze s dělením peněz Vám byla při hře hrané se skutečným účastníkem studie náhodně vybrána role hráče B. Hráč A se rozhodl(a) poslat {} Kč. Tato částka byla ztrojnásobena na {} Kč. Ze svých {} Kč jste poslal(a) hráči B {} Kč. V této úloze jste tedy získal(a) {} Kč a hráč A {} Kč."""

favoritismResultText = "V úkolu, kde Vám ostatní účastníci mohli přidělit nebo sebrat peníze, jste získal(a) {} Kč."
samenessResultTextCorrect = f"Podobnost dalšího účastníka studie jste odhadl(a) správně a získal(a) jste tedy {SAMENESS} Kč."
samenessResultTextIncorrect = f"Podobnost dalšího účastníka studie jste neodhadl(a) správně a nezískal(a) jste tedy za tuto úlohu žádnou odměnu."

checkButtonText3 = "Rozhodl(a) jsem se u všech možností"
checkButtonText2 = "Uvedl(a) jsem svou předpověď"
checkButtonText = "Uvedl(a) jsem své rozhodnutí"


################################################################################


class ScaleFrame(Canvas):
    def __init__(self, root, font = 15, maximum = 0, player = "A", returned = 0, endowment = 100):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.parent = root
        self.root = root.root
        self.rounding = maximum / 5 if player == "A" else 10
        self.player = player
        self.returned = returned
        self.font = font
        self.endowment = endowment
        self.maximum = maximum

        self.valueVar = StringVar()
        self.valueVar.set("0")

        ttk.Style().configure("TScale", background = "white")

        self.value = ttk.Scale(self, orient = HORIZONTAL, from_ = 0, to = maximum, length = 400,
                            variable = self.valueVar, command = self.changedValue)
        self.value.bind("<Button-1>", self.onClick)

        self.playerText1 = "Já:" if player == "A" or player == "prediction" else "Hráč A:"
        self.playerText2 = "Hráč B:" if player == "A" or player == "prediction" else "Já:"
        self.totalText1 = "{0:3d} Kč" if player == "A" else "{0:3d} Kč"
        self.totalText2 = "{0:3d} Kč" if player == "A" else "{0:3d} Kč"

        self.valueLab = ttk.Label(self, textvariable = self.valueVar, font = "helvetica {}".format(font), background = "white", width = 3, anchor = "e")
        self.currencyLab = ttk.Label(self, text = "Kč", font = "helvetica {}".format(font), background = "white", width = 6)

        self.value.grid(column = 1, row = 1, padx = 10)
        self.valueLab.grid(column = 3, row = 1)        
        self.currencyLab.grid(column = 4, row = 1)

        fg = "white" if self.player == "prediction" else "black"

        self.playerLab1 = ttk.Label(self, text = self.playerText1, font = "helvetica {}".format(font), background = "white", width = 6, anchor = "e", foreground = fg) 
        self.playerLab2 = ttk.Label(self, text = self.playerText2, font = "helvetica {}".format(font), background = "white", width = 6, anchor = "e", foreground = fg) 
        self.totalLab1 = ttk.Label(self, text = self.totalText1.format(0), font = "helvetica {}".format(font), background = "white", width = 6, anchor = "e", foreground = fg)
        self.totalLab2 = ttk.Label(self, text = self.totalText2.format(0), font = "helvetica {}".format(font), background = "white", width = 6, anchor = "e", foreground = fg)
        self.spaces = ttk.Label(self, text = " ", font = "helvetica {}".format(font), background = "white", width = 1)

        self.playerLab1.grid(column = 5, row = 1, padx = 3)
        self.totalLab1.grid(column = 6, row = 1, padx = 3, sticky = "ew")
        self.playerLab2.grid(column = 8, row = 1, padx = 3)        
        self.totalLab2.grid(column = 9, row = 1, padx = 3, sticky = "ew")
        self.spaces.grid(column = 7, row = 1)        
        
        self.changedValue(0)


    def showPrediction(self):
        self.playerLab1["foreground"] = "black"
        self.playerLab2["foreground"] = "black"
        self.totalLab1["foreground"] = "black"
        self.totalLab2["foreground"] = "black"
        self.changedValue(0)


    def onClick(self, event):       
        if self.value.instate(["disabled"]):
            return
        click_position = event.x
        newValue = int((click_position / self.value.winfo_width()) * self.value['to'])
        self.changedValue(newValue)
        self.update()


    def changedValue(self, value):           
        value = str(min([max([eval(str(value)), 0]), self.maximum]))
        self.valueVar.set(value)
        newval = int(round(eval(self.valueVar.get())/self.rounding, 0)*self.rounding)
        self.valueVar.set("{0:3d}".format(newval))
        if self.player == "A":
            self.totalLab1["text"] = self.totalText1.format(self.endowment - newval)
            self.totalLab2["text"] = self.totalText2.format(self.endowment + newval * 3)
            self.totalLab1["font"] = "helvetica {} bold".format(self.font)
            self.playerLab1["font"] = "helvetica {} bold".format(self.font)
        elif self.player == "B":
            self.totalLab1["text"] = self.totalText1.format(self.endowment - self.returned + newval)
            self.totalLab2["text"] = self.totalText2.format(self.returned * 3 + self.endowment - newval)
            self.totalLab2["font"] = "helvetica {} bold".format(self.font)
            self.playerLab2["font"] = "helvetica {} bold".format(self.font)
        elif self.player == "prediction":
            self.totalLab1["text"] = self.totalText1.format(self.endowment - (self.maximum - self.endowment) // 3 + newval)
            self.totalLab2["text"] = self.totalText2.format(self.maximum - newval)
            self.totalLab1["font"] = "helvetica {} bold".format(self.font)
            self.playerLab1["font"] = "helvetica {} bold".format(self.font)
        #self.parent.checkAnswers()
              


class GroupsFrame(Canvas):
    def __init__(self, root, close, distant):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.root = root

        self.label = ttk.Label(self, text=intstuctionsT2a, font="helvetica 15 bold", background="white")
        self.label.grid(row = 0, column = 0, columnspan = 2, pady = 10, sticky=W)

        self.closeText = Text(self, wrap=WORD, font="helvetica 15", height=7, width=45, background="white", relief="flat")
        self.closeText.grid(row = 1, column = 0, pady = 10)
        self.closeText.tag_configure("bold", font = "helvetica 15 bold", foreground = "blue")
        self.closeText.insert("1.0", "\n".join(["Blízké skupiny:"] + close))
        self.closeText.tag_add("bold", "1.0", "2.0")
        self.closeText.config(state=DISABLED)

        self.distantText = Text(self, wrap=WORD, font="helvetica 15", height=7, width=45, background="white", relief="flat")
        self.distantText.grid(row = 1, column = 1, pady = 10)
        self.distantText.tag_configure("bold", font = "helvetica 15 bold", foreground = "red")
        self.distantText.insert("1.0", "\n".join(["Vzdálené skupiny:"] + distant))
        self.distantText.tag_add("bold", "1.0", "2.0")
        self.distantText.config(state=DISABLED)



class Trust(InstructionsFrame):
    def __init__(self, root):

        if not "trustblock" in root.status:
            root.status["trustblock"] = 1
            self.groups = {}                
            self.groups["real1"] = root.status["groups"][4]
            proenvi = random.randint(-8,-7)
            proenvi2 = random.randint(-5,-4)
            neutral = random.choice([-2, -1, 1, 2])            
            antienvi = random.randint(7,8)
            antienvi2 = random.randint(4,5)
            self.groups["proenvi"] = createSyntetic(proenvi, "string")
            self.groups["proenvi2"] = createSyntetic(proenvi2, "string")
            self.groups["neutral"] = createSyntetic(neutral, "string")
            self.groups["antienvi"] = createSyntetic(antienvi, "string")
            self.groups["antienvi2"] = createSyntetic(antienvi2, "string")
            if len(root.status["groups"]) == 6:                
                self.groups["real2"] = root.status["groups"][5]
            else:                
                neutral2 = random.choice([-2, -1, 1, 2])                
                self.groups["neutral2"] = createSyntetic(neutral2, "string")                        
            keys = list(self.groups.keys())
            random.shuffle(keys)
            root.status["trust_groups_order"] = keys
            root.status["trust_groups"] = {key: self.groups[key] for key in keys}         
        else:
            root.status["trustblock"] += 1

        endowment = TRUST    
        
        text = instructionsT2.format(endowment, int(endowment/5), endowment, endA)

        height = 13
        width = 90

        super().__init__(root, text = text, height = height, font = 15, width = width)
        
        self.person = self.root.status["trust_groups_order"][self.root.status["trustblock"] - 1]
        close, distant = self.root.status["trust_groups"][self.person].split("|")       

        self.groupFrame = GroupsFrame(self, close.split("_"), distant.split("_"))

        self.labA = ttk.Label(self, text = "Pokud budu hráč A", font = "helvetica 15 bold", background = "white")
        self.labA.grid(column = 0, row = 2, columnspan = 3, pady = 10)        

        # ta x-pozice tady je hnusny hack, idealne by se daly texty odmen vsechny sem ze slideru
        self.labR = ttk.Label(self, text = "Rozdělení odměn po tomto kroku", font = "helvetica 15 bold", background = "white", anchor = "center", width = 30)
        self.labR.grid(column = 1, row = 2, pady = 5, sticky = E)

        self.labX = ttk.Label(self, text = "Finální rozdělení odměn", font = "helvetica 15 bold", background = "white", anchor = "center", width = 28)
        self.labX.grid(column = 1, row = 6, pady = 5, sticky = E)

        self.frames = {}
        for i in range(8):            
            if i < 6:
                text = "Pokud hráč A pošle {} Kč, pošlu hráči A zpět:".format(int(i*endowment/5))
                ttk.Label(self, text = text, font = "helvetica 15", background = "white").grid(column = 0, row = 7 + i, pady = 1, sticky = E)
                player = "B"
            elif i == 6:
                ttk.Label(self, text = "Pošlu hráči B:", font = "helvetica 15", background = "white").grid(column = 0, row = 3, pady = 1, sticky = E)            
                player = "A"
            else:
                ttk.Label(self, text = "Očekávám, že hráč B pošle zpět:", font = "helvetica 15", background = "white").grid(column = 0, row = 4, pady = 1, sticky = E)  
                player = "prediction"
            maximum = int(i * 3 * endowment / 5 + endowment) if i < 6 else endowment            
            self.frames[i] = ScaleFrame(self, maximum = maximum, player = player, returned = int(i*endowment/5), endowment = endowment)
            row = 7 + i if i < 6 else i - 3
            self.frames[i].grid(column = 1, row = row, pady = 1)
            if i != 6:
                self.frames[i].value["state"] = "disabled"
        
        self.labB = ttk.Label(self, text = "Pokud budu hráč B", font = "helvetica 15 bold", background = "white")
        self.labB.grid(column = 0, row = 6, columnspan = 3, pady = 10)

        self.checkVar = BooleanVar()
        ttk.Style().configure("TCheckbutton", background = "white", font = "helvetica 15")
        self.checkBut = ttk.Checkbutton(self, text = checkButtonText, command = self.checkbuttoned, variable = self.checkVar, onvalue = True, offvalue = False)
        self.checkBut.grid(row = 19, column = 0, columnspan = 3, pady = 10)

        self.next.grid(column = 0, row = 20, columnspan = 3, pady = 5, sticky = N)            
        self.next["state"] = "disabled"
        
        self.groupFrame.grid(row = 0, column = 0, columnspan = 3, pady = 5, sticky = S)
        self.text.grid(row = 1, column = 0, columnspan = 3)

        self.trialLabel = ttk.Label(self, text = "Hra {}/7".format(self.root.status["trustblock"]), font = "helvetica 15", background = "white")
        self.trialLabel.grid(row = 0, column = 1, columnspan = 3, pady = 15, padx = 20, sticky = NE)

        self.status = "A"

        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 0)
        self.rowconfigure(2, weight = 0)
        self.rowconfigure(3, weight = 0)
        self.rowconfigure(4, weight = 1)
        self.rowconfigure(18, weight = 2)
        self.rowconfigure(20, weight = 2)

        self.columnconfigure(0, weight = 2)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(3, weight = 2)

    def checkbuttoned(self):
        self.next["state"] = "normal" if self.checkVar.get() else "disabled"
      
    def nextFun(self):
        if self.status == "A":
            for i, frame in self.frames.items():
                if i != 7:
                    frame.value["state"] = "normal" if not self.checkVar.get() else "disabled"
                else:
                    frame.value["state"] = "normal" if self.checkVar.get() else "disabled"
                    frame.maximum = TRUST + int(self.frames[6].valueVar.get()) * 3
                    frame.value["to"] = frame.maximum
                    frame.showPrediction()
            self.status = "prediction"
            self.checkBut["text"] = checkButtonText2
            self.next["state"] = "disabled"
            self.checkVar.set(False)
            self.changeText(instructionsT2.format(TRUST, int(TRUST/5), TRUST, endPrediction))
        elif self.status == "prediction":
            for i, frame in self.frames.items():
                if i > 5:
                    frame.value["state"] = "disabled"
                else:
                    frame.value["state"] = "normal"
            self.status = "B"
            self.checkBut["text"] = checkButtonText3
            self.next["state"] = "disabled"
            self.checkVar.set(False)
            self.changeText(instructionsT2.format(TRUST, int(TRUST/5), TRUST, endB))
        else:
            self.send()
            self.write()
            super().nextFun()

    def send(self):        
        key = self.root.status["trust_groups_order"][self.root.status["trustblock"] - 1]
        if not key.startswith("real"):
            return
        num_id = key.lstrip("real")
        pair = self.root.status["trust_pairs"][int(num_id) - 1]
        self.responses = [self.frames[i].valueVar.get().strip() for i in range(7)]        
        data = {'id': self.id, 'round': "trust" + str(pair), 'offer': "_".join(self.responses[:7])}
        self.sendData(data)

    def write(self):
        block = self.root.status["trustblock"]
        self.file.write("Trust\n")                
        key = self.root.status["trust_groups_order"][block - 1]
        d = [self.id, str(block), key, self.root.status["trust_groups"][key]]        
        self.responses = [self.frames[i].valueVar.get().strip() for i in range(8)]  
        self.file.write("\t".join(map(str, d + self.responses)))
        if URL == "TEST" and self.person == "real1":
            if self.root.status["trust_roles"][0] == "A":                        
                self.root.status["trustTestSentA"] = int(self.frames[6].valueVar.get())
            else:
                self.root.status["trustTestSentB"] = [int(self.frames[i].valueVar.get()) for i in range(6)]       
        self.file.write("\n\n")




class Wait(InstructionsFrame):
    def __init__(self, root, what):
        super().__init__(root, text = "Čekejte na data od ostatních účastníků studie", height = 3, font = 15, proceed = False, width = 45)
        self.progressBar = ttk.Progressbar(self, orient = HORIZONTAL, length = 400, mode = 'indeterminate')
        self.progressBar.grid(row = 2, column = 1, sticky = N)

        self.what = what

    def checkUpdate(self):
        t0 = perf_counter() - 4
        while True:
            self.update()
            if perf_counter() - t0 > 5:
                t0 = perf_counter()
                
                if URL == "TEST":                    
                    if self.what == "groups":
                        persons = []
                        ids = []
                        for i in range(5):
                            value = random.randint(-9, 9)                            
                            persons.append(createSyntetic(value, "string"))                            
                            part_id = str(uuid4())
                            part_id = "test" + str(value + 20) + part_id[6:]
                            ids.append(part_id)
                        response = "_".join(ids) + "!" + "~".join(persons)
                    elif self.what == "articles":
                        types = random.choices(["envi", "filler", "anti"], k = 3)
                        nums = random.sample(range(1, 16), 3)
                        articles = [f"{types[i]}{nums[i]}" for i in range(3)]                                                
                        response = "_".join(articles)
                    elif self.what == "results":                                        
                        # trustgame
                        if self.root.status["trust_roles"][0] == "A":                        
                            sentA = self.root.status["trustTestSentA"]
                            sentB = random.randint(0, int((sentA * 3 + TRUST) / 10)) * 10
                        else:
                            chose = random.randint(0,5)
                            sentA = int(chose * 2 * TRUST / 10)
                            sentB = self.root.status["trustTestSentB"][chose]
                        # favoritism
                        favoritism = random.randint(0, 6) * FAVORITISM                                             
                        # sameness
                        sameness = random.randint(17, 20)

                        response = "_".join(map(str, [self.root.status["trust_pairs"][0], sentA, sentB, favoritism, sameness]))
                else:
                    try:
                        data = urllib.parse.urlencode({'id': self.id, 'round': "wait", 'offer': self.what})                
                        data = data.encode('ascii')                
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8")     
                            if URL == "http://127.0.0.1:8000/":
                                print(response)  
                    except Exception as e:
                        continue

                if response:               
                    if self.what == "groups":
                        ids, persons = response.split("!")
                        self.root.status["paired_ids"] = ids.split("_")
                        self.root.status["groups"] = persons.split("~")
                    elif self.what == "articles":
                        self.root.status["othersArticles"] = response.split("_")                        
                    elif self.what == "results":
                        # trustgame
                        pair, sentA, sentB, favoritism, sameness = response.split("_")
                        sentA, sentB = int(sentA), int(sentB)

                        if self.root.status["trust_roles"][0] == "A": 
                            reward = TRUST - sentA + sentB
                            text = trustResultTextA.format(sentA, sentA*3, TRUST + sentA*3, sentB, TRUST - sentA + sentB, TRUST + sentA*3 - sentB)
                        else:
                            text = trustResultTextB.format(sentA, sentA*3, TRUST + sentA*3, sentB, TRUST + sentA*3 - sentB, TRUST - sentA + sentB)
                            reward = TRUST + sentA*3 - sentB                        

                        self.root.status["results"] += [text]
                        self.root.status["reward"] += reward

                        # favoritism
                        self.root.status["results"] += [favoritismResultText.format(favoritism)]
                        self.root.status["reward"] += int(favoritism)

                        # sameness
                        if self.root.status["sameness_prediction"] == sameness:
                            text = samenessResultTextCorrect
                            self.root.status["reward"] += SAMENESS
                        else:
                            text = samenessResultTextIncorrect
                        self.root.status["results"] += [text]

                    self.write(response)
                    self.progressBar.stop()
                    self.nextFun()  
                    return

    def run(self):
        self.progressBar.start()
        self.checkUpdate()

    def write(self, response):        
        self.file.write(self.what.capitalize() + " Results" + "\n")
        self.file.write(self.id + "\t" + response.replace("_", "\t") + "\n\n") 



WaitGroups = (Wait, {"what": "groups"})
WaitResults = (Wait, {"what": "results"})
WaitArticles = (Wait, {"what": "articles"})


controlTexts = [[trustControl1, trustAnswers1, trustFeedback1], [trustControl2, trustAnswers2, trustFeedback2], [trustControl3, trustAnswers3, trustFeedback3]]
IntroTrust = (InstructionsFrame, {"text": instructionsT0, "height": 6, "width": 80, "font": 15})
InstructionsTrust = (InstructionsAndUnderstanding, {"text": instructionsT1.format(TRUST, TRUST, int(TRUST/5), TRUST) + "\n\n", "height": 22, "width": 100, "name": "Trust Control Questions", "randomize": False, "controlTexts": controlTexts, "fillerheight": 300, "finalButton": "Pokračovat k volbě"})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    from intros import Ending
    GUI([Login,    
         WaitGroups,
         #IntroTrust,
         #InstructionsTrust,
         Trust, Trust, Trust, Trust, Trust, Trust, Trust,
         WaitResults,
         Ending
         ])