import tkinter as tk
from tkinter import ttk

from doubly_linked_list import DoublyLinkedList
from flashcards_data import INITIAL_CARDS

FONT = "Helvetica"

COLORS = {
    "background": "#1e1e2e",
    "card": "#2a2a3d",
    "shadow": "#141420",
    "text": "#cdd6f4",
    "muted": "#a6adc8",
    "blue": "#89b4fa",
    "green": "#a6e3a1",
    "red": "#f38ba8",
    "yellow": "#f9e2af",
    "slate": "#6c7a96",
    "disabled": "#34344a",
    "disabled_text": "#6c6c85",
    "dark_text": "#1e1e2e",
    "light_text": "#ffffff",
}


def blend(hex_color, target, factor):
    channels = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(c + (target - c) * factor) for c in channels]
    return "#" + "".join(f"{value:02x}" for value in mixed)


def lighten(hex_color, factor=0.25):
    return blend(hex_color, 255, factor)


def darken(hex_color, factor=0.25):
    return blend(hex_color, 0, factor)


def rounded_points(x1, y1, x2, y2, r):
    return [
        x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1,
        x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r,
        x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2,
        x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r,
        x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1,
    ]


class ActionButton(tk.Label):
    def __init__(self, parent, text, color, command, text_color):
        super().__init__(
            parent,
            text=text,
            bg=color,
            fg=text_color,
            font=(FONT, 14, "bold"),
            padx=18,
            pady=12,
            cursor="hand2",
        )
        self.base_color = color
        self.hover_color = lighten(color)
        self.press_color = darken(color)
        self.text_color = text_color
        self.command = command
        self.enabled = True
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_enter(self, event):
        if self.enabled:
            self.configure(bg=self.hover_color)

    def on_leave(self, event):
        if self.enabled:
            self.configure(bg=self.base_color)

    def on_press(self, event):
        if self.enabled:
            self.configure(bg=self.press_color)

    def on_release(self, event):
        if not self.enabled:
            return
        inside = (
            0 <= event.x <= self.winfo_width()
            and 0 <= event.y <= self.winfo_height()
        )
        self.configure(bg=self.hover_color if inside else self.base_color)
        if inside:
            self.command()

    def set_enabled(self, enabled):
        self.enabled = enabled
        if enabled:
            self.configure(
                bg=self.base_color, fg=self.text_color, cursor="hand2"
            )
        else:
            self.configure(
                bg=COLORS["disabled"],
                fg=COLORS["disabled_text"],
                cursor="arrow",
            )


class CardView(tk.Canvas):
    def __init__(self, parent):
        super().__init__(
            parent, bg=COLORS["background"], highlightthickness=0
        )
        self.tag_text = ""
        self.body_text = ""
        self.accent = COLORS["blue"]
        self.bind("<Configure>", lambda event: self.redraw())

    def show(self, tag_text, body_text, accent):
        self.tag_text = tag_text
        self.body_text = body_text
        self.accent = accent
        self.redraw()

    def redraw(self):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 50 or height < 50:
            return
        margin = 16
        offset = 8
        left = margin
        top = margin
        right = width - margin - offset
        bottom = height - margin - offset
        self.create_polygon(
            rounded_points(
                left + offset, top + offset, right + offset, bottom + offset, 28
            ),
            smooth=True,
            fill=COLORS["shadow"],
            outline="",
        )
        self.create_polygon(
            rounded_points(left, top, right, bottom, 28),
            smooth=True,
            fill=COLORS["card"],
            outline=self.accent,
            width=3,
        )
        self.create_text(
            left + 34,
            top + 36,
            text=self.tag_text,
            anchor="w",
            fill=self.accent,
            font=(FONT, 12, "bold"),
        )
        font_size = 24 if len(self.body_text) <= 90 else 18
        self.create_text(
            (left + right) / 2,
            (top + bottom) / 2 + 12,
            text=self.body_text,
            width=right - left - 90,
            justify="center",
            fill=COLORS["text"],
            font=(FONT, font_size, "bold"),
        )


class AddCardDialog(tk.Toplevel):
    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Add Card")
        self.configure(bg=COLORS["background"])
        self.resizable(False, False)
        self.transient(parent)
        self.build_form()
        self.center_on(parent, 540, 440)
        self.grab_set()
        self.question_entry.focus_set()

    def center_on(self, parent, width, height):
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{max(x, 0)}+{max(y, 0)}")

    def build_form(self):
        frame = ttk.Frame(self, style="App.TFrame", padding=28)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="New Card", style="Heading.TLabel").pack(
            anchor="w", pady=(0, 16)
        )
        ttk.Label(frame, text="Question", style="Field.TLabel").pack(
            anchor="w"
        )
        self.question_entry = ttk.Entry(
            frame, style="Field.TEntry", font=(FONT, 14)
        )
        self.question_entry.pack(fill="x", pady=(4, 14))
        ttk.Label(frame, text="Answer", style="Field.TLabel").pack(anchor="w")
        self.answer_text = tk.Text(
            frame,
            height=5,
            wrap="word",
            font=(FONT, 14),
            bg=COLORS["card"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            padx=10,
            pady=10,
            highlightthickness=2,
            highlightbackground=COLORS["slate"],
            highlightcolor=COLORS["blue"],
        )
        self.answer_text.pack(fill="x", pady=(4, 8))
        self.error_label = ttk.Label(frame, text="", style="Error.TLabel")
        self.error_label.pack(anchor="w", pady=(0, 8))
        buttons = ttk.Frame(frame, style="App.TFrame")
        buttons.pack(fill="x")
        buttons.columnconfigure((0, 1), weight=1, uniform="dialog")
        save_button = ActionButton(
            buttons,
            "Save",
            COLORS["green"],
            self.save,
            COLORS["dark_text"],
        )
        save_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        cancel_button = ActionButton(
            buttons,
            "Cancel",
            COLORS["slate"],
            self.destroy,
            COLORS["light_text"],
        )
        cancel_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def save(self):
        question = self.question_entry.get().strip()
        answer = self.answer_text.get("1.0", "end").strip()
        if not question or not answer:
            self.error_label.configure(text="Please fill in both fields.")
            return
        self.on_save(question, answer)
        self.destroy()


class MemoCardApp:
    def __init__(self, root):
        self.root = root
        self.cards = DoublyLinkedList()
        self.showing_answer = False
        for item in INITIAL_CARDS:
            self.cards.append(item["question"], item["answer"])
        self.configure_window()
        self.configure_styles()
        self.build_header()
        self.build_card()
        self.build_controls()
        self.refresh()

    def configure_window(self):
        self.root.title("MemoCard")
        self.root.geometry("860x660")
        self.root.minsize(720, 580)
        self.root.configure(bg=COLORS["background"])

    def configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        background = COLORS["background"]
        style.configure("App.TFrame", background=background)
        style.configure(
            "TitleBlue.TLabel",
            background=background,
            foreground=COLORS["blue"],
            font=(FONT, 34, "bold"),
        )
        style.configure(
            "TitleGreen.TLabel",
            background=background,
            foreground=COLORS["green"],
            font=(FONT, 34, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=background,
            foreground=COLORS["muted"],
            font=(FONT, 13),
        )
        style.configure(
            "Counter.TLabel",
            background=background,
            foreground=COLORS["text"],
            font=(FONT, 18, "bold"),
        )
        style.configure(
            "CounterFlash.TLabel",
            background=background,
            foreground=COLORS["yellow"],
            font=(FONT, 18, "bold"),
        )
        style.configure(
            "Heading.TLabel",
            background=background,
            foreground=COLORS["blue"],
            font=(FONT, 22, "bold"),
        )
        style.configure(
            "Field.TLabel",
            background=background,
            foreground=COLORS["muted"],
            font=(FONT, 12, "bold"),
        )
        style.configure(
            "Error.TLabel",
            background=background,
            foreground=COLORS["red"],
            font=(FONT, 12, "bold"),
        )
        style.configure(
            "Field.TEntry",
            fieldbackground=COLORS["card"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"],
            bordercolor=COLORS["slate"],
            lightcolor=COLORS["slate"],
            darkcolor=COLORS["slate"],
            padding=8,
        )
        style.map(
            "Field.TEntry",
            bordercolor=[("focus", COLORS["blue"])],
            lightcolor=[("focus", COLORS["blue"])],
            darkcolor=[("focus", COLORS["blue"])],
        )

    def build_header(self):
        header = ttk.Frame(self.root, style="App.TFrame")
        header.pack(pady=(24, 0))
        title = ttk.Frame(header, style="App.TFrame")
        title.pack()
        ttk.Label(title, text="Memo", style="TitleBlue.TLabel").pack(
            side="left"
        )
        ttk.Label(title, text="Card", style="TitleGreen.TLabel").pack(
            side="left"
        )
        ttk.Label(
            header,
            text="Study smarter with a doubly linked list",
            style="Subtitle.TLabel",
        ).pack(pady=(0, 10))
        self.counter_label = ttk.Label(header, style="Counter.TLabel")
        self.counter_label.pack()

    def build_card(self):
        self.card_view = CardView(self.root)
        self.card_view.pack(fill="both", expand=True, padx=40, pady=(12, 12))

    def build_controls(self):
        controls = ttk.Frame(self.root, style="App.TFrame")
        controls.pack(fill="x", padx=40, pady=(0, 30))
        controls.columnconfigure(tuple(range(5)), weight=1, uniform="controls")
        dark = COLORS["dark_text"]
        self.prev_button = ActionButton(
            controls, "Previous", COLORS["slate"], self.on_prev,
            COLORS["light_text"],
        )
        self.flip_button = ActionButton(
            controls, "Flip", COLORS["yellow"], self.on_flip, dark
        )
        self.next_button = ActionButton(
            controls, "Next", COLORS["blue"], self.on_next, dark
        )
        self.delete_button = ActionButton(
            controls, "Delete", COLORS["red"], self.on_delete, dark
        )
        self.add_button = ActionButton(
            controls, "Add Card", COLORS["green"], self.on_add, dark
        )
        buttons = [
            self.prev_button,
            self.flip_button,
            self.next_button,
            self.delete_button,
            self.add_button,
        ]
        for column, button in enumerate(buttons):
            button.grid(row=0, column=column, sticky="ew", padx=6)

    def refresh(self):
        current = self.cards.get_current()
        empty = self.cards.is_empty()
        if empty:
            self.card_view.show(
                "EMPTY",
                "No cards left.\nPress Add Card to create a new one.",
                COLORS["muted"],
            )
        elif self.showing_answer:
            self.card_view.show("ANSWER", current.answer, COLORS["green"])
        else:
            self.card_view.show("QUESTION", current.question, COLORS["blue"])
        self.counter_label.configure(
            text=f"Card {self.cards.get_position()} of {self.cards.size}"
        )
        self.prev_button.set_enabled(not empty and current.prev is not None)
        self.next_button.set_enabled(not empty and current.next is not None)
        self.flip_button.set_enabled(not empty)
        self.delete_button.set_enabled(not empty)

    def flash_counter(self):
        self.counter_label.configure(style="CounterFlash.TLabel")
        self.root.after(
            300, lambda: self.counter_label.configure(style="Counter.TLabel")
        )

    def on_prev(self):
        self.cards.prev_card()
        self.showing_answer = False
        self.refresh()
        self.flash_counter()

    def on_next(self):
        self.cards.next_card()
        self.showing_answer = False
        self.refresh()
        self.flash_counter()

    def on_flip(self):
        self.showing_answer = not self.showing_answer
        self.refresh()

    def on_delete(self):
        self.cards.delete_current()
        self.showing_answer = False
        self.refresh()
        self.flash_counter()

    def on_add(self):
        AddCardDialog(self.root, self.handle_new_card)

    def handle_new_card(self, question, answer):
        self.cards.append(question, answer)
        self.refresh()
        self.flash_counter()
