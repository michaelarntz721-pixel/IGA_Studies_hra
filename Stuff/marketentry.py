from tkinter import *
from tkinter import ttk
from time import sleep
import random
import os
import re

from common import ExperimentFrame, InstructionsFrame, InstructionsAndUnderstanding
from gui import GUI
from constants import TESTING, MARKET_ROUNDS, MARKET_ENDOWMENT, MARKET_WIN, MARKET_LOSS
from login import Login


################################################################################
# TEXTS

meIntro0 = """<center>Now you will proceed with another task.</center>"""

meIntro1 = """First, you will complete a short quiz consisting of 5 estimation questions. For each question, please provide your best estimate.

After the quiz, you will participate in a market entry game consisting of {} rounds. In each round, you will be randomly paired with another participant.

In each round, you will choose between:
  \u2022 Enter the market
  \u2022 Stay out

<b>Payoffs:</b>
  \u2022 If both participants stay out, each receives CZK {}
  \u2022 If one enters and the other stays out, the entrant receives CZK {} and the other receives CZK {}
  \u2022 If both enter, the participant with the higher quiz score receives CZK {} and the other receives CZK {} (in case of a tie, the winner is chosen randomly)

Your performance on the quiz will be used in determining outcomes in the market entry game. You will not receive feedback during the task. One randomly selected round will determine your payment for this part of the study."""

meIntro2 = """Please answer the following questions. For each question, provide your best numerical estimate. There are no time limits, but answer as accurately as possible."""

meGameText = """You will now make your decision for Round {}/{}.

In this round, you will be randomly paired with another participant. Both of you choose simultaneously and independently whether to enter the market or stay out.

<b>Reminder \u2013 Payoffs:</b>
  \u2022 Both stay out: CZK {} each
  \u2022 One enters, one stays out: entrant CZK {}, other CZK {}
  \u2022 Both enter: higher quiz score earns CZK {}, lower earns CZK {}"""

meConfidenceText = "Out of the {} questions you just answered, how many do you think you answered correctly?"

meRoundResultText = """<b>Round {} result</b>

Your decision:\t\t{}
Number of entrants:\t{}
Your payoff this round:\tCZK {}"""

# Control questions
meControl1 = "What happens if both participants stay out?"
meAnswers1 = ["CZK {} each".format(MARKET_ENDOWMENT),
			  "CZK 0",
			  "CZK {}".format(MARKET_WIN)]
meFeedback1 = ["Correct.",
			   "Incorrect. If both stay out, each receives CZK {}.".format(MARKET_ENDOWMENT),
			   "Incorrect. If both stay out, each receives CZK {}.".format(MARKET_ENDOWMENT)]

meControl2 = "What happens if both participants enter the market?"
meAnswers2 = ["Outcome depends on quiz score",
			  "Always CZK {}".format(MARKET_WIN),
			  "Both get CZK {}".format(MARKET_ENDOWMENT)]
meFeedback2 = ["Correct. The participant with the higher quiz score wins CZK {}.".format(MARKET_WIN),
			   "Incorrect. The outcome depends on quiz scores.",
			   "Incorrect. The outcome depends on quiz scores."]

meControl3 = "How many rounds will be played?"
meAnswers3 = [str(MARKET_ROUNDS),
			  str(MARKET_ROUNDS + 1),
			  str(MARKET_ROUNDS - 1)]
meFeedback3 = ["Correct.",
			   "Incorrect. There are {} rounds.".format(MARKET_ROUNDS),
			   "Incorrect. There are {} rounds.".format(MARKET_ROUNDS)]

meControlTexts = [
	[meControl1, meAnswers1, meFeedback1],
	[meControl2, meAnswers2, meFeedback2],
	[meControl3, meAnswers3, meFeedback3],
]

# Quiz question sets: one set per round.
# Each question: (display text, true value for scoring)
# Scoring: answer within 10 % of the true value counts as correct.
# Rounds 2+ use placeholder questions – replace before deployment.
ME_QUIZ_QUESTIONS = [
	# Round 1
	[
		("What is the straight-line distance between Berlin and Vienna in kilometers?", 524),
		("What is the population of Berlin?", 3_600_000),
		("What is the population of Norway?", 5_400_000),
		("What is the height of the tallest mountain in Europe in meters?", 5_642),
		("What is the GDP per capita of Luxembourg in CZK (2024)?", 3_000_000),
	],
	# Round 2 – replace with actual questions
	[
		("What is the straight-line distance from Prague to Paris in kilometers?", 1_050),
		("What is the population of Vienna?", 1_900_000),
		("What is the area of Switzerland in km\u00b2?", 41_285),
		("What is the height of Mont Blanc in meters?", 4_808),
		("What is the GDP per capita of Switzerland in CZK (2024)?", 2_000_000),
	],
	# Round 3 – replace with actual questions
	[
		("What is the straight-line distance from London to Madrid in kilometers?", 1_265),
		("What is the population of Munich?", 1_500_000),
		("What is the area of Sweden in km\u00b2?", 450_295),
		("What is the length of the Rhine river in kilometers?", 1_230),
		("What is the GDP per capita of Denmark in CZK (2024)?", 1_700_000),
	],
	# Round 4 – replace with actual questions
	[
		("What is the straight-line distance from Rome to Athens in kilometers?", 1_050),
		("What is the population of Hamburg?", 1_900_000),
		("What is the area of Finland in km\u00b2?", 338_145),
		("What is the height of the Zugspitze in meters?", 2_962),
		("What is the GDP per capita of Austria in CZK (2024)?", 1_200_000),
	],
]

understandingPrompt = "<b>Please answer the following control questions to check your understanding of the instructions.</b>"

################################################################################


class MarketEntryQuiz(ExperimentFrame):
	"""Two-phase frame: (1) 5 estimation questions, (2) confidence about correct count."""

	def __init__(self, root):
		super().__init__(root)
		if "me_block" not in self.root.status:
			self.root.status["me_block"] = 1

		self.block = self.root.status["me_block"]
		idx = min(self.block - 1, len(ME_QUIZ_QUESTIONS) - 1)
		self.question_set = ME_QUIZ_QUESTIONS[idx]
		self.quiz_raw = []
		self.phase = 1
		self._build_quiz()

	def _validate_numeric_input(self, value):
		"""Allow digits with optional decimal separator (comma or dot)."""
		if value == "":
			return True
		return bool(re.fullmatch(r"\d*([\.,]\d*)?", value))

	def _normalize_numeric_string(self, value):
		"""Normalize user numeric input for parsing (comma decimal -> dot)."""
		return value.replace(",", ".").replace("\u00a0", "").replace(" ", "")

	def _all_quiz_answers_valid(self):
		if not hasattr(self, "entry_vars"):
			return False
		for var in self.entry_vars:
			value = var.get().strip()
			if not value or not self._validate_numeric_input(value):
				return False
		return True

	def _update_quiz_next_state(self, *args):
		if hasattr(self, "next"):
			self.next["state"] = "normal" if self._all_quiz_answers_valid() else "disabled"

	# ------------------------------------------------------------------
	def _build_quiz(self):
		header = ttk.Label(self,
						   text="Quiz \u2013 Round {}/{}".format(self.block, MARKET_ROUNDS),
						   font="helvetica 15 bold", background="white")
		header.grid(row=0, column=0, columnspan=3, pady=15)

		intro = Text(self, font="helvetica 15", relief="flat", background="white",
					 width=80, height=3, wrap="word", highlightbackground="white",
					 highlightcolor="white")
		intro.insert("1.0", meIntro2)
		intro.config(state="disabled")
		intro.grid(row=1, column=0, columnspan=3, pady=5)

		self.entry_vars = []
		vcmd = (self.register(self._validate_numeric_input), "%P")
		for i, (q_text, _) in enumerate(self.question_set):
			ttk.Label(self, text=q_text, font="helvetica 15", background="white",
					  wraplength=580, anchor="w", justify="left").grid(
				row=2 + i, column=0, sticky=W, padx=60, pady=4)
			var = StringVar()
			var.trace_add("write", self._update_quiz_next_state)
			ent = ttk.Entry(self, textvariable=var, width=14, font="helvetica 15",
							validate="key", validatecommand=vcmd)
			ent.grid(row=2 + i, column=1, sticky=W, padx=10, pady=4)
			self.entry_vars.append(var)

		ttk.Style().configure("TButton", font="helvetica 15")
		self.next = ttk.Button(self, text="Pokračovat", command=self.nextFun)
		self.next.grid(row=2 + len(self.question_set), column=0, columnspan=3, pady=20)
		self.next["state"] = "disabled"

		self.columnconfigure(0, weight=1)
		self.columnconfigure(2, weight=1)
		self.rowconfigure(0, weight=1)
		self.rowconfigure(2 + len(self.question_set), weight=2)

	def _build_confidence(self):
		for widget in self.winfo_children():
			widget.destroy()

		header = ttk.Label(self, text="Confidence estimate",
						   font="helvetica 15 bold", background="white")
		header.grid(row=0, column=0, columnspan=3, pady=15)

		ttk.Label(self, text=meConfidenceText.format(len(self.question_set)),
				  font="helvetica 15", background="white",
				  wraplength=700).grid(row=1, column=0, columnspan=3, pady=15)

		self.confidence_var = StringVar()
		ttk.Style().configure("TRadiobutton", background="white", font="helvetica 15")
		conf_frame = Canvas(self, background="white",
							highlightbackground="white", highlightcolor="white")
		conf_frame.grid(row=2, column=0, columnspan=3, pady=10)
		for j in range(len(self.question_set) + 1):
			ttk.Radiobutton(conf_frame, text=str(j), variable=self.confidence_var,
							value=str(j), command=self._enable_next).grid(
				row=0, column=j, padx=8)

		ttk.Style().configure("TButton", font="helvetica 15")
		self.next = ttk.Button(self, text="Pokračovat", command=self.nextFun,
							   state="disabled")
		self.next.grid(row=3, column=0, columnspan=3, pady=20)

		self.columnconfigure(0, weight=1)
		self.columnconfigure(2, weight=1)
		self.rowconfigure(0, weight=1)
		self.rowconfigure(3, weight=2)

	def _enable_next(self):
		self.next["state"] = "normal"

	def _score_quiz(self):
		"""Count questions answered within 10 % of the true value."""
		score = 0
		for i, (_, correct) in enumerate(self.question_set):
			try:
				raw = self._normalize_numeric_string(self.quiz_raw[i])
				ans = float(raw)
				if correct > 0 and abs(ans - correct) / correct <= 0.10:
					score += 1
			except (ValueError, IndexError):
				pass
		return score

	# ------------------------------------------------------------------
	def nextFun(self):
		if self.phase == 1:
			if not all(v.get().strip() for v in self.entry_vars):
				return
			self.quiz_raw = [v.get().strip() for v in self.entry_vars]
			self.phase = 2
			self._build_confidence()
		else:
			self.write()
			self.destroy()
			self.root.nextFrame()

	def write(self):
		score = self._score_quiz()
		if "me_quiz_scores" not in self.root.status:
			self.root.status["me_quiz_scores"] = {}
		self.root.status["me_quiz_scores"][self.block] = score

		self.file.write("MarketEntryQuiz\n")
		self.file.write("\t".join(
			[self.id, str(self.block)] + self.quiz_raw + [str(score), self.confidence_var.get()]
		))
		self.file.write("\n\n")

	def gothrough(self):
		sleep(0.1)
		if self.phase == 1:
			for var in self.entry_vars:
				var.set("1000")
			self.quiz_raw = ["1000"] * len(self.entry_vars)
			self.phase = 2
			self._build_confidence()
		if self.phase == 2:
			self.confidence_var.set(str(len(self.question_set) // 2))
			self._enable_next()
			sleep(0.1)
			self.write()
			self.destroy()
			self.root.nextFrame()


################################################################################


class MarketEntryGame(InstructionsFrame):
	"""Decision screen: Enter the market or Stay out."""

	def __init__(self, root):
		block = root.status.get("me_block", 1)
		text = meGameText.format(block, MARKET_ROUNDS,
								 MARKET_ENDOWMENT, MARKET_WIN, MARKET_ENDOWMENT,
								 MARKET_WIN, MARKET_LOSS)
		super().__init__(root, text=text, height=12, font=15, width=80)

		self.block = block
		self.decision_var = StringVar()
		ttk.Style().configure("TRadiobutton", background="white", font="helvetica 15")

		choice_frame = Canvas(self, background="white",
							  highlightbackground="white", highlightcolor="white")
		ttk.Radiobutton(choice_frame, text="Enter the market",
						variable=self.decision_var, value="enter",
						command=self._selected).grid(row=0, column=0, padx=20, pady=10, sticky=W)
		ttk.Radiobutton(choice_frame, text="Stay out",
						variable=self.decision_var, value="stayout",
						command=self._selected).grid(row=1, column=0, padx=20, pady=10, sticky=W)
		choice_frame.grid(row=2, column=1, pady=15)

		note = ttk.Label(self,
						 text="Your quiz performance may determine outcomes when both participants choose to enter.",
						 font="helvetica 13 italic", background="white", wraplength=600)
		note.grid(row=3, column=0, columnspan=3, pady=5)

		self.trialLabel = ttk.Label(self,
									text="Round {}/{}".format(block, MARKET_ROUNDS),
									font="helvetica 15", background="white")
		self.trialLabel.grid(row=0, column=2, pady=15, padx=20, sticky=NE)

		self.next.grid(row=4, column=1, pady=15)
		self.next["state"] = "disabled"

		self.rowconfigure(0, weight=1)
		self.rowconfigure(4, weight=2)
		self.columnconfigure(0, weight=2)
		self.columnconfigure(2, weight=2)

	def _selected(self):
		self.next["state"] = "normal"

	def nextFun(self):
		if not self.decision_var.get():
			return
		self.write()
		self.destroy()
		self.root.nextFrame()

	def write(self):
		decision = self.decision_var.get()
		if "me_decisions" not in self.root.status:
			self.root.status["me_decisions"] = {}
		self.root.status["me_decisions"][self.block] = decision
		self.root.status["me_block"] = self.block + 1
		self.file.write("MarketEntryGame\n")
		self.file.write(self.id + "\t" + str(self.block) + "\t" + decision + "\n\n")

	def gothrough(self):
		sleep(0.1)
		self.decision_var.set("enter")
		self._selected()
		sleep(0.1)
		self.nextFun()


################################################################################
# Tuples for use in frame lists

IntroMarketEntry = (InstructionsFrame, {
	"text": meIntro0,
	"height": "auto",
	"width": 80,
	"font": 15,
})

InstructionsMarketEntry = (InstructionsAndUnderstanding, {
	"text": meIntro1.format(MARKET_ROUNDS,
							MARKET_ENDOWMENT,
							MARKET_WIN, MARKET_ENDOWMENT,
							MARKET_WIN, MARKET_LOSS) + "\n\n",
	"height": "auto",
	"width": 90,
	"name": "Market Entry Control Questions",
	"randomize": False,
	"controlTexts": meControlTexts,
	"fillerHeight": 150,
	"finalButton": "Continue to the game",
	"prompt": understandingPrompt,
})


################################################################################

if __name__ == "__main__":
	os.chdir(os.path.dirname(os.getcwd()))
	from intros import Ending
	from games import WaitResults
	GUI([Login,
		 IntroMarketEntry,
		 InstructionsMarketEntry,
		 *([MarketEntryQuiz, MarketEntryGame] * MARKET_ROUNDS),
		 WaitResults,
		 Ending
		 ])




