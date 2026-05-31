import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import date, timedelta

DATA_FILE = "habits.json"

COLORS = {
    "bg":         "#1e1e2e",
    "panel":      "#2a2a3d",
    "accent":     "#7c6af7",
    "accent2":    "#56cfb2",
    "text":       "#e0e0f0",
    "text_dim":   "#888aaa",
    "done":       "#56cfb2",
    "undone":     "#444466",
    "danger":     "#f76a6a",
    "border":     "#3a3a5a",
}

FONT       = ("Segoe UI", 11)
FONT_BOLD  = ("Segoe UI", 11, "bold")
FONT_TITLE = ("Segoe UI", 15, "bold")
FONT_SMALL = ("Segoe UI", 9)


# ── Data helpers ──────────────────────────────────────────────────────────────

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"habits": [], "logs": {}}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def today_str():
    return str(date.today())


def last_n_days(n):
    return [(date.today() - timedelta(days=i)).isoformat() for i in range(n - 1, -1, -1)]


# ── Main App ──────────────────────────────────────────────────────────────────

class HabitApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Трекер привычек")
        self.geometry("720x560")
        self.minsize(600, 460)
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)

        self.data = load_data()
        self._build_ui()
        self.show_today()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Left sidebar
        sidebar = tk.Frame(self, bg=COLORS["panel"], width=160)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="📋 Привычки", font=FONT_TITLE,
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(pady=(24, 20))

        nav_items = [
            ("Сегодня",    self.show_today),
            ("Статистика", self.show_stats),
            ("Привычки",   self.show_manage),
        ]
        self.nav_buttons = {}
        for label, cmd in nav_items:
            b = tk.Button(sidebar, text=label, font=FONT, bd=0, cursor="hand2",
                          bg=COLORS["panel"], fg=COLORS["text"],
                          activebackground=COLORS["accent"],
                          activeforeground="white",
                          relief="flat", pady=10,
                          command=cmd)
            b.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[label] = b

        # Main content area
        self.content = tk.Frame(self, bg=COLORS["bg"])
        self.content.pack(side="left", fill="both", expand=True)

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _set_active_nav(self, label):
        for lbl, btn in self.nav_buttons.items():
            if lbl == label:
                btn.configure(bg=COLORS["accent"], fg="white")
            else:
                btn.configure(bg=COLORS["panel"], fg=COLORS["text"])

    # ── Today view ────────────────────────────────────────────────────────────

    def show_today(self):
        self._clear_content()
        self._set_active_nav("Сегодня")

        day = today_str()
        done_list = self.data["logs"].get(day, [])

        tk.Label(self.content, text=f"Сегодня — {day}", font=FONT_TITLE,
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(24, 6), padx=24, anchor="w")
        tk.Label(self.content, text="Отметьте выполненные привычки", font=FONT,
                 bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(padx=24, anchor="w")

        # Scrollable list
        canvas = tk.Canvas(self.content, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=COLORS["bg"])

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=24, pady=16)
        scrollbar.pack(side="right", fill="y")

        if not self.data["habits"]:
            tk.Label(frame, text="Нет привычек. Добавьте в разделе «Привычки».",
                     font=FONT, bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(pady=40)
            return

        for habit in self.data["habits"]:
            is_done = habit in done_list
            self._habit_row(frame, habit, is_done, day)

        # Progress bar
        total = len(self.data["habits"])
        done_count = len([h for h in self.data["habits"] if h in done_list])
        self._progress_bar(done_count, total)

    def _habit_row(self, parent, habit, is_done, day):
        row = tk.Frame(parent, bg=COLORS["panel"], pady=10, padx=14,
                       highlightbackground=COLORS["border"], highlightthickness=1)
        row.pack(fill="x", pady=5)

        color = COLORS["done"] if is_done else COLORS["undone"]
        check_text = "✓" if is_done else "○"

        check_btn = tk.Button(row, text=check_text, font=FONT_BOLD,
                              bg=color, fg="white", bd=0, width=3,
                              relief="flat", cursor="hand2",
                              command=lambda h=habit: self._toggle(h, day))
        check_btn.pack(side="left", padx=(0, 12))

        tk.Label(row, text=habit, font=FONT,
                 bg=COLORS["panel"],
                 fg=COLORS["done"] if is_done else COLORS["text"]).pack(side="left")

    def _toggle(self, habit, day):
        logs = self.data["logs"]
        if day not in logs:
            logs[day] = []
        if habit in logs[day]:
            logs[day].remove(habit)
        else:
            logs[day].append(habit)
        save_data(self.data)
        self.show_today()

    def _progress_bar(self, done, total):
        bar_frame = tk.Frame(self.content, bg=COLORS["bg"])
        bar_frame.pack(fill="x", padx=24, pady=(0, 16))

        pct = int(done / total * 100) if total else 0
        tk.Label(bar_frame, text=f"{done}/{total} выполнено  ({pct}%)",
                 font=FONT_SMALL, bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(anchor="w")

        canvas = tk.Canvas(bar_frame, height=8, bg=COLORS["undone"],
                           highlightthickness=0)
        canvas.pack(fill="x", pady=4)
        canvas.update_idletasks()
        w = canvas.winfo_width()
        if w > 1:
            canvas.create_rectangle(0, 0, int(w * pct / 100), 8,
                                     fill=COLORS["accent2"], outline="")

    # ── Stats view ────────────────────────────────────────────────────────────

    def show_stats(self):
        self._clear_content()
        self._set_active_nav("Статистика")

        tk.Label(self.content, text="Статистика", font=FONT_TITLE,
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(24, 6), padx=24, anchor="w")
        tk.Label(self.content, text="Выполнение за последние 7 дней", font=FONT,
                 bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(padx=24, anchor="w")

        days = last_n_days(7)

        if not self.data["habits"]:
            tk.Label(self.content, text="Нет привычек.", font=FONT,
                     bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(pady=40)
            return

        # Header row with dates
        header = tk.Frame(self.content, bg=COLORS["bg"])
        header.pack(fill="x", padx=24, pady=(20, 4))
        tk.Label(header, text="Привычка", font=FONT_BOLD, width=22, anchor="w",
                 bg=COLORS["bg"], fg=COLORS["text_dim"]).grid(row=0, column=0, sticky="w")
        for i, d in enumerate(days):
            short = d[8:]  # just the day number
            tk.Label(header, text=short, font=FONT_SMALL, width=3, anchor="center",
                     bg=COLORS["bg"], fg=COLORS["text_dim"]).grid(row=0, column=i+1, padx=2)
        tk.Label(header, text="%", font=FONT_BOLD, width=5, anchor="center",
                 bg=COLORS["bg"], fg=COLORS["text_dim"]).grid(row=0, column=8, padx=6)

        # Habit rows
        for habit in self.data["habits"]:
            row_frame = tk.Frame(self.content, bg=COLORS["panel"],
                                 highlightbackground=COLORS["border"], highlightthickness=1)
            row_frame.pack(fill="x", padx=24, pady=3)

            tk.Label(row_frame, text=habit, font=FONT, width=22, anchor="w",
                     bg=COLORS["panel"], fg=COLORS["text"]).grid(row=0, column=0, padx=10, pady=8)

            done_count = 0
            for i, d in enumerate(days):
                done = habit in self.data["logs"].get(d, [])
                if done:
                    done_count += 1
                cell_color = COLORS["done"] if done else COLORS["undone"]
                cell = tk.Label(row_frame, text="●", font=FONT_SMALL, width=3,
                                bg=COLORS["panel"], fg=cell_color)
                cell.grid(row=0, column=i+1, padx=2)

            pct = int(done_count / 7 * 100)
            tk.Label(row_frame, text=f"{pct}%", font=FONT_BOLD, width=5,
                     bg=COLORS["panel"],
                     fg=COLORS["done"] if pct >= 70 else COLORS["text_dim"]).grid(row=0, column=8, padx=6)

    # ── Manage habits view ────────────────────────────────────────────────────

    def show_manage(self):
        self._clear_content()
        self._set_active_nav("Привычки")

        tk.Label(self.content, text="Управление привычками", font=FONT_TITLE,
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(24, 6), padx=24, anchor="w")

        # Add button
        add_frame = tk.Frame(self.content, bg=COLORS["bg"])
        add_frame.pack(fill="x", padx=24, pady=(8, 16))

        self.new_habit_var = tk.StringVar()
        entry = tk.Entry(add_frame, textvariable=self.new_habit_var, font=FONT,
                         bg=COLORS["panel"], fg=COLORS["text"],
                         insertbackground=COLORS["text"],
                         relief="flat", bd=0)
        entry.pack(side="left", fill="x", expand=True, ipady=8, ipadx=8)
        entry.bind("<Return>", lambda e: self._add_habit())

        tk.Button(add_frame, text="+ Добавить", font=FONT_BOLD,
                  bg=COLORS["accent"], fg="white", bd=0, padx=16, pady=8,
                  relief="flat", cursor="hand2",
                  command=self._add_habit).pack(side="left", padx=(8, 0))

        # Habit list
        if not self.data["habits"]:
            tk.Label(self.content, text="Список пуст. Добавьте первую привычку!",
                     font=FONT, bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(pady=40)
            return

        for habit in self.data["habits"]:
            row = tk.Frame(self.content, bg=COLORS["panel"],
                           highlightbackground=COLORS["border"], highlightthickness=1)
            row.pack(fill="x", padx=24, pady=4)

            tk.Label(row, text=habit, font=FONT, bg=COLORS["panel"],
                     fg=COLORS["text"]).pack(side="left", padx=14, pady=10)

            tk.Button(row, text="✕", font=FONT, bd=0, cursor="hand2",
                      bg=COLORS["panel"], fg=COLORS["danger"],
                      activebackground=COLORS["panel"],
                      relief="flat",
                      command=lambda h=habit: self._delete_habit(h)).pack(side="right", padx=12)

    def _add_habit(self):
        name = self.new_habit_var.get().strip()
        if not name:
            return
        if name in self.data["habits"]:
            messagebox.showwarning("Уже есть", f'Привычка "{name}" уже существует.')
            return
        self.data["habits"].append(name)
        save_data(self.data)
        self.show_manage()

    def _delete_habit(self, habit):
        if messagebox.askyesno("Удалить?", f'Удалить привычку "{habit}"?'):
            self.data["habits"].remove(habit)
            # Убираем из логов
            for day_logs in self.data["logs"].values():
                if habit in day_logs:
                    day_logs.remove(habit)
            save_data(self.data)
            self.show_manage()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = HabitApp()
    app.mainloop()
