import tkinter as tk
from tkinter import ttk
import os
import subprocess
from pathlib import Path
from tkinter import font

class GameBoyLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Boy ROM Launcher")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0C0C0C')
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('Hacker.TFrame', background='#0C0C0C')
        self.style.configure('Hacker.TButton',
                           background='#00FF00',
                           foreground='#000000',
                           font=('Courier', 12, 'bold'),
                           padding=10)
        self.style.configure('Hacker.TLabel',
                           background='#0C0C0C',
                           foreground='#00FF00',
                           font=('Courier', 12))
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20", style='Hacker.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_font = font.Font(family='Courier', size=24, weight='bold')
        title = tk.Label(main_frame,
                        text="GAME BOY LAUNCHER v1.0",
                        font=title_font,
                        fg='#00FF00',
                        bg='#0C0C0C')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create search box with custom styling
        search_frame = ttk.Frame(main_frame, style='Hacker.TFrame')
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        search_label = ttk.Label(search_frame,
                               text="SEARCH:",
                               style='Hacker.TLabel')
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_games)
        search_entry = tk.Entry(search_frame,
                              textvariable=self.search_var,
                              font=('Courier', 12),
                              bg='#1A1A1A',
                              fg='#00FF00',
                              insertbackground='#00FF00',  # Cursor color
                              relief=tk.FLAT,
                              width=50)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Stats frame
        self.stats_frame = ttk.Frame(main_frame, style='Hacker.TFrame')
        self.stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.stats_label = ttk.Label(self.stats_frame,
                                   text="LOADING ROMS...",
                                   style='Hacker.TLabel')
        self.stats_label.pack(side=tk.LEFT)
        
        # Create listbox with custom styling
        self.listbox = tk.Listbox(main_frame,
                                 width=70,
                                 height=20,
                                 font=('Courier', 12),
                                 bg='#1A1A1A',
                                 fg='#00FF00',
                                 selectmode=tk.SINGLE,
                                 selectbackground='#005500',
                                 selectforeground='#FFFFFF',
                                 relief=tk.FLAT)
        
        # Custom scrollbar
        scrollbar = tk.Scrollbar(main_frame,
                               orient=tk.VERTICAL,
                               command=self.listbox.yview,
                               width=20,
                               troughcolor='#1A1A1A',
                               bg='#333333')
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        scrollbar.grid(row=3, column=1, sticky=(tk.N, tk.S))
        
        # Control panel frame
        control_frame = ttk.Frame(main_frame, style='Hacker.TFrame')
        control_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        # Create launch button with custom styling
        launch_button = tk.Button(control_frame,
                                text="LAUNCH GAME",
                                command=self.launch_game,
                                font=('Courier', 14, 'bold'),
                                bg='#00FF00',
                                fg='#000000',
                                activebackground='#008800',
                                activeforeground='#FFFFFF',
                                relief=tk.FLAT,
                                padx=20,
                                pady=10)
        launch_button.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("SYSTEM READY")
        status_label = ttk.Label(main_frame,
                               textvariable=self.status_var,
                               style='Hacker.TLabel')
        status_label.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Double-click binding
        self.listbox.bind('<Double-Button-1>', lambda e: self.launch_game())
        
        # Load games
        self.games = []
        self.load_games()
    
    def load_games(self):
        roms_dir = Path("roms")
        if roms_dir.exists():
            for file in roms_dir.glob("*.gb"):
                self.games.append(file.name)
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
            subprocess.Popen(["python", "-m", "pyboy", f"roms/{game}"])
            self.status_var.set("SYSTEM READY")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameBoyLauncher(root)
    root.mainloop() 
