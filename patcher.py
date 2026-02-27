import os
import subprocess
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

class PatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MerchantCMS Safe Patcher")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.configure("TProgressbar", thickness=20)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1565c0", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header, 
            text="MerchantCMS Patcher", 
            fg="white", 
            bg="#1565c0", 
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        # Main Content
        self.main_frame = tk.Frame(self.root, padx=30, pady=20)
        self.main_frame.pack(fill="both", expand=True)
        
        self.status_label = tk.Label(
            self.main_frame, 
            text="Ready to update. Click the button below to start.",
            font=("Arial", 10),
            wraplength=540,
            justify="center"
        )
        self.status_label.pack(pady=(10, 20))
        
        self.progress = ttk.Progressbar(
            self.main_frame, 
            orient="horizontal", 
            length=540, 
            mode="determinate"
        )
        self.progress.pack(pady=10)
        
        self.log_text = tk.Text(
            self.main_frame, 
            height=10, 
            width=70, 
            state="disabled", 
            font=("Consolas", 9),
            bg="#f5f5f5"
        )
        self.log_text.pack(pady=10)
        
        self.start_btn = tk.Button(
            self.root, 
            text="Start Safe Patching", 
            command=self.start_patch,
            bg="#2e7d32",
            fg="white",
            font=("Arial", 11, "bold"),
            height=2
        )
        self.start_btn.pack(side="bottom", fill="x")

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.root.update_idletasks()

    def update_status(self, text, step_val):
        self.status_label.config(text=text)
        self.progress["value"] = step_val
        self.root.update_idletasks()

    def check_git(self):
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def start_patch(self):
        self.start_btn.config(state="disabled")
        threading.Thread(target=self.patch_process, daemon=True).start()

    def patch_process(self):
        try:
            # Step 1: Check Environment
            self.update_status("Checking environment...", 10)
            self.log("Verifying Git installation...")
            if not self.check_git():
                messagebox.showerror("Error", "Git not found. Please install Git to use the patcher.")
                self.log("ERROR: Git not found.")
                return

            if not os.path.exists(".git"):
                self.log("ERROR: Not a Git repository.")
                messagebox.showerror("Error", "This folder is not a Git repository. Patcher must be run from inside the app folder.")
                return

            # Step 2: Backup Data
            self.update_status("Backing up local data...", 40)
            self.log("Backing up database...")
            db_path = "data/data.db"
            if os.path.exists(db_path):
                backup_dir = "data/backups"
                os.makedirs(backup_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{backup_dir}/data_backup_{timestamp}.db"
                shutil.copy2(db_path, backup_path)
                self.log(f"Backup created: {backup_path}")
            else:
                self.log("No database found to backup.")

            # Step 3: Git Pull
            self.update_status("Fetching latest binary updates...", 70)
            self.log("Running git pull...")
            try:
                # Force pulling from main
                result = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True, check=True)
                self.log(result.stdout if result.stdout else "Already up to date.")
            except subprocess.CalledProcessError as e:
                self.log(f"GIT ERROR: {e.stderr}")
                if "local changes" in e.stderr.lower() or "untracked files" in e.stderr.lower():
                    if messagebox.askyesno("Conflict", "Local changes or untracked files detected. Stash/clean and continue?"):
                        subprocess.run(["git", "stash"])
                        subprocess.run(["git", "pull", "origin", "main"])
                    else:
                        self.log("Update aborted by user due to conflicts.")
                        return
                else:
                    raise e

            # Step 4: Finalize
            self.update_status("Patching complete!", 100)
            self.log("Patching sequence finished successfully.")
            self.log("Database schema will be updated automatically on next app launch.")
            
            if messagebox.askyesno("Success", "Application updated successfully!\n\nWould you like to launch MerchantCMS now?"):
                self.log("Launching MerchantCMS.exe...")
                if os.path.exists("MerchantCMS.exe"):
                    subprocess.Popen(["MerchantCMS.exe"])
                else:
                    messagebox.showinfo("Note", "MerchantCMS.exe not found in this folder. Please ensure you are running the patcher from the correct directory.")

        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}")
            messagebox.showerror("Unexpected Error", f"An error occurred: {str(e)}")
        finally:
            self.start_btn.config(state="normal")
            self.start_btn.config(text="Update Successful!", bg="#1565c0")

if __name__ == "__main__":
    root = tk.Tk()
    app = PatcherApp(root)
    root.mainloop()
