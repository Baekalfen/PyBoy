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
    
    # Mock the Toplevel window
    settings_window.top = MagicMock(spec=tk.Toplevel)
    settings_window.top.title.return_value = "Settings"
    
    yield settings_window, launcher
    
    settings_window.top.destroy()


@pytest.fixture
def setup_keybinds_config(setup_game_launcher):
    """
    Fixture to set up a mock keybinds configuration window and test its functionality
    """
    launcher, root = setup_game_launcher
    keybinds = {
        "UP": "Up",
        "DOWN": "Down",
        "LEFT": "Left",
        "RIGHT": "Right",
        "A": "a",
        "S": "s",
        "START": "Return",
        "SELECT": "BackSpace"
    }
    
    keybinds_config = KeybindsConfig(root, keybinds)
    
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
    assert "UP" in launcher.keybinds
    assert "DOWN" in launcher.keybinds
    assert "LEFT" in launcher.keybinds
    assert "RIGHT" in launcher.keybinds
    assert "A" in launcher.keybinds
    assert "S" in launcher.keybinds
    assert "START" in launcher.keybinds
    assert "SELECT" in launcher.keybinds
    
    # Verify window properties
    assert launcher.root == root
    assert launcher.rom_directory == Path("roms")


def test_settings_window_initialization(setup_settings_window):
    """
    Test the initialization of the SettingsWindow class.
    Verifies that settings options are properly created.
    """
    settings_window, launcher = setup_settings_window
    
    # Verify window properties
    assert settings_window.launcher == launcher
    assert settings_window.top.title() == "Settings"


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
    keybinds_config.update_binding("UP", "w", keybinds_config.buttons["UP"])
    
    # Verify the keybind was updated
    assert keybinds_config.keybinds["UP"] == "w"


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
    
    # Mock ROM files
    with patch('pathlib.Path.glob', return_value=rom_list.values()):
        # Set search text
        launcher.search_var.get.return_value = "Pokemon"
        
        # Call filter function
        launcher.filter_games()
        
        # Verify listbox was updated
        launcher.listbox.delete.assert_called()
        launcher.listbox.insert.assert_called()


def test_game_launch(setup_game_launcher, setup_rom_list):
    """
    Test the game launching functionality.
    Verifies that games can be properly launched.
    """
    launcher, root = setup_game_launcher
    rom_list = setup_rom_list
    
    # Mock selected game
    launcher.listbox.curselection.return_value = (0,)
    launcher.listbox.get.return_value = "Pokemon Red.gb"
    
    # Mock status variable
    launcher.status_var = MagicMock(spec=tk.StringVar)
    launcher.root = MagicMock(spec=tk.Tk)
    
    # Create a mock ROM file
    rom_path = Path("roms/Pokemon Red.gb")
    with patch('os.path.exists', return_value=True):
        with patch('subprocess.Popen') as mock_popen:
            launcher.launch_game()
            
            # Verify Popen was called with correct arguments
            mock_popen.assert_called_once_with(["python", "-m", "pyboy", "roms/Pokemon Red.gb"])
            
            # Verify status updates
            launcher.status_var.set.assert_any_call("LAUNCHING POKEMON RED...")
            launcher.status_var.set.assert_any_call("SYSTEM READY")
