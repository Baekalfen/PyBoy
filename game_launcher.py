import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
from pathlib import Path
from tkinter import font
import json
import os
from functools import partial

KEYBINDS = {
    "PRESS_ARROW_RIGHT": "Right",
    "PRESS_ARROW_LEFT": "Left",
    "PRESS_ARROW_UP": "Up",
    "PRESS_ARROW_DOWN": "Down",
    "PRESS_BUTTON_a": "a",
    "PRESS_BUTTON_b": "s",
    "PRESS_BUTTON_START": "Return",
    "PRESS_BUTTON_SELECT": "Backspace",
}

tkinter_to_sdl2 = {
    'a': 'SDLK_a', 'b': 'SDLK_b', 'c': 'SDLK_c', 'd': 'SDLK_d',
    'e': 'SDLK_e', 'f': 'SDLK_f', 'g': 'SDLK_g', 'h': 'SDLK_h',
    'i': 'SDLK_i', 'j': 'SDLK_j', 'k': 'SDLK_k', 'l': 'SDLK_l',
    'm': 'SDLK_m', 'n': 'SDLK_n', 'o': 'SDLK_o', 'p': 'SDLK_p',
    'q': 'SDLK_q', 'r': 'SDLK_r', 's': 'SDLK_s', 't': 'SDLK_t',
    'u': 'SDLK_u', 'v': 'SDLK_v', 'w': 'SDLK_w', 'x': 'SDLK_x',
    'y': 'SDLK_y', 'z': 'SDLK_z',
    '0': 'SDLK_0', '1': 'SDLK_1', '2': 'SDLK_2', '3': 'SDLK_3',
    '4': 'SDLK_4', '5': 'SDLK_5', '6': 'SDLK_6', '7': 'SDLK_7',
    '8': 'SDLK_8', '9': 'SDLK_9',
    'space': 'SDLK_SPACE', 'Tab': 'SDLK_TAB', 'Caps_Lock': 'SDLK_CAPSLOCK',
    'Return': 'SDLK_RETURN', 'Shift': 'SDLK_LSHIFT', 'Control': 'SDLK_LCTRL',
    'Alt_L': 'SDLK_LALT', 'Alt_R': 'SDLK_RALT', 'BackSpace': 'SDLK_BACKSPACE',
    'Left': 'SDLK_LEFT', 'Right': 'SDLK_RIGHT', 'Up': 'SDLK_UP', 'Down': 'SDLK_DOWN',
    'Mouse1': 'SDL_BUTTON_LEFT', 'Mouse2': 'SDL_BUTTON_MIDDLE', 'Mouse3': 'SDL_BUTTON_RIGHT',
    'comma': 'SDLK_COMMA', 'minus': 'SDLK_MINUS', 'equal': 'SDLK_EQUALS',
    'bracketleft': 'SDLK_LEFTBRACKET', 'bracketright': 'SDLK_RIGHTBRACKET',
    'backslash': 'SDLK_BACKSLASH', 'semicolon': 'SDLK_SEMICOLON',
    'apostrophe': 'SDLK_QUOTE', 'period': 'SDLK_PERIOD', 'slash': 'SDLK_SLASH',
    'colon': 'SDLK_COLON'
}


class KeybindsConfig:
    def __init__(self, parent, keybinds):
        self.parent = parent
        self.top = tk.Toplevel(parent.root)
        self.top.title("Keybind Settings")

        # Get the position of the parent window
        parent_x = self.parent.root.winfo_x()
        parent_y = self.parent.root.winfo_y()

        # Adjust the window position based on the parent window's position
        offset_x = 60  # Offset from the parent window's left edge
        offset_y = 60  # Offset from the parent window's top edge

        self.top.geometry(f"300x550+{parent_x+offset_x}+{parent_y+offset_y}")
        self.top.configure(bg='#C5C1C2')

        self.keybinds = keybinds
        self.create_widgets()

    def create_widgets(self):
        self.buttons = {}
        self.top.grid_rowconfigure(0, minsize=25)

        row = 1
        for action, key in self.keybinds.items():
            # Label for each action
            label = action.replace("PRESS_ARROW_", "").replace("PRESS_BUTTON_", "").upper()
            tk.Label(self.top,
                     text=label,
                     font=("Courier", 10, "bold"),
                     bg='#C5C1C2',
                     fg="#21298C",
                     anchor="e",
                     width=12).grid(row=row, column=0, padx=10, pady=5, sticky="e")

            # Creating button for each keybind
            btn = tk.Button(self.top,
                            text=key,
                            font=("Courier", 10, "bold"),
                            bg="grey",
                            fg="black",
                            width=15,
                            height=2)
            # Using partial to pass both the action and the button
            btn.config(command=partial(self.rebind_key, action, btn))
            btn.grid(row=row, column=1, padx=10, pady=5)

            self.buttons[action] = btn
            row += 1

        # Adding Save Button at the bottom
        save_button = tk.Button(self.top,
                                text="SAVE",
                                font=("Courier", 14, "bold"),
                                bg="#a61257",
                                fg="black",
                                width=5,
                                height=2,
                                relief=tk.RAISED,
                                bd=5,
                                highlightthickness=0,
                                command=self.save_keybinds)
        save_button.grid(row=row, column=0, columnspan=2, pady=10)

    def save_keybinds(self):
        """ Function to save the keybinds to remapped_keys. """
        has_unbound = False
        for action, binding in self.keybinds.items():
            if binding == "UNBOUND":
                has_unbound = True
                btn = self.buttons.get(action)
                if btn:
                    self.flash_button(btn)

        if has_unbound:
            return  # Prevent saving if any are unbound

        if self.keybinds != KEYBINDS:
            self.parent.remapped_keys = self.keybinds.copy()
        self.top.destroy()

    def flash_button(self, btn, count=6):
        def toggle(i):
            # Toggle the button color based on index i
            current_bg = btn.cget("bg")
            btn.config(bg="#a61257" if current_bg != "#a61257" else "grey")

            # If there are more flashes left, schedule the next one
            if i < count - 1:
                self.top.after(200, toggle, i + 1)  # Schedule next toggle after 200ms

        toggle(0)  # Start with 0

    def rebind_key(self, action, btn):
        # Highlight the button by changing its background color
        btn.config(bg="#a61257")  # Highlight the button
        btn.config(state="disabled")  # Disable the button to prevent further clicks

        self.top.unbind("<KeyPress>")
        self.top.unbind("<Button>")

        def capture_key(event):
            new_key = event.keysym
            if is_valid_key(new_key):
                self.update_binding(action, new_key, btn)

        def capture_mouse(event):
            new_mouse = f"Mouse{event.num}"
            self.update_binding(action, new_mouse, btn)

        self.top.bind("<KeyPress>", capture_key)
        self.top.bind("<Button>", capture_mouse)

    def update_binding(self, action, new_binding, btn):
        # Check if this binding is already used
        for other_action, bound_key in self.keybinds.items():
            if other_action != action and bound_key == new_binding:
                # Unbind the key from the other action
                self.keybinds[other_action] = "UNBOUND"

                # Update the button label for the old binding
                other_btn = self.buttons.get(other_action)
                if other_btn:
                    other_btn.config(text="UNBOUND")

        # Update the keybinding and the button text
        self.keybinds[action] = new_binding
        btn.config(text=new_binding)

        # Reset button state and color
        btn.config(bg="grey", state="normal")  # Reset color and re-enable the button
        self.top.unbind("<KeyPress>")
        self.top.unbind("<Button>")


class SettingsWindow:
    def __init__(self, launcher):
        self.launcher = launcher
        self.top = tk.Toplevel(launcher.root)
        self.top.title("Settings")
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
            # "Toggle Screen Recording",
        ]

        # Get the position of the parent window
        parent_x = self.launcher.root.winfo_x()
        parent_y = self.launcher.root.winfo_y()

        # Adjust the window position based on the parent window's position
        offset_x = 30  # Offset from the parent window's left edge
        offset_y = 30  # Offset from the parent window's top edge

        # Set the size and position of the SettingsWindow relative to the parent window
        window_height = 100 + len(options) * 50
        self.top.geometry(f"400x{window_height}+{parent_x + offset_x}+{parent_y + offset_y}")

        # Create buttons and pack them
        for opt in options:
            opt_to_func = opt.lower().replace(" ", "_")
            opt_btn = tk.Button(self.top,
                                text=opt,
                                font=("Courier", 10, "bold"),
                                bg="grey",
                                fg="black",
                                width=30,
                                height=2,
                                command=lambda opt_to_func=opt_to_func: getattr(self.launcher, opt_to_func)())
            opt_btn.pack(pady=5)


class GameBoyLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Boy ROM Launcher")
        self.root.geometry("1000x700")
        self.root.configure(bg='#C5C1C2')
        self.rom_directory = Path("roms")

        self.keybinds = KEYBINDS.copy()
        self.remapped_keys = {}
        self.open_windows = {}

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

        self.listbox.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

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

        power_button_frame = tk.Frame(center_buttons_frame, bg='#C5C1C2')
        power_button_frame.pack(side=tk.LEFT, padx=10)

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

        power_button = tk.Button(power_button_frame,
                                 width=10,
                                 height=1,
                                 font=('Courier', 8, 'bold'),
                                 relief=tk.RAISED,
                                 bg="grey",
                                 fg="#21298C",
                                 command=self.close_window)
        power_button.pack()

        power_label = tk.Label(power_button_frame,
                               text="Exit",
                               font=('Courier', 8, 'bold'),
                               bg='#C5C1C2',
                               fg="#21298C")
        power_label.pack(pady=(5, 0))

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

    def close_window(self):
        self.root.destroy()

    def change_keybindings(self):
        if "keybinds" not in self.open_windows or not self.open_windows["keybinds"].top.winfo_exists():
            keybinds_window = KeybindsConfig(self, self.keybinds)
            self.open_windows["keybinds"] = keybinds_window

            def on_close():
                keybinds_window.top.destroy()
                if "keybinds" in self.open_windows:
                    del self.open_windows["keybinds"]

            keybinds_window.top.protocol("WM_DELETE_WINDOW", on_close)
        else:
            self.open_windows["keybinds"].top.lift()

    def change_rom_directory(self):
        directory = filedialog.askdirectory(title="Select a Directory")
        if directory:
            self.rom_directory = Path(directory)
            self.load_games()

    def open_settings_window(self):
        # Check if the settings window is already open
        if "settings" not in self.open_windows or not self.open_windows["settings"].top.winfo_exists():
            settings_window = SettingsWindow(self)
            self.open_windows["settings"] = settings_window  # Store the window

            # When the window is closed, remove it from open_windows
            def on_close():
                settings_window.top.destroy()
                if "settings" in self.open_windows:
                    del self.open_windows["settings"]

            settings_window.top.protocol("WM_DELETE_WINDOW", on_close)
        else:
            # Focus the existing window
            self.open_windows["settings"].top.lift()

    def load_games(self):
        self.games.clear()
        roms_dir = self.rom_directory
        if roms_dir.exists():
            for file in roms_dir.glob("*.gb"):
                self.games.append(file.name)
            self.games.sort()
            self.update_listbox()
            self.update_stats()

    def update_stats(self):
        self.stats_label.configure(text=f"AVAILABLE ROMS: {len(self.games)}")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for game in self.games:
            game = game.replace('.gb', '')
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
        """Launch the selected game with PyBoy"""
        selection = self.listbox.curselection()
        if selection:
            game = self.listbox.get(selection[0]).strip()
            # Remove .gb extension if it exists in the game name
            game = game.replace('.gb', '')
            rom_path = f"roms/{game}.gb"
            print(f"Attempting to launch game with path: {rom_path}")

            # Check if the ROM file exists
            if not os.path.exists(rom_path):
                print(f"Error: ROM file not found: {rom_path}")
                self.status_var.set("ROM NOT FOUND")
                return

            self.status_var.set(f"LAUNCHING {game.upper()}...")
            self.root.update()
            keybinds = json.dumps(self.keybinds)
            try:
                subprocess.Popen(["python", "-m", "pyboy", rom_path])
                # subprocess.Popen(["python", "-m", "pyboy", f"roms/{game}.gb", "-k", keybinds])
                self.status_var.set("SYSTEM READY")
            except Exception as e:
                print(f"Error launching game: {e}")
                self.status_var.set("LAUNCH FAILED")


def install_linux_dependencies():
    pass


def install_windows_dependencies():
    install_package("pip", "install")
    install_package("wheel", "install")
    install_package("setuptools", "install")
    install_package("pyboy", "install")


def install_package(package, install_cmd):
    """Check if a package is installed and install it if not."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "show", package],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{package} is already installed.")
    except subprocess.CalledProcessError:
        print(f"{package} is not installed. Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} has been successfully installed.")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}. Please install it manually.")
            return False
    return True
    # """Check if a package is installed and install it if not."""
    # try:
    #     subprocess.check_call([sys.executable, "-m", "pip", "show", package])
    #     print(f"{package} is already installed.")
    # except subprocess.CalledProcessError:
    #     print(f"{package} is not installed. Installing {package}...")
    #     try:
    #         subprocess.check_call([sys.executable, "-m", "pip", install_cmd, package])
    #         print(f"{package} has been successfully installed.")
    #     except subprocess.CalledProcessError:
    #         print(f"Failed to install {package}. Please install it manually.")
    #         sys.exit(1)


def install_mac_dependencies():
    install_package("pip", "install")
    install_package("wheel", "install")
    install_package("setuptools", "install")
    install_package("pyboy", "install")


def check_and_install_dependencies():
    # Ensure pip is available
    try:
        import pip
    except ImportError:
        print("pip not found. Trying to bootstrap...")
        try:
            import ensurepip
            ensurepip.bootstrap()
        except Exception as e:
            print("Failed to bootstrap pip:", e)
            return False

    for package in ["setuptools", "wheel", "pyboy"]:
        if not install_package(package):
            return False
    return True
    # os_type = platform.system().lower()
    #
    # if os_type == "linux":
    #     install_linux_dependencies()
    # elif os_type == "darwin":
    #     install_mac_dependencies()
    # elif os_type == "windows":
    #     install_windows_dependencies()


def is_valid_key(key):
    return key in tkinter_to_sdl2


# def tkinter_to_sdl2_key(tkinter_key):
#     # Convert Tkinter key name to SDL2 key name
#     sdl2_key = tkinter_to_sdl2.get(tkinter_key, None)
#     if sdl2_key is None:
#         print(f"Warning: No SDL2 mapping found for Tkinter key: {tkinter_key}")
#     return sdl2_key


if __name__ == "__main__":
    # check_and_install_dependencies()
    root = tk.Tk()
    app = GameBoyLauncher(root)
    root.mainloop()


# some code snippets added by ai
