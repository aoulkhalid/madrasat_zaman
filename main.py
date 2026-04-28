#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║   MADRASAT ZAMAN v3 — Tournoi 4 Équipes              ║
║   PyQt5 · OOP · MVC · Audio · Plein écran           ║
║   Lancement : python main.py                         ║
╚══════════════════════════════════════════════════════╝
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _install_deps():
    required = {"PyQt5": "PyQt5", "PIL": "Pillow", "pygame": "pygame"}
    missing  = []
    for mod, pkg in required.items():
        try: __import__(mod)
        except ImportError: missing.append(pkg)
    if missing:
        import subprocess
        print(f"📦 Installation : {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                               "--quiet"] + missing)

_install_deps()

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QFont

from config                         import QSS, APP_TITLE
from controllers.tournament_controller import TournamentController
from audio.manager                  import AudioManager
from utils.asset_generator          import generate_all

from pages.home_page       import HomePage
from pages.menu_page       import MenuPage
from pages.quiz_page       import QuizPage
from pages.logo_page       import LogoPage
from pages.difference_page import DifferencePage
from pages.result_page     import ResultPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setStyleSheet(QSS)

        # Contrôleurs
        self.tc    = TournamentController()
        self.audio = AudioManager()

        # Génération des assets
        generate_all()

        # Widget central empilé
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Créer toutes les pages
        self.pages = {}
        for name, Cls in [
            ("home",       HomePage),
            ("menu",       MenuPage),
            ("quiz",       QuizPage),
            ("logo",       LogoPage),
            ("difference", DifferencePage),
            ("result",     ResultPage),
        ]:
            page = Cls(self)
            self.stack.addWidget(page)
            self.pages[name] = page

        # Plein écran
        self.showFullScreen()

        # Page d'accueil
        self.show_page("home")

    def show_page(self, name: str, **kwargs):
        page = self.pages[name]
        page.on_show(**kwargs)
        self.stack.setCurrentWidget(page)

        # Audio automatique
        if name in ("home", "menu"):
            self.audio.play("calm")
        elif name in ("quiz", "logo", "difference"):
            self.audio.play("tension")
        elif name == "result":
            self.audio.play("victory")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
                self.resize(1280, 720)
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
                self.resize(1280, 720)
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 12))
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
