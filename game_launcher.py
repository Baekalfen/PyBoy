import tkinter as tk
from tkinter import ttk
import subprocess
from pathlib import Path
from tkinter import font
import json
import sys


class KeybindsConfig:
    def __init__(self, parent, keybinds):
        self.top = tk.Toplevel(parent)
        self.top.title("Keybind Settings")
        self.top.geometry("300x500")
        self.top.configure(bg='#C5C1C2')

        self.keybinds = keybinds
        self.create_widgets()

    def create_widgets(self):
        self.buttons = {}
        self.top.grid_rowconfigure(0, minsize=25)

        row = 1
        for action, key in self.keybinds.items():
            tk.Label(self.top,
                     text=f"{action}:",
                     font=("Courier", 10, "bold"),
                     bg='#C5C1C2',
                     fg="#21298C",
                     anchor="e",
                     width=12).grid(row=row, column=0, padx=10, pady=5, sticky="e")

            btn = tk.Button(self.top,
                            text=key,
                            font=("Courier", 10, "bold"),
                            bg="grey",
                            fg="white",
                            width=10,
                            height=2,
                            command=lambda a=action: self.rebind_key(a))
            btn.grid(row=row, column=1, padx=10, pady=5)
            self.buttons[action] = btn
            row += 1

    def rebind_key(self, action):
        self.top.unbind("<KeyPress>")
        self.top.unbind("<Button>")

        def capture_key(event):
            new_key = event.keysym
            self.update_binding(action, new_key)

        def capture_mouse(event):
            new_mouse = f"Mouse{event.num}"
            self.update_binding(action, new_mouse)

        self.top.bind("<KeyPress>", capture_key)
        self.top.bind("<Button>", capture_mouse)

    def update_binding(self, action, new_binding):
        self.keybinds[action] = new_binding
        self.buttons[action].config(text=new_binding)
        self.top.unbind("<KeyPress>")
        self.top.unbind("<Button>")


class SettingsWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Settings")
        self.top.geometry("400x400")
        self.top.configure(bg='#C5C1C2')

        title = tk.Label(self.top,
                         text="Settings",
                         font=("Courier", 16, "bold"),
                         bg='#C5C1C2',
                         fg="#21298C")
        title.pack(pady=20)

        options = [
            "Change Keybindings",
            "Change ROM Directory",
            "Toggle Screen Recording",
            "Adjust Volume"
        ]

        for opt in options:
            btn = tk.Button(self.top,
                            text=opt,
                            font=("Courier", 10, "bold"),
                            bg="grey",
                            fg="black",
                            width=30,
                            height=2)
            btn.pack(pady=5)

class GameBoyLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Boy ROM Launcher")
        self.root.geometry("1000x700")
        self.root.configure(bg='#C5C1C2')

        self.keybinds = {
            "UP": "Up",
            "DOWN": "Down",
            "LEFT": "Left",
            "RIGHT": "Right",
            "A": "a",
            "S": "s",
            "START": "Return",
            "SELECT": "BackSpace",
        }

        self.style = ttk.Style()
        self.style.configure('Hacker.TFrame', background='#C5C1C2')
        self.style.configure('Hacker.TButton',
                             background='#00FF00',
                             foreground='#C5C1C2',
                             font=('Courier', 12, 'bold'),
                             padding=10)
        self.style.configure('Hacker.TLabel',
                             background='#C5C1C2',
                             foreground='#21298C',
                             font=('Courier', 12))

        main_frame = ttk.Frame(root, padding="20", style='Hacker.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_font = font.Font(family='Courier', size=24, weight='bold')
        title = tk.Label(main_frame,
                         text="GAME BOY LAUNCHER v1.0",
                         font=title_font,
                         fg='#21298C',
                         bg='#C5C1C2')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        search_frame = ttk.Frame(main_frame, style='Hacker.TFrame')
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        search_label = ttk.Label(search_frame, text="SEARCH:", style='Hacker.TLabel')
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.filter_games)
        search_entry = tk.Entry(search_frame,
                                textvariable=self.search_var,
                                font=('Courier', 12),
                                bg='#5D5A61',
                                fg='#C5C1C2',
                                insertbackground='#21298C',
                                relief=tk.FLAT,
                                width=50)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.stats_frame = ttk.Frame(main_frame, style='Hacker.TFrame')
        self.stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.stats_label = ttk.Label(self.stats_frame,
                                     text="LOADING ROMS...",
                                     style='Hacker.TLabel')
        self.stats_label.pack(side=tk.LEFT)

        self.listbox = tk.Listbox(main_frame,
                                  width=70,
                                  height=20,
                                  font=('Courier', 14, 'bold'),
                                  bg='#596708',
                                  fg='#21298C',
                                  selectmode=tk.SINGLE,
                                  selectbackground='#005500',
                                  selectforeground='#596708',
                                  relief=tk.FLAT)

        scrollbar = tk.Scrollbar(main_frame,
                                 orient=tk.VERTICAL,
                                 command=self.listbox.yview,
                                 width=20,
                                 troughcolor='#1A1A1A',
                                 bg='#333333')
        self.listbox.configure(yscrollcommand=scrollbar.set)

        self.listbox.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        scrollbar.grid(row=3, column=1, sticky=(tk.N, tk.S))

        control_frame = ttk.Frame(main_frame, style='Hacker.TFrame')
        control_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)

        launch_button = tk.Button(control_frame,
                                  text=f"LAUNCH\nGAME",
                                  command=self.launch_game,
                                  font=('Courier', 14, 'bold'),
                                  bg='#a61257',
                                  fg='#000000',
                                  activebackground='#008800',
                                  activeforeground='#FFFFFF',
                                  relief=tk.RAISED,
                                  width=6,
                                  height=3,
                                  bd=5,
                                  highlightthickness=0)
        launch_button.pack(side=tk.RIGHT, padx=10)

        center_buttons_frame = tk.Frame(control_frame, bg='#C5C1C2')
        center_buttons_frame.pack(expand=True, padx=(80, 0))

        settings_frame = tk.Frame(center_buttons_frame, bg='#C5C1C2')
        settings_frame.pack(side=tk.LEFT, padx=10)

        keybinds_frame = tk.Frame(center_buttons_frame, bg='#C5C1C2')
        keybinds_frame.pack(side=tk.LEFT, padx=10)

        settings_button = tk.Button(settings_frame,
                                    width=10,
                                    height=1,
                                    font=('Courier', 8, 'bold'),
                                    relief=tk.RAISED,
                                    bg="grey",
                                    fg="#21298C",
                                    command=self.open_settings_window)
        settings_button.pack()

        settings_label = tk.Label(settings_frame,
                                  text="Settings",
                                  font=('Courier', 8, 'bold'),
                                  bg='#C5C1C2',
                                  fg="#21298C")
        settings_label.pack(pady=(5, 0))

        keybind_button = tk.Button(keybinds_frame,
                                   width=10,
                                   height=1,
                                   font=('Courier', 8, 'bold'),
                                   relief=tk.RAISED,
                                   bg="grey",
                                   fg="#21298C",
                                   command=self.open_keybinds_window)
        keybind_button.pack()

        keybind_label = tk.Label(keybinds_frame,
                                 text="Keybinds",
                                 font=('Courier', 8, 'bold'),
                                 bg='#C5C1C2',
                                 fg="#21298C")
        keybind_label.pack(pady=(5, 0))

        self.status_var = tk.StringVar()
        self.status_var.set("SYSTEM READY")
        status_label = ttk.Label(main_frame,
                                 textvariable=self.status_var,
                                 style='Hacker.TLabel')
        status_label.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        self.listbox.bind('<Double-Button-1>', lambda e: self.launch_game())

        self.games = []
        self.load_games()

    def open_keybinds_window(self):
        KeybindsConfig(self.root, self.keybinds)

    def open_settings_window(self):
        SettingsWindow(self.root)

    def load_games(self):
        roms_dir = Path("roms")
        if roms_dir.exists():
            for file in roms_dir.glob("*.gb"):
                self.games.append(file.stem)
            self.games.sort()
            self.update_listbox()
            self.update_stats()

    def update_stats(self):
        self.stats_label.configure(text=f"TOTAL ROMS: {len(self.games)} | SELECTED: {len(self.listbox.curselection())}")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for game in self.games:
            self.listbox.insert(tk.END, f" {game}")
        self.update_stats()

    def filter_games(self, *args):
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        for game in self.games:
            if search_term in game.lower():
                self.listbox.insert(tk.END, f" {game}")
        self.update_stats()

    def launch_game(self):
        selection = self.listbox.curselection()
        if selection:
            game = self.listbox.get(selection[0]).strip()
            self.status_var.set(f"LAUNCHING: {game}")
            self.root.update()
            keybinds = json.dumps(self.keybinds)
            subprocess.Popen([sys.executable, "-m", "pyboy", f"roms/{game}.gb"])
            self.status_var.set("SYSTEM READY")


if __name__ == "__main__":
    root = tk.Tk()
    app = GameBoyLauncher(root)
    root.mainloop()
