@echo off
if not exist venv_build (
    python -m venv venv_build
)
call venv_build\Scripts\activate
pip install -r requirements.txt
pip install cx_Freeze pyinstaller
python setup_installer.py bdist_msi
