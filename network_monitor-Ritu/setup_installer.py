import sys
import os
from cx_Freeze import setup, Executable

# Files and folders to include
include_files = ['templates/', 'static/', 'instance/']

# Packages to include (explicitly including hidden dynamic imports)
packages = [
    'flask', 'flask_sqlalchemy', 'werkzeug', 'apscheduler', 'sqlalchemy',
    'monitor', 'models', 'ping_engine', 'email_alerts', 'clear_devices', 'import_devices', 'webview'
]

# Build Options
build_exe_options = {
    'packages': packages,
    'include_files': include_files,
    'excludes': ['tkinter']
}

# Define MSI shortcut table for both Desktop and Start Menu
shortcut_table = [
    (
        "DesktopShortcut",              # Shortcut ID
        "DesktopFolder",                # Directory_ (Where the shortcut goes)
        "Network Monitor",              # Name of the shortcut
        "TARGETDIR",                    # Component_
        "[TARGETDIR]NetworkMonitor.exe",# Target
        None,                           # Arguments
        "Network Monitor Application",  # Description
        None,                           # Hotkey
        None,                           # Icon
        None,                           # IconIndex
        None,                           # ShowCmd
        "TARGETDIR"                     # WkDir (Working directory)
    ),
    (
        "StartMenuShortcut",            # Shortcut ID
        "ProgramMenuFolder",            # Directory_ (Start Menu)
        "Network Monitor",              # Name of the shortcut
        "TARGETDIR",                    # Component_
        "[TARGETDIR]NetworkMonitor.exe",# Target
        None,                           # Arguments
        "Network Monitor Application",  # Description
        None,                           # Hotkey
        None,                           # Icon
        None,                           # IconIndex
        None,                           # ShowCmd
        "TARGETDIR"                     # WkDir (Working directory)
    )
]

msi_data = {"Shortcut": shortcut_table}

# MSI Options: Install to AppData instead of Program Files so sqlite DB can be written to
bdist_msi_options = {
    'initial_target_dir': r'[LocalAppDataFolder]\NetworkMonitor',
    'upgrade_code': '{E4F49D0E-C24D-4A42-99FE-0275C9A4D3B0}',
    'data': msi_data
}

base = "gui" if sys.platform == "win32" else None 

# Define the Executable (without inline shortcut config to avoid conflicts with shortcut_table)
executable = Executable(
    script="app.py",
    base=base,
    target_name="NetworkMonitor.exe",
    icon="static/Logo.ico"
)

# Setup
setup(
    name="NetworkMonitor",
    version="1.5",
    description="Network Monitor Application",
    author="Ritu",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=[executable]
)
