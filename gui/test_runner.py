import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import queue
import os

class TestRunnerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Orchestratex Test Runner")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create output text area
        self.output_text = scrolledtext.ScrolledText(
            main_frame,
            width=80,
            height=20,
            wrap=tk.WORD
        )
        self.output_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Run All Tests", command=self.run_all_tests).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Run Performance Tests", command=self.run_performance_tests).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Run Security Tests", command=self.run_security_tests).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Run Edge Cases", command=self.run_edge_cases).grid(row=0, column=3, padx=5)
        
        # Configure grid weights
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Create queue for thread-safe updates
        self.queue = queue.Queue()
        
    def run_command(self, command):
        """Run a command and capture output."""
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.queue.put(output.strip())
        
        rc = process.poll()
        self.queue.put(f"Command completed with return code: {rc}")
        return rc
        
    def update_output(self):
        """Update output text from queue."""
        try:
            while True:
                line = self.queue.get_nowait()
                self.output_text.insert(tk.END, line + "\n")
                self.output_text.see(tk.END)
        except queue.Empty:
            pass
        
        self.root.after(100, self.update_output)
        
    def run_all_tests(self):
        """Run all tests."""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Starting all tests...\n")
        self.run_command("python -m tests.setup_test_environment")
        
    def run_performance_tests(self):
        """Run performance tests."""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Starting performance tests...\n")
        self.run_command("python -m tests.additional_test_scenarios --performance")
        
    def run_security_tests(self):
        """Run security tests."""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Starting security tests...\n")
        self.run_command("python -m tests.additional_test_scenarios --security")
        
    def run_edge_cases(self):
        """Run edge case tests."""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Starting edge case tests...\n")
        self.run_command("python -m tests.additional_test_scenarios --edge")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestRunnerGUI(root)
    root.mainloop()
