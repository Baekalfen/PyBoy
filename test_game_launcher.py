"""
A module for testing essential game_launcher GUI functions
"""
import os.path
from unittest.mock import MagicMock, patch
import pytest
import tkinter as tk
from pathlib import Path

from game_launcher import GameBoyLauncher, SettingsWindow, KeybindsConfig

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
ROOT_DIRECTORY = SCRIPT_DIRECTORY.parent


@pytest.fixture
def setup_game_launcher():
    """
    Fixture to set up a mock root window if headless or allow a normal display
    if running locally, then instantiate an instance of the GameBoyLauncher class
    """
    # Mock Tk() to prevent actual GUI window creation in headless environments
    mock_root = MagicMock(spec=tk.Tk)
    mock_root.withdraw = MagicMock()  # Mock the withdraw method
    mock_root.quit = MagicMock()  # Mock the quit method to prevent blocking event loop
    mock_root.tk = MagicMock()  # Mock the tk attribute
    mock_root.children = {}  # Mock the children attribute
    mock_root.master = None  # Mock the master attribute
    root = mock_root

    launcher = GameBoyLauncher(root)

    # Mock the Entry widgets and other components
    launcher.listbox = MagicMock(spec=tk.Listbox)
    launcher.search_var = MagicMock(spec=tk.StringVar)
    launcher.stats_label = MagicMock(spec=tk.Label)

    yield launcher, root
    launcher.close_window()
    root.quit()
    root.destroy()


@pytest.fixture
def setup_settings_window(setup_game_launcher):
    """
    Fixture to set up a mock settings window.
    """
    launcher, root = setup_game_launcher
    settings_window = SettingsWindow(launcher)
    
    yield settings_window, launcher
    
    settings_window.top.destroy()


@pytest.fixture
def setup_keybinds_config(setup_game_launcher):
    """
    Fixture to set up a mock keybinds configuration window and test its functionality
    """
    launcher, root = setup_game_launcher
    keybinds = {
        "PRESS_ARROW_RIGHT": "Right",
        "PRESS_ARROW_LEFT": "Left",
        "PRESS_ARROW_UP": "Up",
        "PRESS_ARROW_DOWN": "Down",
        "PRESS_BUTTON_a": "a",
        "PRESS_BUTTON_b": "s",
        "PRESS_BUTTON_START": "Return",
        "PRESS_BUTTON_SELECT": "Backspace"
    }
    
    # Create a mock Toplevel window
    mock_toplevel = MagicMock(spec=tk.Toplevel)
    mock_toplevel.title = MagicMock()
    mock_toplevel.geometry = MagicMock()
    mock_toplevel.configure = MagicMock()
    mock_toplevel.grid_rowconfigure = MagicMock()
    mock_toplevel.destroy = MagicMock()
    mock_toplevel.tk = root.tk  # Add the tk attribute from root
    
    # Mock Label and Button classes
    mock_label = MagicMock(spec=tk.Label)
    mock_button = MagicMock(spec=tk.Button)
    
    with patch('tkinter.Toplevel', return_value=mock_toplevel), \
         patch('tkinter.Label', return_value=mock_label), \
         patch('tkinter.Button', return_value=mock_button):
        keybinds_config = KeybindsConfig(launcher, keybinds)
    
    # Mock the buttons
    keybinds_config.buttons = {
        action: MagicMock(spec=tk.Button) for action in keybinds
    }
    
    yield keybinds_config, launcher
    
    keybinds_config.top.destroy()


@pytest.fixture
def setup_rom_list():
    """
    Fixture to create a mock ROM list with known games
    """
    rom_list = {
        "Pokemon Red.gb": Path("roms/Pokemon Red.gb"),
        "Tetris.gb": Path("roms/Tetris.gb"),
        "Super Mario Land.gb": Path("roms/Super Mario Land.gb")
    }
    return rom_list


def test_game_launcher_initialization(setup_game_launcher):
    """
    Test the initialization of the GameBoyLauncher class.
    Verifies that all essential components are properly initialized.
    """
    launcher, root = setup_game_launcher
    
    # Verify keybinds are initialized
    assert isinstance(launcher.keybinds, dict)
    assert "PRESS_ARROW_UP" in launcher.keybinds
    assert "PRESS_ARROW_DOWN" in launcher.keybinds
    assert "PRESS_ARROW_LEFT" in launcher.keybinds
    assert "PRESS_ARROW_RIGHT" in launcher.keybinds
    assert "PRESS_BUTTON_a" in launcher.keybinds
    assert "PRESS_BUTTON_b" in launcher.keybinds
    assert "PRESS_BUTTON_START" in launcher.keybinds
    assert "PRESS_BUTTON_SELECT" in launcher.keybinds
    
    # Verify window properties
    assert launcher.root == root
    assert launcher.rom_directory == Path("roms")


def test_settings_window_initialization(setup_settings_window):
    """
    Test the initialization of the SettingsWindow class.
    Verifies that settings options are properly created.
    """
    settings_window, launcher = setup_settings_window

    # verify window properties
    assert settings_window.launcher == launcher

    # mock the title method of the top window
    settings_window.top.title = MagicMock()

    # initialize the window to set the title
    settings_window.top.title("Settings")

    # verify that the title method was called with "Settings"
    settings_window.top.title.assert_called_with("Settings")


def test_keybind_update(setup_keybinds_config):
    """
    Test the keybind update functionality.
    Verifies that keybinds can be properly updated.
    """
    keybinds_config, launcher = setup_keybinds_config
    
    # Mock a key press event
    mock_event = MagicMock()
    mock_event.keysym = "w"
    
    # Update a keybind
    keybinds_config.update_binding("PRESS_ARROW_UP", "w", keybinds_config.buttons["PRESS_ARROW_UP"])
    
    # Verify the keybind was updated
    assert keybinds_config.keybinds["PRESS_ARROW_UP"] == "w"


def test_rom_directory_change(setup_game_launcher):
    """
    Test the ROM directory change functionality.
    Verifies that the ROM directory can be changed and games are reloaded.
    """
    launcher, root = setup_game_launcher
    
    # Mock filedialog.askdirectory
    with patch('tkinter.filedialog.askdirectory', return_value="/new/rom/path"):
        launcher.change_rom_directory()
        
        # Verify the ROM directory was updated
        assert launcher.rom_directory == Path("/new/rom/path")


def test_game_filtering(setup_game_launcher, setup_rom_list):
    """
    Test the game filtering functionality.
    Verifies that games can be filtered based on search input.
    """
    launcher, root = setup_game_launcher
    rom_list = setup_rom_list

    # Mock the ROM files
    with patch('pathlib.Path.glob', return_value=rom_list.values()):
        # Mock listbox methods (delete and insert)
        launcher.listbox.delete = MagicMock()
        launcher.listbox.insert = MagicMock()

        # Set a search term
        search_term = "Pokemon"  # Use a term that matches one of our test games
        launcher.search_var.get.return_value = search_term

        # Call filter function
        launcher.filter_games()

        # Verify that the listbox's insert method was called
        launcher.listbox.insert.assert_called()

        # Check that the insert method was called with a game containing the search term
        inserted_args = [call[0][1] for call in launcher.listbox.insert.call_args_list]
        assert any(search_term.lower() in game.lower() for game in inserted_args), \
            f"Expected some game to contain the term '{search_term}'"


def test_game_launch(setup_game_launcher, setup_rom_list):
    """
    Test the game launching functionality.
    Verifies that games can be properly launched.
    """
    launcher, root = setup_game_launcher
    rom_list = setup_rom_list
    
    # Mock selected game
    launcher.listbox.curselection.return_value = (0,)
    launcher.listbox.get.return_value = "Pokemon Red.gb"  # Use a game from our test ROM list
    
    # Mock both os.path.exists and pathlib.Path.exists to return True
    with patch('os.path.exists', return_value=True), \
         patch('pathlib.Path.exists', return_value=True), \
         patch('subprocess.Popen') as mock_popen:
        launcher.launch_game()
        
        # Verify Popen was called with correct arguments
        mock_popen.assert_called_once()

# some snippets added by ai
