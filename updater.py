"""
updater.py
Checks GitHub Releases for a newer version of Zoetrope Studio and offers
to download + install it.  The check runs in a background thread so it
never blocks the UI.

Settings (stored in QSettings):
    auto_update_enabled  bool   default True
    last_checked         str    ISO timestamp of last successful check

Usage (from app.py):
    from updater import UpdateChecker
    checker = UpdateChecker(parent_window)
    checker.check(silent=True)   # silent=True → only show dialog if update found
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from urllib.request import urlopen, urlretrieve
from urllib.error import URLError

from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QSettings, QObject, QUrl,
)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QMessageBox, QCheckBox,
)

from version import APP_VERSION as CURRENT_VERSION

GITHUB_OWNER = "section9agent"
GITHUB_REPO  = "zoetrope-studio"

API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


def _version_tuple(v: str) -> tuple:
    """'1.2.3' → (1, 2, 3)"""
    try:
        return tuple(int(x) for x in v.lstrip("v").split("."))
    except Exception:
        return (0, 0, 0)


def _asset_name_for_platform() -> str:
    """Return the zip asset name GitHub Actions uploads for this OS."""
    p = platform.system()
    if p == "Windows":
        return "ZoetropeStudio-windows.zip"
    elif p == "Darwin":
        return "ZoetropeStudio-mac.zip"
    else:
        return "ZoetropeStudio-linux.zip"


# ---------------------------------------------------------------------------
# Background worker thread — does the network call
# ---------------------------------------------------------------------------

class _FetchWorker(QThread):
    finished = pyqtSignal(dict)   # emits the parsed JSON release object
    error    = pyqtSignal(str)    # emits an error message

    def run(self):
        try:
            with urlopen(API_URL, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            self.finished.emit(data)
        except URLError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(str(e))


# ---------------------------------------------------------------------------
# Download worker
# ---------------------------------------------------------------------------

class _DownloadWorker(QThread):
    progress = pyqtSignal(int)    # 0–100
    done     = pyqtSignal(str)    # path to downloaded zip
    error    = pyqtSignal(str)

    def __init__(self, url: str, dest: str):
        super().__init__()
        self._url  = url
        self._dest = dest

    def run(self):
        try:
            def _hook(block, block_size, total):
                if total > 0:
                    pct = min(100, int(block * block_size * 100 / total))
                    self.progress.emit(pct)

            urlretrieve(self._url, self._dest, reporthook=_hook)
            self.done.emit(self._dest)
        except Exception as e:
            self.error.emit(str(e))


# ---------------------------------------------------------------------------
# Update dialog shown when a new version is available
# ---------------------------------------------------------------------------

class _UpdateDialog(QDialog):
    def __init__(self, release: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Available")
        self.setFixedWidth(420)
        self.setModal(True)
        self.setStyleSheet("background: #111; color: #ccc;")

        self._release  = release
        self._worker   = None
        self._zip_path = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(12)

        tag = release.get("tag_name", "unknown")
        body = release.get("body", "").strip() or "No release notes."

        hdr = QLabel("A new version is available!")
        hdr.setStyleSheet("color: #fff; font-size: 15px; font-weight: 700;")
        layout.addWidget(hdr)

        ver_row = QHBoxLayout()
        ver_row.addWidget(QLabel(f"Current:  {CURRENT_VERSION}"))
        ver_row.addStretch()
        new_lbl = QLabel(f"New:  {tag}")
        new_lbl.setStyleSheet("color: #1D9E75; font-weight: 600;")
        ver_row.addWidget(new_lbl)
        layout.addLayout(ver_row)

        notes_lbl = QLabel(body[:600])   # cap notes length
        notes_lbl.setStyleSheet(
            "color: #888; font-size: 11px; background: #0d0d0d; "
            "border: 1px solid #1e1e1e; border-radius: 6px; padding: 8px;"
        )
        notes_lbl.setWordWrap(True)
        layout.addWidget(notes_lbl)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setVisible(False)
        self._progress.setStyleSheet("""
            QProgressBar {
                background: #1e1e1e; border: 1px solid #2a2a2a;
                border-radius: 4px; height: 8px; text-align: center;
            }
            QProgressBar::chunk { background: #1D9E75; border-radius: 4px; }
        """)
        layout.addWidget(self._progress)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #666; font-size: 11px;")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status)

        btn_row = QHBoxLayout()
        self._btn_later = QPushButton("Later")
        self._btn_later.setFixedHeight(32)
        self._btn_later.setStyleSheet("""
            QPushButton { background:#1e1e1e; color:#888; border:1px solid #2a2a2a;
                border-radius:6px; font-size:12px; }
            QPushButton:hover { background:#252525; color:#ccc; }
        """)
        self._btn_later.clicked.connect(self.reject)

        self._btn_update = QPushButton("⬇  Download & Install")
        self._btn_update.setFixedHeight(32)
        self._btn_update.setStyleSheet("""
            QPushButton { background:#1D9E75; color:#fff; border:none;
                border-radius:6px; font-size:13px; font-weight:600; padding:0 16px; }
            QPushButton:hover { background:#22b886; }
            QPushButton:disabled { background:#1e1e1e; color:#444; }
        """)
        self._btn_update.clicked.connect(self._start_download)

        btn_row.addWidget(self._btn_later)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_update)
        layout.addLayout(btn_row)

    def _asset_url(self) -> str | None:
        name = _asset_name_for_platform()
        for asset in self._release.get("assets", []):
            if asset.get("name") == name:
                return asset.get("browser_download_url")
        return None

    def _start_download(self):
        url = self._asset_url()
        if not url:
            # No matching asset — open browser to releases page instead
            QDesktopServices.openUrl(
                QUrl(f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest")
            )
            self.accept()
            return

        self._btn_update.setEnabled(False)
        self._btn_later.setEnabled(False)
        self._progress.setVisible(True)
        self._status.setText("Downloading…")

        dest = os.path.join(tempfile.gettempdir(), _asset_name_for_platform())
        self._worker = _DownloadWorker(url, dest)
        self._worker.progress.connect(self._progress.setValue)
        self._worker.done.connect(self._on_downloaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_downloaded(self, zip_path: str):
        self._status.setText("Installing…")
        self._progress.setValue(100)
        self._install(zip_path)

    def _on_error(self, msg: str):
        self._status.setText(f"Error: {msg}")
        self._btn_later.setEnabled(True)

    def _install(self, zip_path: str):
        """
        Unzip next to the current executable, then relaunch.
        On all three platforms the bundle is a folder (COLLECT mode).
        We replace the folder in-place and relaunch.
        """
        try:
            # Determine install root — the folder that contains the exe/app
            if getattr(sys, "frozen", False):
                # Running from a PyInstaller bundle
                app_dir = os.path.dirname(sys.executable)
                install_root = os.path.dirname(app_dir)   # one level up from exe
            else:
                # Running from source — just open the releases page
                QDesktopServices.openUrl(
                    QUrl(f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest")
                )
                self.accept()
                return

            # Extract to a temp dir next to install root
            tmp_extract = tempfile.mkdtemp(prefix="zoetrope_update_")
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(tmp_extract)

            # The zip contains a single top-level folder (ZoetropeStudio/)
            entries = os.listdir(tmp_extract)
            if len(entries) == 1:
                new_app_dir = os.path.join(tmp_extract, entries[0])
            else:
                new_app_dir = tmp_extract   # flat layout

            # Write a launcher script that swaps the folders and relaunches
            # (we can't replace our own running exe directly on Windows)
            launcher = self._write_launcher(install_root, new_app_dir)
            self.accept()

            if platform.system() == "Windows":
                subprocess.Popen(["cmd", "/c", launcher], close_fds=True)
            else:
                subprocess.Popen(["bash", launcher], close_fds=True)

            # Quit this instance
            from PyQt6.QtWidgets import QApplication
            QApplication.quit()

        except Exception as e:
            self._status.setText(f"Install failed: {e}")
            self._btn_later.setEnabled(True)

    def _write_launcher(self, install_root: str, new_app_dir: str) -> str:
        """Write a small shell/batch script that replaces the app then restarts."""
        if platform.system() == "Windows":
            script = os.path.join(tempfile.gettempdir(), "zoetrope_update.bat")
            exe = os.path.join(install_root, "ZoetropeStudio", "ZoetropeStudio.exe")
            old_dir = os.path.join(install_root, "ZoetropeStudio")
            with open(script, "w") as f:
                f.write("@echo off\n")
                f.write("timeout /t 2 /nobreak >nul\n")
                f.write(f'rmdir /s /q "{old_dir}"\n')
                f.write(f'xcopy /e /i /q "{new_app_dir}" "{old_dir}"\n')
                f.write(f'start "" "{exe}"\n')
        else:
            script = os.path.join(tempfile.gettempdir(), "zoetrope_update.sh")
            exe_name = "ZoetropeStudio"
            old_dir  = os.path.join(install_root, exe_name)
            exe      = os.path.join(old_dir, exe_name)
            with open(script, "w") as f:
                f.write("#!/bin/bash\n")
                f.write("sleep 2\n")
                f.write(f'rm -rf "{old_dir}"\n')
                f.write(f'cp -r "{new_app_dir}" "{old_dir}"\n')
                f.write(f'chmod +x "{exe}"\n')
                f.write(f'"{exe}" &\n')
            os.chmod(script, 0o755)
        return script


# ---------------------------------------------------------------------------
# Public class used by app.py
# ---------------------------------------------------------------------------

class UpdateChecker(QObject):
    """
    Thin wrapper: start background fetch, show dialog if update found.
    Remembers the auto-update preference in QSettings.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QSettings("ZoetropeStudio", "ZoetropeStudio")
        self._worker   = None
        self._silent   = True

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------

    @property
    def auto_update_enabled(self) -> bool:
        return self._settings.value("auto_update_enabled", True, type=bool)

    @auto_update_enabled.setter
    def auto_update_enabled(self, val: bool):
        self._settings.setValue("auto_update_enabled", val)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check(self, silent: bool = True):
        """
        Start a background check.
        silent=True  → only show a dialog if an update is available.
        silent=False → also show "you're up to date" if no update found.
        """
        if not self.auto_update_enabled and silent:
            return
        self._silent = silent
        self._worker = _FetchWorker()
        self._worker.finished.connect(self._on_fetch_done)
        self._worker.error.connect(self._on_fetch_error)
        self._worker.start()

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_fetch_done(self, release: dict):
        tag = release.get("tag_name", "")
        if _version_tuple(tag) > _version_tuple(CURRENT_VERSION):
            parent = self.parent() if self.parent() else None
            dlg = _UpdateDialog(release, parent)
            dlg.exec()
        elif not self._silent:
            QMessageBox.information(
                self.parent(),
                "Up to Date",
                f"You have the latest version ({CURRENT_VERSION}).",
            )

    def _on_fetch_error(self, msg: str):
        if not self._silent:
            QMessageBox.warning(
                self.parent(),
                "Update Check Failed",
                f"Could not reach GitHub:\n{msg}",
            )
