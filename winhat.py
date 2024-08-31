import tkinter as tk
import subprocess
import os
from tkinter import simpledialog, messagebox

class TerminalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WINHAT")
        self.root.geometry("800x600")
        self.root.configure(bg="black")

        # Create a Text widget that looks like a terminal
        self.text_widget = tk.Text(self.root, bg="black", fg="white", insertbackground="green",
                                   font=("Courier New", 12), wrap="word", borderwidth=0)
        self.text_widget.pack(expand=True, fill='both')
        self.text_widget.bind("<Return>", self.execute_command)
        self.text_widget.bind("<Key>", self.on_key_press)
        self.text_widget.bind("<BackSpace>", self.disable_backspace)
        self.text_widget.bind("<Control-c>", self.disable_ctrl_c)

        self.insert_prompt()

    def insert_prompt(self):
        # Get current working directory and update prompt
        current_directory = os.getcwd()
        self.prompt = f"{current_directory}> "
        self.text_widget.insert(tk.END, self.prompt)
        self.text_widget.mark_set(tk.INSERT, tk.END)  # Move cursor to the end

    def execute_command(self, event):
        command_line = self.text_widget.get("end-1c linestart", "end-1c")
        command = command_line[len(self.prompt):]  # Extract command after the prompt

        if command.lower() == "cls":
            self.clear_screen()
            return "break"

        if command.lower() in ["exit", "quit"]:
            self.root.quit()
            return

        self.text_widget.insert(tk.END, "\n")  # Move to next line
        try:
            # Handle 'cd' command
            if command.startswith("cd "):
                path = command.split(" ", 1)[1]
                if path == "..":
                    self.change_directory_up()
                else:
                    self.change_directory(path)
            # Handle 'touch' command
            elif command.startswith("touch "):
                filename = command.split(" ", 1)[1]
                self.create_file(filename)
            # Handle 'edit' command
            elif command.startswith("edit "):
                filename = command.split(" ", 1)[1]
                self.edit_file(filename)
            else:
                # Execute other commands
                result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
                if result.stdout:
                    self.text_widget.insert(tk.END, result.stdout, "output")
                if result.stderr:
                    self.text_widget.insert(tk.END, result.stderr, "error")

        except Exception as e:
            self.text_widget.insert(tk.END, f"Error: {str(e)}", "error")

        self.text_widget.insert(tk.END, "\n")
        self.insert_prompt()

        # Prevent the newline character from adding extra lines
        return "break"

    def clear_screen(self):
        self.text_widget.delete("1.0", tk.END)
        self.insert_prompt()

    def change_directory(self, path):
        try:
            os.chdir(path)
        except FileNotFoundError:
            self.text_widget.insert(tk.END, "The system cannot find the path specified.\n", "error")
        except NotADirectoryError:
            self.text_widget.insert(tk.END, "The system cannot find the path specified.\n", "error")
        except PermissionError:
            self.text_widget.insert(tk.END, "Access is denied.\n", "error")

    def change_directory_up(self):
        try:
            os.chdir("..")
        except FileNotFoundError:
            self.text_widget.insert(tk.END, "The system cannot find the path specified.\n", "error")
        except PermissionError:
            self.text_widget.insert(tk.END, "Access is denied.\n", "error")

    def create_file(self, filename):
        try:
            with open(filename, 'w') as file:
                pass  # Create an empty file
            self.text_widget.insert(tk.END, f"File '{filename}' created successfully.\n", "output")
        except Exception as e:
            self.text_widget.insert(tk.END, f"Error: {str(e)}", "error")

    def edit_file(self, filename):
        if not os.path.exists(filename):
            self.text_widget.insert(tk.END, f"File '{filename}' does not exist.\n", "error")
            return

        editor_window = tk.Toplevel(self.root)
        editor_window.title(f"Editing {filename}")
        editor_window.geometry("800x600")

        text_editor = tk.Text(editor_window, bg="black", fg="green", insertbackground="green",
                              font=("Courier New", 12), wrap="word")
        text_editor.pack(expand=True, fill='both')

        # Load file content
        with open(filename, 'r') as file:
            text_editor.insert(tk.END, file.read())

        def save_file():
            with open(filename, 'w') as file:
                file.write(text_editor.get("1.0", tk.END))
            messagebox.showinfo("Save", f"File '{filename}' saved successfully.")

        save_button = tk.Button(editor_window, text="Save", command=save_file)
        save_button.pack()

    def on_key_press(self, event):
        if event.keysym in ["Left", "Right", "Up", "Down"]:
            return
        if self.text_widget.index(tk.INSERT) == self.text_widget.index(tk.END):
            return
        if event.keysym in ["BackSpace", "Delete"]:
            return "break"
    
    def disable_backspace(self, event):
        if self.text_widget.index(tk.INSERT) == self.text_widget.index(tk.END):
            return "break"

    def disable_ctrl_c(self, event):
        return "break"

if __name__ == "__main__":
    root = tk.Tk()
    app = TerminalApp(root)
    root.mainloop()
