from tkinter import *
from tkinter import ttk
from time import time, sleep

import os
import sys
import random
import urllib.request
import urllib.parse

from constants import TESTING, URL


class ExperimentFrame(Canvas):
    def __init__(self, root):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")
        
        self.root = root
        self.file = self.root.file
        self.id = self.root.id

    def nextFun(self):
        if self.check():
            self.write()
            self.file.write("\n")
            self.destroy()
            self.root.nextFrame()
        else:
            self.back()

    def check(self):
        return True

    def back(self):
        pass

    def write(self):
        pass

    def gothrough(self):        
        self.nextFun()

    def sendData(self, message, pause = 0.1, trials = -1): 
        if URL == "http://127.0.0.1:8000/":
            print(message)
        count = 0           
        while trials != count:
            count += 1
            data = urllib.parse.urlencode(message)
            data = data.encode('ascii')
            if URL == "TEST":
                response = "ok"
            else:
                try:
                    with urllib.request.urlopen(URL, data = data) as f:
                        response = f.read().decode("utf-8")       
                        if URL == "http://127.0.0.1:8000/":
                            print(response)
                except Exception:
                    continue
            if response == "ok":                    
                return            
            sleep(pause)               
        return





class InstructionsFrame(ExperimentFrame):
    def __init__(self, root, text, proceed = True, firstLine = None, end = False, height = 12,
                 font = 15, space = False, width = 80, keys = None, update = None, bold = None, wait = 2, savedata = False):
        super().__init__(root)

        self.root = root
        self.wait = wait
        self.t0 = time()
        self.savedata = savedata

        if update:
            updateTexts = []
            for i in update:
                updateTexts.append(self.root.texts[i])
            text = text.format(*updateTexts)       
                   
        self.text = Text(self, font = "helvetica {}".format(font), relief = "flat",
                         background = "white", width = width, height = height, wrap = "word",
                         highlightbackground = "white")
        self.text.grid(row = 1, column = 0, columnspan = 3)
        if firstLine:
            self.text.insert("1.0", text[:text.find("\n", 5)], firstLine)
            self.text.insert("end", text[text.find("\n", 5):])
            self.text.tag_configure(firstLine, font = "helvetica 20 {}".format(firstLine))
        else:
            self.text.insert("1.0", text)
 
        self.text.tag_configure("bold", font = "helvetica {} bold".format(font))
        self.text.tag_configure("italic", font = "helvetica {} italic".format(font))    
        self.text.tag_configure("courier", font = "courier {}".format(font))      
        self.text.tag_configure("center", justify="center")               
        self.text.tag_configure("blue", foreground = "blue")
        self.text.tag_configure("red", foreground = "red")
        self.text.tag_configure("green", foreground = "green")

        self.addStandardTags()

        self.text.config(state = "disabled")

        if proceed:
            ttk.Style().configure("TButton", font = "helvetica 15")
            self.next = ttk.Button(self, text = "Pokračovat", command = self.nextFun)
            self.next.grid(row = 2, column = 1)
        elif space:
            self.root.bind("<space>", lambda e: self.proceed())
        elif keys:
            for key in keys:
                if key in [str(i) for i in range(10)]:
                    self.root.bind("{}".format(key), lambda e: self.proceed())
                else:
                    self.root.bind("<{}>".format(key), lambda e: self.proceed())                
        self.keys = keys

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 3)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(2, weight = 3)
        self.rowconfigure(3, weight = 3)

    def addStandardTags(self):
        self.addtags("<b>", "</b>", "bold")
        self.addtags("<i>", "</i>", "italic")
        self.addtags("<c>", "</c>", "courier")
        self.addtags("<center>", "</center>", "center")
        self.addtags("<blue>", "</blue>", "blue")
        self.addtags("<red>", "</red>", "red")  
        self.addtags("<green>", "</green>", "green")

    def addtags(self, starttag, endtag, tag):            
        i_index = "1.0"
        while True:
            i_index = self.text.search(starttag, i_index)
            if not i_index:
                break
            e_index = self.text.search(endtag, i_index)
            self.text.tag_add(tag, i_index, e_index)
            self.text.delete(e_index, e_index + "+{}c".format(len(endtag)))
            self.text.delete(i_index, i_index + "+{}c".format(len(starttag)))
            i_index = e_index

    def changeText(self, newtext, tags = True):
        self.text.config(state = "normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", newtext)
        if tags:
            self.addStandardTags()
        self.text.config(state = "disabled")

    def proceed(self):
        if time() - self.t0 > self.wait:
            self.nextFun()

    def nextFun(self):        
        if self.check():
            self.root.unbind("<space>")
            if self.keys:
                for key in self.keys:
                    if key in [str(i) for i in range(10)]:
                        self.root.unbind("{}".format(key))
                    else:
                        self.root.unbind("<{}>".format(key))
            if self.savedata:
                self.write()
            self.destroy()
            self.root.nextFrame()
        else:
            self.back()



class Question(Canvas):
    def __init__(self, root, text, conditional = None, condtype = None, condtext = "", width = 80,
                 label = True, answer = "yesno", condition = "yes", where = "below"):
        super().__init__(root)
        self["background"] = "white"
        self["highlightbackground"] = "white"
        self["highlightcolor"] = "white"

        self.root = root

        self.yesno = answer == "yesno"
        self.condition = condition

        self.answer = StringVar()
        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 13")

        if label:
            self.label = ttk.Label(self, text = text, background = "white", font = "helvetica 15",
                                   width = width)
        else:
            self.label = Text(self, width = width, wrap = "word", font = "helvetica 15",
                              relief = "flat", height = 5, cursor = "arrow",
                              selectbackground = "white", selectforeground = "black")
            self.label.insert("1.0", text)
            self.label.config(state = "disabled")

        if answer == "yesno":
            self.yes = ttk.Radiobutton(self, text = "Ano", variable = self.answer, value = "yes",
                                       command = self.answered)
            self.no = ttk.Radiobutton(self, text = "Ne", variable = self.answer, value = "no",
                                       command = self.answered)
            self.yes.grid(column = 0, row = 1, sticky = "w", padx = 5)
            self.no.grid(column = 0, row = 2, sticky = "w", padx = 5)
        else:
            self.field = answer[0](self, textvariable = self.answer, **answer[1])
            if where == "below":
                self.field.grid(column = 0, row = 1, sticky = "w", padx = 5)
            elif where == "next":
                self.field.grid(column = 5, row = 0, sticky = "w", padx = 5)

        self.condtype = condtype
        if conditional:
            self.condvar = StringVar()
            if condtype in ("combo", "entry"):
                self.cond = conditional[0](self, textvariable = self.condvar, **conditional[1])
            else:
                self.cond = conditional[0](self, variable = self.condvar, **conditional[1])
            if condtype == "combo":
                self.cond.config(state = "readonly")
            self.cond.grid(column = 2, row = 1, sticky = "w")
            self.condtext = ttk.Label(self, text = condtext, background = "white",
                                      font = "helvetica 13")
            self.condtext.grid(column = 1, row = 1, sticky = "w", padx = 20)
            self.condtext.grid_forget()
            self.cond.grid_forget()
                        
        self.label.grid(column = 0, row = 0, columnspan = 4, sticky = "w", pady = 10)

        self.columnconfigure(3, weight = 1)


    def answered(self):
        if self.condtype:
            if self.answer.get() == self.condition:
                row = 1 if self.condition == "yes" else 2
                self.condtext.grid(column = 1, row = row, sticky = "w", padx = 20)
                self.cond.grid(column = 2, row = row, sticky = "w")
            else:
                self.condtext.grid_forget()
                self.cond.grid_forget()

    def check(self):
        return self.answer.get() and (not self.condtype or self.condvar.get()
                                      or self.answer.get() != self.condition)

    def write(self, newline = True):
        self.root.file.write(self.answer.get())
        if self.condtype and self.condvar.get():
            self.root.file.write("\t" + self.condvar.get())
        if newline:
            self.root.file.write("\n")

    def disable(self):
        if self.yesno: 
            self.yes.config(state = "disabled")
            self.no.config(state = "disabled")
        else:
            self.field.config(state = "disabled")
        if self.condtype:
            self.cond.config(state = "disabled")


class TextArea(Canvas):
    def __init__(self, root, text, width = 80, qlines = 2, alines = 5):
        super().__init__(root)
        self["background"] = "white"
        self["highlightbackground"] = "white"
        self["highlightcolor"] = "white"

        self.root = root

        self.answer = StringVar()

        self.label = Text(self, width = width, wrap = "word", font = "helvetica 15",
                          relief = "flat", height = qlines, cursor = "arrow",
                          selectbackground = "white", selectforeground = "black")
        self.label.insert("1.0", text)
        self.label.config(state = "disabled")
        self.label.grid(column = 0, row = 0)

        self.field = Text(self, width = int(width*1.2), wrap = "word", font = "helvetica 15",
                          height = alines, relief = "solid")
        self.field.grid(column = 0, row = 1, pady = 6)

        self.columnconfigure(0, weight = 1)


    def check(self):
        return self.field.get("1.0", "end").strip()

    def write(self, newline = True):
        self.root.file.write(self.field.get("1.0", "end").replace("\n", "  ").replace("\t", " "))
        if newline:
            self.root.file.write("\n")

    def disable(self):
        self.field.config(state = "disabled")


class Measure(Canvas):
    def __init__(self, root, text, values, left, right, shortText = "", function = None,
                 questionPosition = "next", labelPosition = "above", middle = "",
                 funconce = False, filler = 0):
        super().__init__(root)

        self.root = root
        self.text = shortText
        self.answer = StringVar()
        self["background"] = "white"
        self["highlightbackground"] = "white"
        self["highlightcolor"] = "white"

        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 14")

        if text:        
            if questionPosition == "next":
                self.question = ttk.Label(self, text = text, background = "white", anchor = "e", font = "helvetica 14")
                self.question.grid(column = 0, row = 2, sticky = E, padx = 5)
            elif questionPosition == "above":
                self.question = ttk.Label(self, text = text, background = "white", anchor = "center",
                                          font = "helvetica 14")
                self.question.grid(column = 0, row = 0, columnspan = 4, pady = 5)

        if labelPosition != "none":
            self.left = ttk.Label(self, text = "{:>15}".format(left), background = "white",
                                  font = "helvetica 14")
            self.right = ttk.Label(self, text = "{:<15}".format(right), background = "white",
                                   font = "helvetica 14")
        if labelPosition == "above":
            self.left.grid(column = 1, row = 1, sticky = W)
            self.right.grid(column = 2, row = 1, sticky = E)
        elif labelPosition == "next":
            self.left.grid(column = 0, row = 2, sticky = E)
            self.right.grid(column = 3, row = 2, sticky = W)

        if middle:
            self.middle = ttk.Label(self, text = middle, background = "white",
                                    font = "helvetica 14")
            self.middle.grid(column = 1, row = 1, columnspan = 2)
            self.question["font"] = "helvetica 16"

        self.scale = Canvas(self, background = "white", highlightbackground = "white",
                            highlightcolor = "white")
        self.scale.grid(column = 1, row = 2, sticky = EW, columnspan = 2, padx = 40)

        self.radios = []
        for col, value in enumerate(values):
            padx = 4 if not middle else 18
            self.radios.append(ttk.Radiobutton(self.scale, text = str(value), value = value,
                                               command = self.func, variable = self.answer))
            self.radios[col].grid(row = 0, column = col, padx = padx)
            self.scale.columnconfigure(col, weight = 1)
        if filler:
            self.filler = Canvas(self.scale, background = "white", width = filler, height = 1,
                                 highlightbackground = "white", highlightcolor = "white")
            self.filler.grid(column = 0, row = 1, columnspan = len(values), sticky = EW)
            
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(3, weight = 1)

        self.function = function            
        self.functionProcessed = False
        self.funconce = funconce


    def func(self):
        if not self.funconce or not self.functionProcessed:
            if self.function:
                self.function()
                self.functionProcessed = True


    def write(self):
        if self.text:
            ans = "{}\t{}".format(self.text, self.answer.get())
        else:
            ans = self.answer.get()
        self.root.file.write(ans)

    def check(self):
        return self.answer.get()


class MultipleChoice(Canvas):
    def __init__(self, root, text, answers, feedback, randomize = True, callback = False):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.root = root
        self.answer = StringVar()
        self.feedbackTexts = feedback
        self.answers = answers
        self.callback = callback
        
        self.question = ttk.Label(self, text = text, background = "white", anchor = "center",
                                          font = "helvetica 15 bold")
        self.question.grid(column = 0, row = 0, pady = 5, sticky = W)

        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 15")
        self.radios = []
        self.order = [i for i in range(len(answers))]
        if randomize:
            random.shuffle(self.order)
        for i in range(len(answers)):            
            self.radios.append(ttk.Radiobutton(self, text = answers[self.order[i]], value = i + 1,
                                               command = self.answerFunction, variable = self.answer))
            self.radios[i].grid(row = i+ 1, column = 0, pady = 3, sticky = W)

        self.filler = ttk.Label(self, text = " "*150 + "\n ", background = "white", anchor = "center",
                                          font = "helvetica 15", wraplength = 1000)
        self.filler.grid(column = 0, row = len(answers) + 1, pady = 5, sticky = NW)
        self.feedback = ttk.Label(self, text = " \n ", background = "white", anchor = "center",
                                          font = "helvetica 15", wraplength = 900)
        self.feedback.grid(column = 0, row = len(answers) + 1, pady = 5, sticky = NW)
        self.rowconfigure(len(answers) + 1, weight = 1)

    def getAnswer(self):
        return self.answers[self.order[int(self.answer.get()) - 1]].replace("\n", "  ").replace("\t", " ") 

    def answerFunction(self):
        if hasattr(self.root.master, "next"):
            self.root.master.next["state"] = "normal"
        elif hasattr(self.root, "next"):
            self.root.next["state"] = "normal"
        if self.callback:
            self.callback()
        
    def showFeedback(self):
        self.feedback["text"] = self.feedbackTexts[self.order[int(self.answer.get()) - 1]]
        for radio in self.radios:
            radio["state"] = "disabled"
        
        

class InstructionsAndUnderstanding(InstructionsFrame):
    def __init__(self, root, controlTexts, name, randomize = True, fillerheight = 255, finalButton = None, **kwargs):
        super().__init__(root, **kwargs)
        if type(controlTexts) == str:
            self.controlTexts = self.root.texts[controlTexts]
        else:
            self.controlTexts = controlTexts
        self.randomize = randomize
        self.finalButton = finalButton

        self.controlFrame = Canvas(self, background = "white", highlightbackground = "white",
                                 highlightcolor = "white")
        self.filler2 = Canvas(self.controlFrame, background = "white", width = 1, height = fillerheight,
                                highlightbackground = "white", highlightcolor = "white")
        self.filler2.grid(column = 1, row = 0, rowspan = 10, sticky = NS)

        self.controlFrame.grid(row = 2, column = 1)
        self.next.grid(row = 3, column = 1)

        self.controlNum = 0
        self.createQuestion()
        self.file.write(name + "\n")

    def createQuestion(self):
        if self.controlNum:
            self.controlQuestion.grid_forget()
        self.next["state"] = "disabled"
        texts = self.controlTexts[self.controlNum]
        self.controlQuestion = MultipleChoice(self.controlFrame, text = texts[0], answers = texts[1], feedback = texts[2], randomize = self.randomize)
        self.controlQuestion.grid(row = 0, column = 0)
        self.controlNum += 1
        self.controlstate = "answer"
        
    def nextFun(self):        
        if self.controlstate == "feedback":
            self.file.write(self.id + "\t" + str(self.controlNum) + "\t" + self.controlQuestion.getAnswer() + "\n")
            if self.controlNum == len(self.controlTexts):
                self.file.write("\n")
                super().nextFun()   
            else:
                self.createQuestion()                
        else:            
            self.controlQuestion.showFeedback()
            self.controlstate = "feedback"     
            if self.controlNum == len(self.controlTexts) and self.finalButton:         
                self.next["text"] = self.finalButton


class OneFrame(Canvas):
    def __init__(self, root, question, items, scale, wrap = 480):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.root = root
        self.file = self.root.file

        self.answers = scale
        
        self.lab1 = ttk.Label(self, text = question, font = "helvetica 15", background = "white")
        self.lab1.grid(row = 2, column = 1, pady = 10, columnspan = 2)
        self.measures = []
        for count, word in enumerate(items):
            self.measures.append(Measure(self, word, self.answers, "", "", function = self.root.check,
                                         labelPosition = "none"))
            self.measures[count].grid(row = count + 3, column = 1, columnspan = 2, sticky = E)
            self.measures[count].question["wraplength"] = wrap
            self.measures[count].question["justify"] = "right"

    def check(self):
        for measure in self.measures:
            if not measure.answer.get():
                return False
        else:
            return True             

    def write(self):
        for num, measure in enumerate(self.measures):
            self.file.write(str(self.answers.index(measure.answer.get()) + 1))
            if num != len(self.measures) - 1:
                self.file.write("\t")


def read_all(file, encoding = "utf-8"):
    text = ""
    with open(os.path.join(os.path.dirname(__file__), file), encoding = encoding) as f:
        for line in f:
            text += line.rstrip(" \t")
    return text
