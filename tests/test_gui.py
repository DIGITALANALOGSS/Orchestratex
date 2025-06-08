import pytest
import tkinter as tk
from tkinter import ttk
from PIL import Image
import os
import logging
from unittest.mock import Mock, patch
from gui.main import OrchestratexGUI

@pytest.fixture
def gui_app():
    """Fixture for GUI application."""
    root = tk.Tk()
    app = OrchestratexGUI(root)
    yield app
    root.destroy()

@pytest.fixture
def mock_image():
    """Fixture for mock image."""
    return Image.new('RGB', (100, 100), color='black')

def test_gui_initialization(gui_app):
    """Test GUI initialization."""
    assert gui_app.root.title() == "Orchestratex AEM"
    assert gui_app.root.geometry() == "1200x800"
    assert gui_app.root.cget('bg') == '#181818'

def test_load_assets_success(gui_app, mock_image):
    """Test successful asset loading."""
    with patch('PIL.Image.open', return_value=mock_image) as mock_open:
        gui_app.load_assets()
        mock_open.assert_called()
        assert gui_app.main_photo is not None
        assert gui_app.logo_photo is not None

def test_load_assets_failure(gui_app):
    """Test asset loading failure."""
    with patch('PIL.Image.open', side_effect=FileNotFoundError):
        gui_app.load_assets()
        assert gui_app.error_label.cget('text') != ""
        assert "Error loading assets" in gui_app.error_label.cget('text')

def test_menu_creation(gui_app):
    """Test menu creation."""
    assert gui_app.root.winfo_children()[0].winfo_class() == 'Menu'
    assert len(gui_app.root.winfo_children()[0].winfo_children()) > 0

def test_control_panel(gui_app):
    """Test control panel creation."""
    assert gui_app.start_button['state'] == 'normal'
    assert gui_app.stop_button['state'] == 'disabled'
    assert gui_app.reset_button['state'] == 'normal'

def test_progress_bar(gui_app):
    """Test progress bar functionality."""
    gui_app.progress['value'] = 50
    assert gui_app.progress['value'] == 50

def test_error_handling(gui_app):
    """Test error handling."""
    try:
        raise Exception("Test error")
    except Exception as e:
        gui_app.show_error(str(e))
        assert gui_app.error_label.cget('text') != ""
        assert "Test error" in gui_app.error_label.cget('text')

def test_file_operations(gui_app):
    """Test file operations."""
    with patch('tkinter.filedialog.askopenfilename', return_value='test.txt'):
        gui_app.open_file()
        assert gui_app.status_var.get() == "Opened: test.txt"

    with patch('tkinter.filedialog.asksaveasfilename', return_value='test.txt'), \
         patch('builtins.open', mock_open(read_data='test')) as mock_file:
        gui_app.save_file()
        mock_file.assert_called()

def test_logging(gui_app):
    """Test logging functionality."""
    with patch('logging.Logger.info') as mock_log:
        gui_app.status_var.set("Test status")
        mock_log.assert_called()

def test_cleanup(gui_app):
    """Test cleanup functionality."""
    with patch('os.path.exists', return_value=True), \
         patch('os.remove') as mock_remove:
        gui_app.cleanup()
        mock_remove.assert_called()

def test_exception_handling(gui_app):
    """Test exception handling."""
    with patch('sys.excepthook') as mock_excepthook:
        try:
            raise Exception("Test exception")
        except Exception:
            gui_app.handle_exception(*sys.exc_info())
            mock_excepthook.assert_called()
