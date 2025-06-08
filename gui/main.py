import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import logging
from datetime import datetime
import json
import threading
import queue
import sys
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gui.log'),
        logging.StreamHandler()
    ]
)

# --- Constants ---
PROJECT_NAME = "Orchestratex AEM"
WINDOW_SIZE = "1200x800"
BACKGROUND_COLOR = "#181818"
TEXT_COLOR = "#00ffe7"
BUTTON_COLOR = "#0066cc"
ERROR_COLOR = "#ff0000"
SUCCESS_COLOR = "#00ff00"
WARNING_COLOR = "#ffff00"

# --- File paths ---
CONFIG_FILE = "config.json"
LOG_FILE = "orchestratex.log"
TEMP_DIR = "temp"

# --- Error Handling ---
class OrchestratexError(Exception):
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details

# --- File paths ---
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
MAIN_IMAGE_PATH = os.path.join(ASSETS_DIR, "main_image.jpg")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")

# --- GUI Class ---
class OrchestratexGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_widgets()
        self.setup_logging()
        self.load_assets()

    def setup_window(self):
        self.root.title(PROJECT_NAME)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BACKGROUND_COLOR)
        self.root.resizable(True, True)

    def setup_widgets(self):
        # Project name label
        self.project_label = tk.Label(
            self.root,
            text=PROJECT_NAME,
            font=("Helvetica", 28, "bold"),
            fg=TEXT_COLOR,
            bg=BACKGROUND_COLOR
        )
        self.project_label.place(relx=0.5, rely=0.06, anchor="center")

        # Main content frame
        self.content_frame = ttk.Frame(self.root, padding="20")
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Menu
        self.create_menu()

        # Control panel
        self.create_control_panel()

        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        self.progress.place(relx=0.5, rely=0.95, anchor="center")

        # Error display
        self.error_label = tk.Label(
            self.root,
            text="",
            fg=ERROR_COLOR,
            bg=BACKGROUND_COLOR
        )
        self.error_label.place(relx=0.5, rely=0.98, anchor="center")

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Settings", command=self.open_settings)
        tools_menu.add_command(label="Logs", command=self.view_logs)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.open_docs)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    def create_control_panel(self):
        # Control panel frame
        control_frame = ttk.LabelFrame(
            self.root,
            text="Controls",
            padding="5"
        )
        control_frame.place(relx=0.05, rely=0.05, relwidth=0.4, relheight=0.15)

        # Buttons
        self.start_button = ttk.Button(
            control_frame,
            text="Start",
            command=self.start_process
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            control_frame,
            text="Stop",
            command=self.stop_process,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(
            control_frame,
            text="Reset",
            command=self.reset_process
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

    def open_file(self):
        filename = filedialog.askopenfilename(
            title="Open File",
            filetypes=(
                ("All files", "*.*"),
                ("Text files", "*.txt"),
                ("Image files", "*.jpg *.png")
            )
        )
        if filename:
            self.status_var.set(f"Opened: {os.path.basename(filename)}")
            logging.info(f"File opened: {filename}")

    def save_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save File",
            defaultextension=".txt",
            filetypes=(
                ("Text files", "*.txt"),
                ("All files", "*.*")
            )
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.get_current_state())
                self.status_var.set(f"Saved: {os.path.basename(filename)}")
                logging.info(f"File saved: {filename}")
            except Exception as e:
                self.show_error(f"Save error: {str(e)}")

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.configure(bg=BACKGROUND_COLOR)

    def view_logs(self):
        logs_window = tk.Toplevel(self.root)
        logs_window.title("Logs")
        logs_window.geometry("800x600")
        
        text = tk.Text(logs_window, bg="black", fg="white")
        text.pack(fill=tk.BOTH, expand=True)
        
        try:
            with open(LOG_FILE, 'r') as f:
                text.insert(tk.END, f.read())
        except Exception as e:
            text.insert(tk.END, f"Error reading logs: {str(e)}")

    def open_docs(self):
        import webbrowser
        webbrowser.open("https://github.com/yourusername/orchestratex")

    def show_about(self):
        messagebox.showinfo(
            "About",
            f"{PROJECT_NAME}\nVersion 1.0\n\nDeveloped by Your Company\n\nCopyright 2025"
        )

    def start_process(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.status_var.set("Processing...")
        threading.Thread(target=self._process, daemon=True).start()

    def stop_process(self):
        self.status_var.set("Stopping...")
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

    def reset_process(self):
        self.progress['value'] = 0
        self.status_var.set("Ready")
        self.error_label.config(text="")

    def _process(self):
        try:
            # Simulate processing
            for i in range(100):
                if not self.root.winfo_exists():
                    break
                self.progress['value'] = i
                self.root.update()
                time.sleep(0.1)
            self.status_var.set("Completed")
            self.stop_button.config(state=tk.DISABLED)
            self.start_button.config(state=tk.NORMAL)
        except Exception as e:
            self.show_error(f"Processing error: {str(e)}")

    def show_error(self, message):
        self.error_label.config(text=message)
        logging.error(message)
        messagebox.showerror("Error", message)

    def get_current_state(self):
        """Get the current application state for saving."""
        state = {
            "status": self.status_var.get(),
            "progress": self.progress['value']
        }
        return json.dumps(state, indent=2)

    def setup_logging(self):
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )

        # Add exception hook
        sys.excepthook = self.handle_exception

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.error("Uncaught exception",
                     exc_info=(exc_type, exc_value, exc_traceback))
        self.show_error(f"Unexpected error: {str(exc_value)}")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                self.cleanup()
            except Exception as e:
                logging.error(f"Error during cleanup: {str(e)}")
            finally:
                self.root.destroy()

    def cleanup(self):
        """Cleanup resources before exit."""
        # Clean up temporary files
        if os.path.exists(TEMP_DIR):
            for file in os.listdir(TEMP_DIR):
                try:
                    os.remove(os.path.join(TEMP_DIR, file))
                except:
                    logging.warning(f"Failed to remove temporary file: {file}")
            os.rmdir(TEMP_DIR)

    def load_assets(self):
        try:
            # Create assets directory if it doesn't exist
            if not os.path.exists(ASSETS_DIR):
                os.makedirs(ASSETS_DIR)
                raise OrchestratexError("Assets directory created. Please add images.")

            # Load main image
            if not os.path.exists(MAIN_IMAGE_PATH):
                raise OrchestratexError("Main image not found")

            main_img = Image.open(MAIN_IMAGE_PATH)
            main_img = main_img.resize((700, 700), Image.Resampling.LANCZOS)
            self.main_photo = ImageTk.PhotoImage(main_img)
            
            # Create main image label
            self.main_label = tk.Label(
                self.content_frame,
                image=self.main_photo,
                bg=BACKGROUND_COLOR
            )
            self.main_label.pack()

            # Load logo
            if not os.path.exists(LOGO_PATH):
                raise OrchestratexError("Logo not found")

            logo_img = Image.open(LOGO_PATH)
            logo_img = logo_img.resize((120, 120), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            
            # Create logo label
            self.logo_label = tk.Label(
                self.root,
                image=self.logo_photo,
                bg=BACKGROUND_COLOR,
                borderwidth=0
            )
            self.logo_label.place(relx=0.97, rely=0.97, anchor="se")

            self.status_var.set("Application loaded successfully")
            logging.info("GUI assets loaded successfully")

        except OrchestratexError as e:
            self.show_error(f"Error loading assets: {str(e)}")
            if e.details:
                logging.error(f"Additional details: {e.details}")
        except Exception as e:
            self.show_error(f"Unexpected error loading assets: {str(e)}")
            logging.error(f"Unexpected error loading assets: {str(e)}", 
                         exc_info=True)

    def load_assets(self):
        try:
            # Load main image
            main_img = Image.open(MAIN_IMAGE_PATH)
            main_img = main_img.resize((700, 700), Image.Resampling.LANCZOS)
            self.main_photo = ImageTk.PhotoImage(main_img)
            
            # Create main image label
            self.main_label = tk.Label(
                self.content_frame,
                image=self.main_photo,
                bg=BACKGROUND_COLOR
            )
            self.main_label.pack()

            # Load logo
            logo_img = Image.open(LOGO_PATH)
            logo_img = logo_img.resize((120, 120), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            
            # Create logo label
            self.logo_label = tk.Label(
                self.root,
                image=self.logo_photo,
                bg=BACKGROUND_COLOR,
                borderwidth=0
            )
            self.logo_label.place(relx=0.97, rely=0.97, anchor="se")

            self.status_var.set("Application loaded successfully")
            logging.info("GUI assets loaded successfully")

        except Exception as e:
            self.status_var.set(f"Error loading assets: {str(e)}")
            logging.error(f"Error loading assets: {str(e)}")
            messagebox.showerror("Error", f"Failed to load assets: {str(e)}")

    def setup_logging(self):
        self.log_text = tk.Text(
            self.root,
            height=10,
            width=50,
            bg="black",
            fg="white",
            wrap=tk.WORD
        )
        self.log_text.place(relx=0.5, rely=0.9, anchor="center")
        
        # Redirect logging to Text widget
        class TextHandler(logging.Handler):
            def emit(self, record):
                msg = self.format(record)
                self.widget.configure(state='normal')
                self.widget.insert(tk.END, f"{msg}\n")
                self.widget.configure(state='disabled')
                self.widget.see(tk.END)

        text_handler = TextHandler()
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        text_handler.widget = self.log_text
        logging.getLogger('').addHandler(text_handler)

    def start(self):
        try:
            self.root.mainloop()
        except Exception as e:
            self.show_error(f"Application error: {str(e)}")
            logging.critical(f"Fatal error in application: {str(e)}", exc_info=True)
            sys.exit(1)

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.cleanup()
        except Exception as e:
            logging.error(f"Error in destructor: {str(e)}")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

# --- Test Cases ---
import unittest

class TestOrchestratexGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.gui = OrchestratexGUI(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_window_creation(self):
        self.assertEqual(self.root.title(), PROJECT_NAME)
        self.assertEqual(self.root.geometry(), WINDOW_SIZE)

    def test_widget_creation(self):
        self.assertIsNotNone(self.gui.project_label)
        self.assertIsNotNone(self.gui.main_label)
        self.assertIsNotNone(self.gui.logo_label)

    def test_status_update(self):
        test_status = "Test status message"
        self.gui.status_var.set(test_status)
        self.assertEqual(self.gui.status_var.get(), test_status)

if __name__ == "__main__":
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOrchestratexGUI)
    unittest.TextTestRunner(verbosity=2).run(suite)

    # Start GUI if tests pass
    root = tk.Tk()
    app = OrchestratexGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.start()
