from tkinter import *
from tkinter import ttk

import random
import os

from common import ExperimentFrame, InstructionsFrame, InstructionsAndUnderstanding, Wait
from gui import GUI
from constants import COORDINATION_ROUNDS, COORDINATION_SUCCESS
from login import Login


################################################################################
# TEXTS

instructionsC0 = """<center>Now you will proceed with another task.</center>"""

instructionsC1 = """In this task, you will play with {} different participants. With each participant, you will make decisions in two consecutive trials.

In each trial, both of you simultaneously choose one option:
  • Option A
  • Option B

Payoffs:
  • If both participants choose the same option, coordination is successful and both receive CZK {}.
  • If participants choose different options, both receive CZK 0.

After the first trial with each participant, you will receive feedback about both choices and your payoff. After the second trial with that same participant, no immediate feedback will be shown.

At the end of this game, one randomly selected trial determines your payment for this task."""

instructionsC2 = """Coordination Game

You are now making your decision for participant {}/{} (trial {}/2).

Choose Option A or Option B."""

coordinationPrompt = "<b>Please answer the following control questions to check your understanding of the instructions.</b>"

coordControl1 = "What happens if both participants choose the same option?"
coordAnswers1 = [
    "Both receive CZK {}".format(COORDINATION_SUCCESS),
    "Both receive CZK 0",
    "Only one participant receives money",
]
coordFeedback1 = [
    "Correct.",
    "Incorrect. If both choose the same option, both receive CZK {}.".format(COORDINATION_SUCCESS),
    "Incorrect. If both choose the same option, both receive CZK {}.".format(COORDINATION_SUCCESS),
]

coordControl2 = "When do you receive immediate feedback in this game?"
coordAnswers2 = [
    "After the first trial with each participant",
    "After both trials with each participant",
    "No feedback is shown during the task",
]
coordFeedback2 = [
    "Correct.",
    "Incorrect. Immediate feedback is shown only after the first trial with each participant.",
    "Incorrect. Immediate feedback is shown after the first trial with each participant.",
]

coordControl3 = "How many trials do you play with each participant?"
coordAnswers3 = ["2", "1", "3"]
coordFeedback3 = [
    "Correct.",
    "Incorrect. You play 2 trials with each participant.",
    "Incorrect. You play 2 trials with each participant.",
]

coordControlTexts = [
    [coordControl1, coordAnswers1, coordFeedback1],
    [coordControl2, coordAnswers2, coordFeedback2],
    [coordControl3, coordAnswers3, coordFeedback3],
]

coordResultText = """<b>Feedback: participant {}/{} - trial 1</b>

Your choice: {}
Other participant's choice: {}
Coordination successful: {}
Your payoff in this trial: CZK {}"""


################################################################################


class CoordinationGame(InstructionsFrame):
    def __init__(self, root):
        block = root.status.get("co_block", 1)
        trial = root.status.get("co_trial", 1)
        text = instructionsC2.format(block, COORDINATION_ROUNDS, trial)
        super().__init__(root, text=text, height=12, font=15, width=85)

        self.block = block
        self.trial = trial
        self.decision_var = StringVar()
        self.prediction_var = IntVar(value=50)

        ttk.Style().configure("TButton", font="helvetica 15")
        ttk.Style().configure("Coordination.Horizontal.TScale", background="white")

        choice_frame = Canvas(self, background="white", highlightbackground="white", highlightcolor="white")
        choice_frame.grid(row=2, column=1, pady=10)

        self.option_a_button = ttk.Button(
            choice_frame,
            text="Option A",
            command=lambda: self._selected("A"),
        )
        self.option_a_button.grid(row=0, column=0, padx=20, pady=6, sticky=W)

        self.option_b_button = ttk.Button(
            choice_frame,
            text="Option B",
            command=lambda: self._selected("B"),
        )
        self.option_b_button.grid(row=0, column=1, padx=20, pady=6, sticky=W)

        # Fixed-height fillers keep layout stable before hidden widgets appear.
        self.filler_prediction = Canvas(self, background="white", highlightbackground="white", highlightcolor="white", height=40, width=1)
        self.filler_prediction.grid(row=3, column=0, columnspan=1, sticky=W)

        self.filler_scale = Canvas(self, background="white", highlightbackground="white", highlightcolor="white", height=40, width=1)
        self.filler_scale.grid(row=4, column=0, columnspan=1, sticky=W)

        self.filler_probability = Canvas(self, background="white", highlightbackground="white", highlightcolor="white", height=40, width=1)
        self.filler_probability.grid(row=5, column=0, columnspan=1, sticky=W)

        self.filler_next = Canvas(self, background="white", highlightbackground="white", highlightcolor="white", height=40, width=1)
        self.filler_next.grid(row=6, column=0, columnspan=1, sticky=W)

        self.prediction_label = ttk.Label(
            self,
            text="What would you estimate is the probability your choice matches the other participant?",
            font="helvetica 15",
            background="white",
        )
        self.prediction_label.grid(row=3, column=0, columnspan=3, pady=4)
        self.prediction_label.grid_remove()

        self.prediction_scale = ttk.Scale(
            self,
            orient=HORIZONTAL,
            from_=0,
            to=100,
            length=400,
            variable=self.prediction_var,
            command=self._update_prediction_label,
            style="Coordination.Horizontal.TScale",
        )
        self.prediction_scale.grid(row=4, column=1, pady=2)
        self.prediction_scale.grid_remove()

        self.prediction_value_label = ttk.Label(
            self,
            text="50 %",
            font="helvetica 15",
            background="white",
        )
        self.prediction_value_label.grid(row=5, column=0, columnspan=3, pady=4)
        self.prediction_value_label.grid_remove()

        self.next.grid(row=6, column=1, pady=8)
        self.next.grid_remove()

        self.rowconfigure(0, weight=1)
        self.rowconfigure(6, weight=2)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(2, weight=2)

    def _selected(self, decision):
        self.decision_var.set(decision)
        self.prediction_label.grid()
        self.prediction_scale.grid()
        self.prediction_value_label.grid()
        self.next.grid()

    def _update_prediction_label(self, value):
        val = int(round(float(value)))
        self.prediction_var.set(val)
        self.prediction_value_label["text"] = "{} %".format(val)

    def nextFun(self):
        if not self.decision_var.get():
            return
        self.write()
        self.destroy()
        self.root.nextFrame()

    def _ensure_status(self):
        self.root.status.setdefault("co_block", 1)
        self.root.status.setdefault("co_trial", 1)
        self.root.status.setdefault("co_decisions", {})

    def write(self):
        self._ensure_status()
        decision = self.decision_var.get()
        prediction = int(self.prediction_var.get())

        self.root.status["co_decisions"].setdefault(self.block, {})
        self.root.status["co_decisions"][self.block][self.trial] = {
            "decision": decision,
            "prediction": prediction,
        }

        data = {
            "id": self.id,
            "round": "coordination{}_{}".format(self.block, self.trial),
            "offer": "{}_{}".format(decision, prediction),
        }
        self.sendData(data)

        if self.trial == 2:
            self.root.status["co_block"] = self.block + 1
            self.root.status["co_trial"] = 1

        self.file.write("CoordinationGame\n")
        self.file.write(
            "\t".join([self.id, str(self.block), str(self.trial), decision, str(prediction)])
        )
        self.file.write("\n\n")

    def gothrough(self):
        self._selected(random.choice(["A", "B"]))
        self.prediction_var.set(50)
        self._update_prediction_label("50")
        sleep = __import__("time").sleep
        sleep(0.1)
        self.nextFun()


class WaitCoordination(Wait):
    def __init__(self, root):
        super().__init__(root, what="coordination")

    def test(self):
        return random.choice(["A", "B"])

    def processResponse(self, response):
        block = self.root.status.get("co_block", 1)
        trial = 1

        partner_decision = response.strip().upper()
        if partner_decision not in ("A", "B"):
            partner_decision = random.choice(["A", "B"])

        my_trial = self.root.status.get("co_decisions", {}).get(block, {}).get(trial, {})
        my_decision = my_trial.get("decision", "A")
        prediction = int(my_trial.get("prediction", 50))

        coordinated = my_decision == partner_decision
        payoff = COORDINATION_SUCCESS if coordinated else 0

        self.root.status.setdefault("co_results", {})
        self.root.status["co_results"].setdefault(block, {})
        self.root.status["co_results"][block][trial] = {
            "my_decision": my_decision,
            "partner_decision": partner_decision,
            "coordinated": coordinated,
            "payoff": payoff,
            "prediction": prediction,
        }

        # After first-trial feedback, continue with trial 2 for the same participant.
        self.root.status["co_trial"] = 2


class CoordinationRoundResult(InstructionsFrame):
    def __init__(self, root):
        block = root.status.get("co_block", 1)
        result = root.status.get("co_results", {}).get(block, {}).get(1, {})

        my_choice = result.get("my_decision", "-")
        partner_choice = result.get("partner_decision", "-")
        coordinated = "Yes" if result.get("coordinated", False) else "No"
        payoff = result.get("payoff", 0)

        text = coordResultText.format(block, COORDINATION_ROUNDS, my_choice, partner_choice, coordinated, payoff)
        super().__init__(root, text=text, height=9, font=15, width=70)



################################################################################
# Tuples for use in frame lists

IntroCoordination = (
    InstructionsFrame,
    {
        "text": instructionsC0,
        "height": "auto",
        "width": 80,
        "font": 15,
    },
)

InstructionsCoordination = (
    InstructionsAndUnderstanding,
    {
        "text": instructionsC1.format(COORDINATION_ROUNDS, COORDINATION_SUCCESS) + "\n\n",
        "height": "auto",
        "width": 90,
        "name": "Coordination Control Questions",
        "randomize": False,
        "controlTexts": coordControlTexts,
        "fillerHeight": 170,
        "finalButton": "Continue to the game",
        "prompt": coordinationPrompt,
    },
)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    from intros import Ending
    from games import WaitResults

    GUI([
        Login,
        #IntroCoordination,
        #InstructionsCoordination,
        *([CoordinationGame, WaitCoordination, CoordinationRoundResult, CoordinationGame] * COORDINATION_ROUNDS),
        WaitResults,
        Ending,
    ])
