import tkinter as tk
from tkinter import ttk, messagebox


class EsmFamilGame(tk.Tk):
    """GUI for the Esm-Famil (Name-Family / Categories) game."""

    POINT_UNIQUE = 10   # valid and unique answer
    POINT_SHARED = 5    # valid but shared with another player

    def __init__(self):
        super().__init__()
        self.title("Esm-Famil Game")
        self.geometry("620x560")
        self.minsize(560, 480)

        self.players = []
        self.items = []
        self.letter = ""
        self.answers = {}      # {player: {item: answer}}
        self.current = 0
        self.entries = {}

        self.container = ttk.Frame(self, padding=20)
        self.container.pack(fill="both", expand=True)
        self.show_setup()

    # ---------- helpers ----------
    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    # ---------- setup screen ----------
    def show_setup(self):
        self.clear()
        c = self.container
        ttk.Label(c, text="Esm-Famil Game", font=("Arial", 18, "bold")).pack(pady=(0, 15))

        ttk.Label(c, text="Player names (separated by commas):").pack(anchor="w")
        self.players_var = tk.StringVar()
        ttk.Entry(c, textvariable=self.players_var).pack(fill="x", pady=(2, 10))

        ttk.Label(c, text="Categories (separated by spaces, e.g. name family city food):").pack(anchor="w")
        self.items_var = tk.StringVar(value="name family city food")
        ttk.Entry(c, textvariable=self.items_var).pack(fill="x", pady=(2, 10))

        ttk.Label(c, text="Game letter (one character):").pack(anchor="w")
        self.letter_var = tk.StringVar()
        ttk.Entry(c, textvariable=self.letter_var, justify="center", width=5).pack(anchor="w", pady=(2, 20))

        ttk.Button(c, text="Start Game", command=self.start_game).pack(ipadx=20, ipady=5)

    def start_game(self):
        raw = self.players_var.get()
        players = [p.strip() for p in raw.split(",") if p.strip()]
        items = self.items_var.get().split()
        letter = self.letter_var.get().strip()

        if not players:
            messagebox.showerror("Error", "Enter at least one player.")
            return
        if len(set(players)) != len(players):
            messagebox.showerror("Error", "Player names must be unique.")
            return
        if not items:
            messagebox.showerror("Error", "Enter at least one category.")
            return
        if len(letter) != 1:
            messagebox.showerror("Error", "Enter exactly one letter.")
            return

        self.players, self.items, self.letter = players, items, letter
        self.answers = {}
        self.current = 0
        self.show_turn()

    # ---------- player turn screen ----------
    def show_turn(self):
        self.clear()
        c = self.container
        player = self.players[self.current]

        ttk.Label(c, text=f"{player}'s turn", font=("Arial", 16, "bold")).pack()
        ttk.Label(c, text=f"Letter: {self.letter}", font=("Arial", 24, "bold"),
                  foreground="#c0392b").pack(pady=8)

        form = ttk.Frame(c)
        form.pack(fill="x", pady=5)
        form.columnconfigure(1, weight=1)

        self.entries = {}
        for row, item in enumerate(self.items):
            var = tk.StringVar()
            ttk.Label(form, text=item, width=14, anchor="w").grid(row=row, column=0, pady=4)
            ttk.Entry(form, textvariable=var).grid(
                row=row, column=1, sticky="ew", padx=(8, 0), pady=4)
            self.entries[item] = var

        last = self.current == len(self.players) - 1
        ttk.Button(c, text="Show Results" if last else "Submit & Next Player",
                   command=self.submit_turn).pack(pady=15, ipadx=15, ipady=4)
        self.bind("<Return>", lambda e: self.submit_turn())

    def submit_turn(self):
        # Wrong answers are accepted here and reported in the results screen.
        result = {item: var.get().strip() for item, var in self.entries.items()}
        self.answers[self.players[self.current]] = result
        self.current += 1
        if self.current < len(self.players):
            self.show_turn()
        else:
            self.unbind("<Return>")
            self.show_results()

    # ---------- scoring & results ----------
    def is_valid(self, answer):
        """An answer is valid if it is non-empty and starts with the game letter."""
        return bool(answer) and answer[0].casefold() == self.letter.casefold()

    def get_errors(self):
        """Return a list of (player, category, answer) for all invalid answers."""
        errors = []
        for p in self.players:
            for item in self.items:
                a = self.answers[p][item]
                if a and not self.is_valid(a):
                    errors.append((p, item, a))
        return errors

    def compute_scores(self):
        scores = {p: 0 for p in self.players}
        for item in self.items:
            counts = {}
            for p in self.players:
                a = self.answers[p][item]
                if self.is_valid(a):
                    counts[a.casefold()] = counts.get(a.casefold(), 0) + 1
            for p in self.players:
                a = self.answers[p][item]
                if self.is_valid(a):
                    scores[p] += self.POINT_UNIQUE if counts[a.casefold()] == 1 else self.POINT_SHARED
        return scores

    def show_results(self):
        self.clear()
        c = self.container
        scores = self.compute_scores()

        ttk.Label(c, text="Game Results", font=("Arial", 18, "bold")).pack(pady=(0, 10))

        cols = ["player"] + self.items + ["score"]
        tree = ttk.Treeview(c, columns=cols, show="headings", height=min(len(self.players), 8))
        tree.heading("player", text="Player")
        tree.heading("score", text="Score")
        tree.column("player", width=90, anchor="center")
        tree.column("score", width=60, anchor="center")
        for item in self.items:
            tree.heading(item, text=item)
            tree.column(item, width=90, anchor="center")
        def cell(p, i):
            a = self.answers[p][i]
            return f"✗ {a}" if a and not self.is_valid(a) else a

        for p in sorted(self.players, key=lambda x: -scores[x]):
            tree.insert("", "end",
                        values=[p] + [cell(p, i) for i in self.items] + [scores[p]])
        tree.pack(fill="both", expand=True)

        # Errors section
        errors = self.get_errors()
        err_frame = ttk.LabelFrame(c, text=f"Errors (answers must start with '{self.letter}')",
                                   padding=8)
        err_frame.pack(fill="x", pady=(10, 0))
        if errors:
            for p, item, a in errors:
                ttk.Label(err_frame, text=f"• {p} - {item}: \"{a}\" does not start with '{self.letter}'",
                          foreground="#c0392b").pack(anchor="w")
        else:
            ttk.Label(err_frame, text="No errors. All answers are correct!",
                      foreground="#27ae60").pack(anchor="w")

        best = max(scores.values())
        winners = ", ".join(p for p in self.players if scores[p] == best)
        label = "Winner" if len(winners.split(", ")) == 1 else "Winners"
        ttk.Label(c, text=f"{label}: {winners} ({best} points)",
                  font=("Arial", 13, "bold"), foreground="#27ae60").pack(pady=12)

        btns = ttk.Frame(c)
        btns.pack()
        ttk.Button(btns, text="New Game", command=self.show_setup).pack(side="left", padx=5)
        ttk.Button(btns, text="Quit", command=self.destroy).pack(side="left", padx=5)


if __name__ == "__main__":
    EsmFamilGame().mainloop()
