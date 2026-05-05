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

instructionsC0 = """Now you will proceed with another task."""

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

Choose Option A or Option B. Then state the probability (0-100%) that your choice matches the other participant's choice in this trial."""

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

        ttk.Style().configure("TRadiobutton", background="white", font="helvetica 15")

        choice_frame = Canvas(self, background="white", highlightbackground="white", highlightcolor="white")
        choice_frame.grid(row=2, column=1, pady=10)

        ttk.Radiobutton(
            choice_frame,
            text="Option A",
            variable=self.decision_var,
            value="A",
            command=self._selected,
        ).grid(row=0, column=0, padx=20, pady=6, sticky=W)

        ttk.Radiobutton(
            choice_frame,
            text="Option B",
            variable=self.decision_var,
            value="B",
            command=self._selected,
        ).grid(row=1, column=0, padx=20, pady=6, sticky=W)

        self.prediction_label = ttk.Label(
            self,
            text="Probability your choice matches the other participant: 50 %",
            font="helvetica 15",
            background="white",
        )
        self.prediction_label.grid(row=3, column=0, columnspan=3, pady=8)

        self.prediction_scale = ttk.Scale(
            self,
            orient=HORIZONTAL,
            from_=0,
            to=100,
            length=400,
            variable=self.prediction_var,
            command=self._update_prediction_label,
        )
        self.prediction_scale.grid(row=4, column=1, pady=8)
        self.prediction_scale.state(["disabled"])

        self.next.grid(row=5, column=1, pady=15)
        self.next["state"] = "disabled"

        self.rowconfigure(0, weight=1)
        self.rowconfigure(5, weight=2)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(2, weight=2)

    def _selected(self):
        self.prediction_scale.state(["!disabled"])
        self.next["state"] = "normal"

    def _update_prediction_label(self, value):
        val = int(round(float(value)))
        self.prediction_var.set(val)
        self.prediction_label["text"] = (
            "Probability your choice matches the other participant: {} %".format(val)
        )

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
        self.decision_var.set(random.choice(["A", "B"]))
        self._selected()
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


class CoordinationSummary(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)
        self._ensure_all_results()

        header = ttk.Label(
            self,
            text="Coordination Game - Summary",
            font="helvetica 15 bold",
            background="white",
        )
        header.grid(row=0, column=0, columnspan=3, pady=20)

        columns = ("partner", "trial", "your_choice", "partner_choice", "coord", "payoff")
        tree = ttk.Treeview(self, columns=columns, show="headings", height=COORDINATION_ROUNDS * 2 + 1)
        ttk.Style().configure("Treeview", font="helvetica 13", rowheight=28, background="white", fieldbackground="white")
        ttk.Style().configure("Treeview.Heading", font="helvetica 13 bold")

        tree.heading("partner", text="Participant")
        tree.heading("trial", text="Trial")
        tree.heading("your_choice", text="Your choice")
        tree.heading("partner_choice", text="Other choice")
        tree.heading("coord", text="Coordinated")
        tree.heading("payoff", text="Payoff (CZK)")

        tree.column("partner", width=110, anchor="center")
        tree.column("trial", width=80, anchor="center")
        tree.column("your_choice", width=130, anchor="center")
        tree.column("partner_choice", width=130, anchor="center")
        tree.column("coord", width=130, anchor="center")
        tree.column("payoff", width=120, anchor="center")

        total = 0
        results = self.root.status.get("co_results", {})
        for block in range(1, COORDINATION_ROUNDS + 1):
            for trial in (1, 2):
                r = results.get(block, {}).get(trial, {})
                payoff = int(r.get("payoff", 0))
                total += payoff
                tree.insert(
                    "",
                    "end",
                    values=(
                        block,
                        trial,
                        r.get("my_decision", "-"),
                        r.get("partner_decision", "-"),
                        "Yes" if r.get("coordinated", False) else "No",
                        payoff,
                    ),
                )

        tree.insert("", "end", values=("", "", "", "", "Total", total))
        tree.grid(row=1, column=0, columnspan=3, pady=10, padx=25)

        self.root.status["co_total"] = total

        note = ttk.Label(
            self,
            text="You have completed all coordination trials. One randomly selected trial will determine payment for this task.",
            font="helvetica 13 italic",
            background="white",
            wraplength=700,
        )
        note.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Style().configure("TButton", font="helvetica 15")
        self.next = ttk.Button(self, text="Pokračovat", command=self.nextFun)
        self.next.grid(row=3, column=0, columnspan=3, pady=20)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(3, weight=2)

    def _ensure_all_results(self):
        self.root.status.setdefault("co_results", {})
        decisions = self.root.status.get("co_decisions", {})

        for block in range(1, COORDINATION_ROUNDS + 1):
            block_decisions = decisions.get(block, {})
            for trial in (1, 2):
                if trial not in block_decisions:
                    continue
                if trial in self.root.status["co_results"].get(block, {}):
                    continue

                my_decision = block_decisions[trial].get("decision", "A")
                prediction = int(block_decisions[trial].get("prediction", 50))
                partner_decision = random.choice(["A", "B"])
                coordinated = my_decision == partner_decision
                payoff = COORDINATION_SUCCESS if coordinated else 0

                self.root.status["co_results"].setdefault(block, {})
                self.root.status["co_results"][block][trial] = {
                    "my_decision": my_decision,
                    "partner_decision": partner_decision,
                    "coordinated": coordinated,
                    "payoff": payoff,
                    "prediction": prediction,
                }

    def write(self):
        self.file.write("CoordinationSummary\n")
        results = self.root.status.get("co_results", {})
        for block in range(1, COORDINATION_ROUNDS + 1):
            for trial in (1, 2):
                r = results.get(block, {}).get(trial, {})
                self.file.write(
                    "\t".join(
                        [
                            self.id,
                            str(block),
                            str(trial),
                            r.get("my_decision", ""),
                            r.get("partner_decision", ""),
                            "1" if r.get("coordinated", False) else "0",
                            str(r.get("payoff", "")),
                            str(r.get("prediction", "")),
                        ]
                    )
                    + "\n"
                )
        self.file.write("\n")


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
        IntroCoordination,
        InstructionsCoordination,
        *([CoordinationGame, WaitCoordination, CoordinationRoundResult, CoordinationGame] * COORDINATION_ROUNDS),
        CoordinationSummary,
        WaitResults,
        Ending,
    ])
