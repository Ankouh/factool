from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {
    "packages": ["PyQt6", "keyboard", "win32gui", "win32con", "win32api", "win32process", "win32ui", "win32com"],
    "include_files": [
        "Loading.png",
        "LogoDofus.png",
        "LogoAnkama.png",
        "DiscordLogo.png",
        "file_version_info.txt"
    ],
}

setup(
    name="Kaio3",
    version="1.1.0",
    description="Gestionnaire de multicompte Dofus avec raccourcis clavier",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="Kaio3.exe",
            icon="LogoDofus.png",
        )
    ],
) 