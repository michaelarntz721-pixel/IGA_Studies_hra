#! python3
from tkinter import *
from tkinter import ttk

import os
import urllib.request
import urllib.parse

from math import ceil
from time import sleep

from common import InstructionsFrame
from gui import GUI

from constants import PARTICIPATION_FEE, URL
from login import Login


################################################################################
# TEXTS
intro = """Studie se skládá z několika různých úkolů a otázek. Níže je uveden přehled toho, co Vás čeká:

<b>1) Skupiny:</b> Budete uvádět, jaké skupiny jsou Vám blízké a jaké vzdálené.
<b>2) Preference:</b> Budete uvádět, jaká možnost z dvojice se Vám více líbí.
<b>3) Články:</b> Budete vybírat články pro přečtení.
<b>4) Dělení peněz:</b> Budete se rozhodovat, jak dělit peníze v páru s jiným účastníkem studie.
<b>5) Přidělování peněz:</b> Budete rozdělovat peníze mezi další účastníky studie. V tomto úkolu můžete od ostatních účastníků získat peníze.
<b>6) Podobnost:</b> Budete hodnotit, nakolik jsou Vám další účastníci studie podobní. V tomto úkolu můžete také získat peníze.
<b>7) Výběr výrobků:</b> Budete si vybírat výrobky, které budete moct získat.
<b>8) Čtení článků:</b> Budete mít čas si dříve vybrané články přečíst.
<b>9) Příspěvek charitě:</b> Budete se rozhodovat, zda přispějete na charitu, pokud získáte peníze v loterii.
<b>10) Loterie:</b> Můžete se rozhodnout zúčastnit se další loterie a získat peníze v závislosti na výsledcích této loterie.
<b>11) Konec studie a platba:</b> Poté, co skončíte, půjdete do vedlejší místnosti, kde podepíšete pokladní doklad, na základě kterého obdržíte vydělané peníze v hotovosti. Jelikož v dokumentu bude uvedena pouze celková suma, experimentátor, který Vám bude vyplácet odměnu, nebude vědět, kolik jste vydělali v jednotlivých částech studie.

Veškeré interakce s ostatními účastniky studie proběhnou pouze přes počítač a anonymně. Nikdy nebudete navzájem vědět, s kým v rámci experimentu interagujete.

Všechny informace, které v průběhu studie uvidíte, jsou pravdivé a nebudete za žádných okolností klamáni.

V případě, že máte otázky nebo narazíte na technický problém během úkolů, zvedněte ruku a tiše vyčkejte příchodu výzkumného asistenta.
"""


ending = """Toto je konec experimentu.
{}
Za účast na studii dostáváte {} Kč.

<b>Vaše odměna za tuto studii je tedy dohromady {} Kč, zaokrouhleno na desítky korun nahoru získáváte {} Kč. Napište prosím tuto (zaokrouhlenou) částku do příjmového dokladu na stole před Vámi.</b>

Výsledky studie založené na datech získaných v tomto experimentu budou volně dostupné na stránkách Decision Lab Prague (decisionlab.vse.cz) krátce po vyhodnocení dat a publikaci výsledků. 

<b>Žádáme Vás, abyste nesděloval(a) detaily této studie možným účastníkům, aby jejich volby a odpovědi nebyly ovlivněny a znehodnoceny.</b>
  
Můžete si vzít všechny svoje věci a vyplněný příjmový doklad, a aniž byste rušil(a) ostatní účastníky, odeberte se do vedlejší místnosti za výzkumným asistentem, od kterého obdržíte svoji odměnu. 

Děkujeme za Vaši účast!
 
Decision Lab Prague při FPH VŠE""" 


login = """Vítejte na výzkumné studii pořádané Fakultou podnikohospodářskou Vysoké školy ekonomické v Praze ve spolupráci s Univerzitou Karlovou! 

Za účast na studii obdržíte {} Kč. Kromě toho můžete vydělat další peníze v průběhu studie. 

Studie bude trvat cca 50-70 minut.

Do textového pole níže zadejte Váš kód, který jste obdržel(a) mailem a uvedl(a) v rámci dotazníkového šetření. 

Pokud kód neznáte, nebo pokud máte jakékoliv dotazy, zvedněte ruku a tiše vyčkejte příchodu výzkumného asistenta.

Děkujeme, že jste vypnul(a) svůj mobilní telefon, a že nebudete s nikým komunikovat v průběhu studie. Pokud s někým budete komunikovat nebo pokud budete nějakým jiným způsobem narušovat průběh studie, budete požádán(a), abyste opustil(a) laboratoř, bez nároku na vyplacení peněz.

Přečtěte si prosím informovaný souhlas a pokud s ním budete souhlasit, podepište ho. 

Pro přihlášení ke studii klikněte na tlačítko pokračovat.""".format(PARTICIPATION_FEE)



################################################################################





class Ending(InstructionsFrame):
    def __init__(self, root):
        root.texts["results"] = "\n" + "\n\n".join(root.status["results"]) + "\n"

        root.texts["reward"] = str(root.status["reward"])
        root.texts["rounded_reward"] = ceil(root.status["reward"] / 10) * 10
        root.texts["participation_fee"] = PARTICIPATION_FEE
        updates = ["results", "participation_fee", "reward", "rounded_reward"]
        super().__init__(root, text = ending, keys = ["g", "G"], proceed = False, height = 38, update = updates, width = 100)
        self.file.write("Ending\n")
        self.file.write(self.id + "\t" + str(root.texts["rounded_reward"]) + "\n\n")

    def run(self):
        self.sendInfo()

    def sendInfo(self):
        while True:
            self.update()    
            data = urllib.parse.urlencode({'id': self.root.id, 'round': -99, 'offer': self.root.texts["rounded_reward"]})
            data = data.encode('ascii')
            if URL == "TEST":
                response = "ok"
            else:
                try:
                    with urllib.request.urlopen(URL, data = data) as f:
                        response = f.read().decode("utf-8") 
                except Exception:
                    pass
            if "ok" in response:                     
                break              
            sleep(5)




class Initial(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = login, proceed = True, height = 21)
        self.codeFrame = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")
        self.codeFrame.grid(row = 2, column = 1, sticky = EW)

        self.codeFrame.columnconfigure(0, weight = 1)
        self.codeFrame.columnconfigure(3, weight = 1)

        self.next.grid(row = 3, column = 1)
        self.next["state"] = "disabled"

        self.codeVar = StringVar()

        self.codeVar.trace_add("write", lambda *args: self.enable(self.codeVar.get()))
        self.codeEntry = ttk.Entry(self.codeFrame, width = 8, font = "Helvetica 15", textvariable = self.codeVar)
        self.codeEntry.grid(row = 0, column = 2, padx = 10)

        self.filler = ttk.Label(self.codeFrame, text = "\n\n\n\n\n", font = "Helvetica 15", background = "white")
        self.filler.grid(row = 1, column = 0, columnspan = 1, sticky = W)

        self.codeLabel = ttk.Label(self.codeFrame, text = "Kód:", font = "Helvetica 15", background = "white") 
        self.codeLabel.grid(row = 0, column = 1)

        self.problemLabel = ttk.Label(self.codeFrame, text = "", font = "Helvetica 15", background = "white", foreground = "red", wraplength = 750)
        self.problemLabel.grid(row = 1, column = 0, columnspan = 4, pady = 10)

        self.codeFrame.rowconfigure(1, weight = 1)

        self.rowconfigure(2, weight = 2)
        self.rowconfigure(4, weight = 2)


    def nextFun(self):
        self.next["state"] = "disabled"
        count = 0
        while True:
            self.update()
            if count % 50 == 0:            
                data = urllib.parse.urlencode({'id': self.root.id, 'round': self.codeVar.get(), 'offer': "code"})
                data = data.encode('ascii')
                if URL == "TEST":                    
                    response = "validated"
                else:
                    response = ""
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8") 
                    except Exception:
                        self.problemLabel["text"] = "Server nedostupný. Přivolejte výzkumného asistenta zvednutím ruky."
                        self.next["state"] = "normal"                        
                        return
                if response == "validated":
                    self.root.status["code"] = self.codeVar.get()                    
                    super().nextFun()                      
                    return
                elif response == "not_found":
                    self.problemLabel["text"] = "Kód nebyl nalezen. Zkontrolujte prosím, zda jste zadali správný kód."
                    self.next["state"] = "normal"
                    return
                elif response == "too_soon":
                    self.problemLabel["text"] = "Dotazník jste nevyplnil(a) před alespoň 5 dny. Dnes se experimentu nemůžete zúčastnit. Přivolejte výzkumného asistenta zvednutím ruky. Můžete se přihlasit na jiný termín."                
                    self.codeEntry["state"] = "disabled"
                    return
                elif response == "participated":
                    self.problemLabel["text"] = "Experimentu jste se již zúčastnil(a). Není možné se zúčastnit znovu. Přivolejte výzkumného asistenta zvednutím ruky."                
                    self.codeEntry["state"] = "disabled"
                    return
                elif response == "opened":
                    self.problemLabel["text"] = "Experiment s tímto kóden je již otevřený. Přivolejte výzkumného asistenta zvednutím ruky."
                    return
                elif response == "no_questionnaire":
                    self.problemLabel["text"] = "Před účastí na experimentu je potřeba vyplnit alespoň 5 dní předem dotazník, na který se dostanete pomocí odkazu, který Vám přišel s pozvánkou mailem. Dnes se experimentu tedy nemůžete zúčastnit. Přivolejte výzkumného asistenta zvednutím ruky. Můžete se přihlasit na jiný termín 5 dní po vyplnění dotazníku."                
                    self.codeEntry["state"] = "disabled"
                    return                  
                elif response == "already_logged":
                    self.problemLabel["text"] = "Jste již přihlášen(a) do experimentu. Přivolejte výzkumného asistenta zvednutím ruky."                
                    self.codeEntry["state"] = "disabled"
                    return
            count += 1                  
            sleep(0.1)   

        
    def enable(self, value):
        if not value.isalnum():
            self.problemLabel["text"] = "Kód může obsahovat pouze písmena a číslice"
            self.next["state"] = "disabled"
            return
        elif self.problemLabel["text"] == "Kód může obsahovat pouze písmena a číslice":
            self.problemLabel["text"] = ""

        if len(value) == 6:
            self.next["state"] = "normal"
            if self.problemLabel["text"] == "Kód může mít maximálně 6 znaků":
                self.problemLabel["text"] = ""
        elif len(value) > 6:
            self.problemLabel["text"] = "Kód může mít maximálně 6 znaků"
            self.next["state"] = "disabled"

            




Intro = (InstructionsFrame, {"text": intro, "proceed": True, "height": 32})
#Initial = (InstructionsFrame, {"text": login, "proceed": False, "height": 19, "keys": ["g", "G"]})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Initial, 
         Login,
         Intro,
         Ending])
