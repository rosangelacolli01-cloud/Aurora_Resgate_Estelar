"""Cria executável com: python setup.py build (requer cx_Freeze)."""
from pathlib import Path
from cx_Freeze import Executable, setup

PASTA = Path(__file__).resolve().parent

setup(
    name="Aurora Resgate Estelar",
    version="1.0.0",
    description="Jogo 2D em Pygame — adaptação de IronManV2",
    options={
        "build_exe": {
            "packages": ["pygame", "pyttsx3", "recursos"],
            "include_files": [(str(PASTA / "bases"), "bases")],
            "includes": ["recursos.trabalho"],
        }
    },
    executables=[Executable("main.py", base="gui" if __import__("sys").platform == "win32" else None,
                            target_name="AuroraResgateEstelar")],
)
