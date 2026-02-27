"""
Build script for compiling the application with PyInstaller.
This script will create a standalone executable in the dist/ folder.
"""
import os
import subprocess
import shutil
import sys

# Clean previous builds (skip if locked)
try:
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
except Exception as e:
    print(f"Warning: Could not clean previous build: {e}")
    print("Continuing anyway...")

# Get Tcl/Tk paths for proper bundling
import tkinter
tcl_lib = os.path.dirname(tkinter.__file__)

# PyInstaller command with proper Tkinter support
cmd = [
    "pyinstaller",
    "--noconfirm",
    "--onedir",
    "--windowed",
    "--icon", "assets/images/Strife.ico",
    "--add-data", "assets;assets",
    "--collect-all", "tkinter",
    "--name", "MerchantCMS",
    "main.py"
]

print("Building application with PyInstaller...")
print(" ".join(cmd))
subprocess.run(cmd, check=True)

print("\n" + "="*50)
print("Build complete!")
print("Executable location: dist/MerchantCMS/MerchantCMS.exe")
print("="*50)
print("\nIMPORTANT: Copy the 'data' folder to dist/MerchantCMS/ before running!")

