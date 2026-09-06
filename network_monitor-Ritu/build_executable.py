import PyInstaller.__main__
import sys

def build():
    print("Building Standalone Executable with PyInstaller...")
    
    # Determine the path separator for the current OS for PyInstaller data
    separator = ';' if sys.platform.startswith('win') else ':'

    PyInstaller.__main__.run([
        'app.py',
        '--name=NetworkMonitorSetup',
        '--onefile',
        '--clean',
        '--noconfirm',
        f'--add-data=templates{separator}templates',
        f'--add-data=static{separator}static',
    ])
    
    print("\n=======================================================")
    print("Build complete! Check the 'dist' folder for your executable.")
    print("=======================================================")

if __name__ == "__main__":
    build()
