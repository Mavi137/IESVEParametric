import tkinter as tk
import tkinter.ttk as ttk


class StatusBar(tk.Frame):
    """Status bar widget with an integrated progress bar.

    Args:
        master (tk.Widget): The parent Widget.
        init_msg (str): The initial message for the status bar label.
    """
    def __init__(self, master, init_msg):
        tk.Frame.__init__(self, master)
        self.variable = tk.StringVar()
        self.label = tk.Label(
            self,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            textvariable=self.variable,
            padx=3,
            pady=3,
        )
        self.variable.set(init_msg)
        self.label.grid(row=0, column=0, sticky="we")
        self.grid_columnconfigure(0, weight=1)

        self.progress_val = tk.IntVar()
        self.progressbar = ttk.Progressbar(
            self,
            orient=tk.HORIZONTAL,
            maximum=100,
            length=150,
            mode="determinate",
            variable=self.progress_val,
        )
        self.progressbar.grid(row=0, column=1, sticky="nesw")
        self.progressbar.grid_columnconfigure(1, weight=0)
        self.grid(row=0, column=0, sticky="nesw")

    def set_message(self, message):
        self.variable.set(message)


class ThemedText(tk.Frame):
    """A variant of tk.Text styled to look like ttk.Entry.
    Wrapped in a class for brevity.

    Args:
        master (tk.Widget): The parent Widget.
        scrollbar (bool): Whether to include a scrollbar.
        tab (bool): Whether to override the tab key. Usually, in a text
            widget, the tab key inserts a tab character. This option
            overrides that behavior to focus the next widget.
    """
    def __init__(self, master, scrollbar=False, tab=False, *args, **kwargs):
        tk.Frame.__init__(self, master)
        self.text = tk.Text(self, font=("Segoe UI", 9), relief=tk.FLAT, insertwidth=1, highlightthickness=1, *args, **kwargs)
        self.text.grid(row=0, column=0, sticky='nsew')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        def on_enter(_):
            self.text.config(highlightbackground="#171717")

        def on_leave(_):
            self.text.config(highlightbackground="#7a7a7a")

        self.text.bind("<Enter>", on_enter)
        self.text.bind("<Leave>", on_leave)

        self.text.config(highlightcolor="#0078d7")
        self.text.config(highlightbackground="#7a7a7a")

        if scrollbar:
            self.scrollbar = tk.Scrollbar(self, command=self.text.yview)
            self.scrollbar.grid(row=0, column=1, sticky='nsew')
            self.text['yscrollcommand'] = self.scrollbar.set

        if tab:
            self.text.bind("<Tab>", self.focus_next_widget)

    @staticmethod
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return("break")

    def insert(self, *args, **kwargs):
        self.text.insert(*args, **kwargs)

    def get(self, *args, **kwargs):
        if args or kwargs:
            return self.text.get(*args, **kwargs)
        else:
            # default, get all text in the widget
            return self.text.get("1.0", tk.END)


class EditableGrid(tk.Frame):
    """A widget that creates a grid of tkinter Entries.
    These can be addressed individually or as whole columns or rows.
    Additionally, it can have an optional header row with Labels.
    """
    def __init__(self, master, x, y, width=20, headers=None):
        """Constructor.

        Args:
            master (tkinter.Widget): The parent widget.
            x (int): The amount of columns to be created.
            y (int): The amount of rows to be created.
            width (int, optional): The initial width of each Entry.
            Defaults to 20.
            headers (List[str], optional): The titles for each column.
            Defaults to None.
        """
        self.x, self.y = x, y
        self.vars = [[tk.StringVar() for column in range(x)] for row in range(y)]
        tk.Frame.__init__(self, master)
        self.entries = [
            [
                ttk.Entry(self, textvariable=self.vars[row][column], width=width)
                for column in range(x)
            ]
            for row in range(y)
        ]

        if headers is not None:
            offset = 1
            for column, header in enumerate(headers):
                lbl = ttk.Label(self, text=header)
                lbl.grid(row=0, column=column)
        else:
            offset = 0

        # Automatically expand to fill space
        for row in range(offset, y):
            self.grid_rowconfigure(row, weight=1)

        for column in range(x):
            self.grid_columnconfigure(column, weight=1)

        for row in range(y):
            for column in range(x):
                entry = self.entries[row][column]
                entry.grid(row=row + offset, column=column, sticky='nswe')

    def get(self, x, y):
        return self.vars[y][x].get()

    def set(self, x, y, value):
        return self.vars[y][x].set(value)

    def set_state(self, x, y, state):
        self.entries[y][x].config(state=state)

    def set_column_state(self, x, state):
        for y in range(self.y):
            self.set_state(x, y, state)

    def set_row_state(self, y, state):
        for x in range(self.x):
            self.set_state(x, y, state)

    def get_column(self, x):
        return [self.get(x, y) for y in range(self.y)]

    def get_row(self, y):
        return [self.get(x, y) for x in range(self.x)]

    def set_column(self, x, data):
        amount_to_set = min(self.y, len(data))
        for y in range(amount_to_set):
            self.set(x, y, data[y])

    def set_row(self, y, data):
        amount_to_set = min(self.x, len(data))
        for x in range(amount_to_set):
            self.set(x, y, data[x])
