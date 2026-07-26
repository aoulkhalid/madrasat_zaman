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

from pages.home_page        import HomePage
from pages.menu_page        import MenuPage
from pages.quiz_page        import QuizPage
from pages.logo_page        import LogoPage
from pages.difference_page  import DifferencePage
from pages.secret_code_page import SecretCodePage
from pages.element_page     import ElementPage
from pages.heist_page       import HeistPage
from pages.cyber_page       import CyberPage
from pages.blindtest_page   import BlindTestPage
from pages.investment_page  import InvestmentPage
from pages.transmission_page import TransmissionPage
from pages.memory_page import MemoryPage
from pages.result_page      import ResultPage


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
            ("home",        HomePage),
            ("menu",        MenuPage),
            ("quiz",        QuizPage),
            ("logo",        LogoPage),
            ("difference",  DifferencePage),
            ("secret_code", SecretCodePage),
            ("element",     ElementPage),
            ("heist",       HeistPage),
            ("cyber",       CyberPage),
            ("blindtest",   BlindTestPage),
            ("investment",  InvestmentPage),
            ("transmission", TransmissionPage),
            ("memory", MemoryPage),
            ("result",      ResultPage),
        ]:
            page = Cls(self)
            self.stack.addWidget(page)
            self.pages[name] = page

        # Plein écran (contournement Wayland/GNOME)
        screen = QApplication.primaryScreen()
        geo = screen.geometry()
        self.setGeometry(geo)
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
        elif name in ("quiz", "logo", "difference", "secret_code", "element",
              "heist", "cyber", "blindtest", "investment", "transmission", "memory"):
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
    # IMPORTANT : doit être réglé AVANT la création de QApplication,
    # sinon Qt ignore l'attribut et le calcul de la taille d'écran (donc
    # showFullScreen()) peut être faussé sur les écrans HiDPI.
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)

    # Force le repli vers une police d'emoji couleur pour tous les caractères
    # non couverts par les polices utilisées dans l'app (icônes 🔥💧🎉 etc.)
    QFont.insertSubstitution("Segoe UI", "Noto Color Emoji")
    QFont.insertSubstitution("Segoe UI Emoji", "Noto Color Emoji")
    QFont.insertSubstitution("Arial", "Noto Color Emoji")
    QFont.insertSubstitution("Consolas", "Noto Color Emoji")

    app.setFont(QFont("Arial", 12))
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()