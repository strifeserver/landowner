# Compiling MerchantCMS and Patcher

This document outlines the procedures for compiling the MerchantCMS application and its associated Patcher utility. These instructions are intended for developers and AI assistants needing to rebuild the project artifacts.

## Prerequisites

Ensure you have the following installed:

- **Python 3.x**
- **pip** (Python package installer)

### Install Dependencies

Before compiling, install the required Python packages:

```bash
pip install -r requirements.txt
```

Key dependencies include:

- `pyinstaller`: The build tool used for compilation.
- `bcrypt`, `Pillow`, `Jinja2`: Application dependencies.
- `google-auth`, `google-api-python-client`: For Google Sheets integration.
- `tkinter`: Required for the GUI (usually included with Python).

---

## 1. Building MerchantCMS (Main Application)

### Method A: automated Build (Recommended)

The easiest way to build the application is using the provided batch script. this script handles cleaning previous builds, running PyInstaller, and **crucially**, copying the required `data` directory.

Run `rebuild.bat` from the command line:

```bat
rebuild.bat
```

**What this script does:**

1.  Terminates any running instances of `MerchantCMS.exe`.
2.  Removes `build/` and `dist/` directories to ensure a clean build.
3.  Runs `pyinstaller MerchantCMS.spec`.
4.  Copies the `data/` directory to `dist/MerchantCMS/data/`.

### Method B: Manual Build

If you need to run PyInstaller manually (e.g., for debugging the build process), follow these steps:

1.  **Clean previous builds:**
    ```bat
    rmdir /s /q build dist
    ```
2.  **Run PyInstaller:**
    ```bat
    pyinstaller MerchantCMS.spec
    ```
3.  **Copy Data Directory:**
    - **Action:** Copy the `data` folder from the project root.
    - **Destination:** Paste it into `dist/MerchantCMS/`.
    - _Note: The application will fail to start if the `data` folder is missing._

### Output

The compiled executable will be located at:
`dist/MerchantCMS/MerchantCMS.exe`

---

## 2. Building MerchantCMS Patcher

The Patcher is a standalone utility for updating the application. It is built as a single-file executable.

### Build Command

Run `build_patcher.bat`:

```bat
build_patcher.bat
```

**What this script does:**

1.  Cleans `build_patcher/` and `dist_patcher/` directories.
2.  Runs PyInstaller with the arguments:
    - `--onefile`: Bundles everything into a single `.exe`.
    - `--windowed`: No console window.
    - Target script: `patcher.py`.

### Output

The compiled patcher will be located at:
`dist_patcher/MerchantCMSPatcher.exe`

---

## Build Configuration Details

### MerchantCMS.spec

- **Hidden Imports**: The application uses dynamic imports for controllers and models. These are explicitly listed in `hiddenimports` within the `.spec` file to ensure PyInstaller includes them.
- **Assets**: The `assets` and `migrations` folders are bundled via the `datas` configuration.
- **Tkinter**: `collect_all('tkinter')` is used to ensure all Tcl/Tk dependencies are correctly bundled.
- **Icon**: The application icon is set to `assets/images/Strife.ico`.

### Troubleshooting

- **Missing Modules**: If the application crashes with an `ImportError` or `ModuleNotFoundError`, check `MerchantCMS.spec` and ensure the missing module is listed in `hiddenimports`.
- **"Failed to execute script..."**: This generic error often points to missing data files. Verify that the `data` folder exists in the `dist/MerchantCMS/` directory.
