import sys
import os
import subprocess
import re
import shlex
import tempfile
import shutil
import zipfile

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QTextEdit, QLineEdit, QTabWidget, QFrame, QMenu, QSizePolicy,
    QFileDialog, QMessageBox, QComboBox, QProgressBar, QScrollArea, QDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl
from PySide6.QtGui import QColor, QFont, QIcon, QPalette, QDesktopServices

# --- IMPORTS DOS MÓDULOS SEPARADOS ---
from config import APP_VERSION, GITHUB_USER, GITHUB_REPO, tr
from utils import (
    run_adb_command, run_command, check_all_dependencies,
    round_ram_gb, battery_health_text, compare_versions,
    normalize_version, _apply_chmod
)
from threads import (
    UpdateCheckerThread,
    InstallPayloadDumperThread, InstallPlatformToolsThread, FastbootThread,
    RomExtractThread, SequentialFastbootThread
)
from ui_helpers import make_scroll_tab, InfoCard, TerminalOutput, SectionHeader
from dialogs import (
    InstallPayloadDumperDialog, UpdateDialog,
    InstallToolsDialog
)


# ===============================
# MAIN WINDOW
# ===============================
class RomManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"ROM Manager Pro  v{APP_VERSION}")
        self.resize(1240, 780); self.setMinimumSize(800, 500)
        self._lang = "pt"
        central = QWidget(); self.setCentralWidget(central)
        root = QHBoxLayout(); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        root.addWidget(self._build_sidebar())
        self.tabs = QTabWidget(); self.tabs.setObjectName("MainTabs"); self.tabs.tabBar().hide()
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self.tabs, 1); central.setLayout(root)
        self.create_system_tab(); self.create_apps_tab(); self.create_adb_tab()
        self.create_fastboot_tab(); self.create_rom_tab(); self.create_hyperos_tab()
        self.apply_style()
        self._sidebar_buttons[0].setChecked(True)
        QTimer.singleShot(700, self._startup_checks)

    # ── STARTUP ──────────────────────────────────────────────
    def _startup_checks(self):
        results = check_all_dependencies()
        for tool, ok in results.items():
            self._update_dep_indicator(tool, ok)

        missing_tools = [t for t in ("adb","fastboot") if not results.get(t)]
        if missing_tools:
            dlg = InstallToolsDialog(self, missing_tools)
            if dlg.exec() == QDialog.Accepted:
                results2 = check_all_dependencies()
                for tool, ok in results2.items():
                    self._update_dep_indicator(tool, ok)

        if not results.get("payload-dumper-go"):
            dlg2 = InstallPayloadDumperDialog(self)
            if dlg2.exec() == QDialog.Accepted:
                exe = dlg2.get_exe_path()
                if exe:
                    if hasattr(self, "dumper_path_input"): self.dumper_path_input.setText(exe)
                    self._update_dep_indicator("payload-dumper-go", True)

        self._update_thread = UpdateCheckerThread()
        self._update_thread.result_signal.connect(self._on_update_result)
        self._update_thread.start()

    def _on_update_result(self, data):
        if not data: return
        remote_tag = data.get("version", "").strip()
        if not remote_tag: return
        if compare_versions(normalize_version(remote_tag), normalize_version(APP_VERSION)) > 0:
            UpdateDialog(self, remote_tag, data["url"], data.get("notes","")).exec()

    def _update_dep_indicator(self, tool, ok):
        if tool not in self._dep_indicators: return
        dot, lbl = self._dep_indicators[tool]
        color = "#4ADE80" if ok else "#F87171"
        dot.setStyleSheet(f"color:{color};font-size:10px;")
        lbl.setStyleSheet(f"color:{'#4B5563' if ok else '#F87171'};font-size:10px;")

    # ── SIDEBAR ──────────────────────────────────────────────
    def _build_sidebar(self):
        sidebar = QFrame(); sidebar.setObjectName("Sidebar"); sidebar.setFixedWidth(240)
        sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        layout = QVBoxLayout(); layout.setContentsMargins(14,24,14,24); layout.setSpacing(4)
        logo = QLabel("⚡ ROM Manager"); logo.setObjectName("SidebarLogo"); logo.setWordWrap(True)
        layout.addWidget(logo)
        self._dep_indicators = {}
        for tool in ("adb","fastboot","payload-dumper-go"):
            row = QHBoxLayout(); row.setSpacing(6)
            dot = QLabel("●"); dot.setFixedWidth(14); dot.setStyleSheet("color:#374151;font-size:10px;")
            lbl = QLabel(tool); lbl.setStyleSheet("color:#374151;font-size:10px;")
            row.addWidget(dot); row.addWidget(lbl); row.addStretch()
            layout.addLayout(row); self._dep_indicators[tool] = (dot, lbl)
        div = QFrame(); div.setObjectName("Divider"); div.setFixedHeight(1)
        layout.addSpacing(12); layout.addWidget(div); layout.addSpacing(12)
        self._sidebar_buttons = []
        for idx, key in enumerate(["nav_sistema","nav_apps","nav_adb","nav_fastboot","nav_aosp","nav_hyperos"]):
            btn = QPushButton(tr(self._lang, key)); btn.setObjectName("NavButton"); btn.setCheckable(True)
            btn.clicked.connect(lambda c, i=idx: self._switch_tab(i))
            layout.addWidget(btn); self._sidebar_buttons.append(btn)
        layout.addStretch()
        lang_row = QHBoxLayout()
        li = QLabel("🌐"); li.setStyleSheet("font-size:14px;"); li.setFixedWidth(22)
        self.lang_combo = QComboBox(); self.lang_combo.setObjectName("LangCombo")
        for name, code in [("Português","pt"),("English","en"),("Español","es"),("Русский","ru")]:
            self.lang_combo.addItem(name, code)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(li); lang_row.addWidget(self.lang_combo, 1)
        layout.addLayout(lang_row); layout.addSpacing(8)
        self._donate_btn = QPushButton(tr(self._lang, "donate")); self._donate_btn.setObjectName("DonateButton")
        self._donate_btn.setFixedHeight(36); self._donate_btn.setCursor(Qt.PointingHandCursor)
        self._donate_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ko-fi.com/alysoncamargo")))
        layout.addWidget(self._donate_btn); layout.addSpacing(6)
        ver = QLabel(f"v{APP_VERSION}"); ver.setObjectName("VersionLabel"); layout.addWidget(ver)
        self._dev_label = QLabel(tr(self._lang, "dev_by")); self._dev_label.setObjectName("DevLabel")
        layout.addWidget(self._dev_label); layout.addSpacing(4)
        icons_row = QHBoxLayout(); icons_row.setSpacing(6)
        gh = QPushButton("  GitHub"); gh.setObjectName("IconLinkButton"); gh.setCursor(Qt.PointingHandCursor)
        gh.setFixedHeight(28); gh.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}")))
        tg = QPushButton("  Telegram"); tg.setObjectName("IconLinkButton"); tg.setCursor(Qt.PointingHandCursor)
        tg.setFixedHeight(28); tg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/romManagerPro")))
        icons_row.addWidget(gh); icons_row.addWidget(tg); layout.addLayout(icons_row)
        sidebar.setLayout(layout); return sidebar

    def _switch_tab(self, index):
        self.tabs.setCurrentIndex(index)
        for i, btn in enumerate(self._sidebar_buttons): btn.setChecked(i == index)

    def _on_lang_changed(self, index):
        self._lang = self.lang_combo.itemData(index); self._rebuild_all_tabs()

    def _rebuild_all_tabs(self):
        saved = {
            "rom_path":    getattr(self,"rom_path_input",None)    and self.rom_path_input.text(),
            "dumper_path": getattr(self,"dumper_path_input",None) and self.dumper_path_input.text(),
            "partitions":  getattr(self,"partitions_input",None)  and self.partitions_input.text(),
            "hyper_rom":   getattr(self,"hyper_rom_input",None)   and self.hyper_rom_input.text(),
            "adb_cmd":     getattr(self,"adb_input",None)         and self.adb_input.text(),
            "fastboot_cmd":getattr(self,"fastboot_input",None)    and self.fastboot_input.text(),
        }
        while self.tabs.count():
            w = self.tabs.widget(0); self.tabs.removeTab(0)
            if w: w.deleteLater()
        self._sec_headers = {}
        self.create_system_tab(); self.create_apps_tab(); self.create_adb_tab()
        self.create_fastboot_tab(); self.create_rom_tab(); self.create_hyperos_tab()
        L = self._lang
        for btn, key in zip(self._sidebar_buttons, ["nav_sistema","nav_apps","nav_adb","nav_fastboot","nav_aosp","nav_hyperos"]):
            btn.setText(tr(L, key))
        self._donate_btn.setText(tr(L, "donate")); self._dev_label.setText(tr(L, "dev_by"))
        for attr, val in [("rom_path_input","rom_path"),("dumper_path_input","dumper_path"),
                          ("partitions_input","partitions"),("hyper_rom_input","hyper_rom"),
                          ("adb_input","adb_cmd"),("fastboot_input","fastboot_cmd")]:
            w = getattr(self, attr, None)
            if w and saved[val]: w.setText(saved[val])
        self.tabs.setCurrentIndex(next((i for i,b in enumerate(self._sidebar_buttons) if b.isChecked()), 0))

    # ── STYLE ─────────────────────────────────────────────────
    def apply_style(self):
        self.setStyleSheet("""
        * { font-family: 'Consolas', 'Courier New', monospace; }
        QWidget { background-color: #0C0E12; color: #D8DEE9; font-size: 13px; }
        QScrollArea#TabScrollArea { background: transparent; border: none; }
        QScrollArea#TabScrollArea > QWidget > QWidget { background: transparent; }
        QWidget#TabOuter, QWidget#TabInner { background: transparent; }
        QFrame#Sidebar { background-color: #111318; border-right: 1px solid #1E2028; }
        QLabel#SidebarLogo { font-size: 16px; font-weight: bold; color: #7EB8F7; letter-spacing: 1px; padding: 4px 0; }
        QFrame#Divider { background-color: #1E2028; border: none; }
        QComboBox#LangCombo { background-color: #1A1D25; border: 1px solid #252933; border-radius: 7px; padding: 5px 8px; color: #9CA3AF; font-size: 12px; }
        QComboBox#LangCombo:hover { border-color: #3B4460; color: #D8DEE9; }
        QComboBox#LangCombo::drop-down { border: none; width: 20px; }
        QComboBox#LangCombo QAbstractItemView { background-color: #151820; border: 1px solid #252933; color: #9CA3AF; selection-background-color: #1C2333; selection-color: #7EB8F7; padding: 4px; }
        QPushButton#NavButton { background: transparent; border: none; border-radius: 8px; padding: 10px 14px; text-align: left; color: #6B7280; font-size: 14px; }
        QPushButton#NavButton:hover { background-color: #1A1D25; color: #D8DEE9; }
        QPushButton#NavButton:checked { background-color: #1C2333; color: #7EB8F7; border-left: 3px solid #7EB8F7; }
        QLabel#VersionLabel { font-size: 13px; font-weight: bold; color: #FFFFFF; padding: 0 2px; }
        QLabel#DevLabel { font-size: 11px; color: #4B5563; padding: 0 2px; }
        QPushButton#IconLinkButton { background: transparent; border: 1px solid #1E2028; border-radius: 7px; color: #6B7280; font-size: 11px; padding: 0 6px; text-align: left; }
        QPushButton#IconLinkButton:hover { background-color: #1A1D25; border-color: #2A3145; color: #D8DEE9; }
        QPushButton#DonateButton { background-color: #1A1400; border: 1px solid #5C4A00; border-radius: 8px; color: #F59E0B; font-size: 12px; font-weight: bold; }
        QPushButton#DonateButton:hover { background-color: #241C00; border-color: #92700A; color: #FCD34D; }
        QTabWidget#MainTabs { border: none; }
        QTabWidget#MainTabs::pane { border: none; background-color: #0C0E12; }
        QFrame#InstallFrame, QFrame#FlashFrame { background-color: #111318; border: 1px solid #1E2028; border-radius: 10px; }
        QFrame#FlashFrame { border-color: #2A1E0A; }
        QFrame#KsuFrame { background-color: #111318; border: 1px solid #2A1535; border-radius: 10px; }
        QFrame#InfoCard { background-color: #111318; border: 1px solid #1E2028; border-radius: 12px; }
        QFrame#InfoCard:hover { border: 1px solid #2A3145; }
        QLabel#cardIcon { font-size: 15px; }
        QLabel#cardTitle { font-size: 10px; color: #4B5563; letter-spacing: 1.5px; }
        QLabel#cardValue { font-size: 17px; font-weight: bold; color: #E2E8F0; }
        QLabel#SectionHeader { font-size: 11px; color: #4B5563; letter-spacing: 2px; padding: 0 4px; }
        QPushButton { background-color: #1A1D25; border: 1px solid #252933; border-radius: 8px; padding: 8px 16px; color: #9CA3AF; font-size: 12px; }
        QPushButton:hover { background-color: #1E2330; border-color: #3B4460; color: #D8DEE9; }
        QPushButton:pressed { background-color: #131823; }
        QPushButton:disabled { background-color: #111318; border-color: #1A1D24; color: #374151; }
        QPushButton#PrimaryButton { background-color: #1C2E4A; border: 1px solid #2B4778; color: #7EB8F7; }
        QPushButton#PrimaryButton:hover { background-color: #1F3457; border-color: #3B6BAA; color: #A8D0F8; }
        QPushButton#DangerButton { background-color: #2A1A1A; border: 1px solid #5C2222; color: #F87171; }
        QPushButton#DangerButton:hover { background-color: #341F1F; border-color: #7B3333; }
        QPushButton#SuccessButton { background-color: #0F2A1A; border: 1px solid #1A5C32; color: #4ADE80; font-weight: bold; }
        QPushButton#SuccessButton:hover { background-color: #153520; border-color: #22A355; color: #6EF0A0; }
        QProgressBar { background-color: #1A1D25; border: none; border-radius: 3px; }
        QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7EB8F7,stop:1 #4ADE80); border-radius: 3px; }
        QLabel#SideloadNotice { background-color: #0F1F14; border: 1px solid #1A5C32; border-radius: 8px; color: #4ADE80; font-size: 12px; padding: 10px 14px; }
        QListWidget { background-color: #111318; border: 1px solid #1E2028; border-radius: 10px; padding: 6px; outline: none; }
        QListWidget::item { padding: 8px 12px; border-radius: 6px; color: #9CA3AF; }
        QListWidget::item:hover { background-color: #1A1D25; color: #D8DEE9; }
        QListWidget::item:selected { background-color: #1C2333; color: #7EB8F7; }
        QTextEdit#TerminalOutput { background-color: #080A0D; border: 1px solid #1A1D24; border-radius: 10px; padding: 14px; color: #7EB8F7; font-size: 12px; line-height: 1.6; }
        QLineEdit { background-color: #111318; border: 1px solid #1E2028; border-radius: 8px; padding: 9px 14px; color: #D8DEE9; font-size: 13px; selection-background-color: #1C2E4A; }
        QLineEdit:focus { border-color: #2B4778; background-color: #131620; }
        QScrollBar:vertical { background: transparent; width: 6px; margin: 0; }
        QScrollBar::handle:vertical { background: #252933; border-radius: 3px; min-height: 30px; }
        QScrollBar::handle:vertical:hover { background: #374151; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        QScrollBar:horizontal { background: transparent; height: 6px; }
        QScrollBar::handle:horizontal { background: #252933; border-radius: 3px; }
        QScrollBar::handle:horizontal:hover { background: #374151; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
        QListWidget#DebloatList { background-color: #0D0F14; border: 1px solid #1E2028; border-radius: 10px; padding: 4px; outline: none; }
        QListWidget#DebloatList::item { padding: 7px 10px; border-radius: 5px; border-bottom: 1px solid #13151B; font-size: 12px; }
        QListWidget#DebloatList::item:hover { background-color: #1A1D25; }
        QListWidget#DebloatList::indicator { width: 16px; height: 16px; border: 1px solid #374151; border-radius: 4px; background-color: #111318; margin-right: 4px; }
        QListWidget#DebloatList::indicator:hover { border-color: #7EB8F7; }
        QListWidget#DebloatList::indicator:checked { background-color: #2563EB; border-color: #3B82F6; }
        QPushButton#SmallBtn { background-color: #151820; border: 1px solid #1E2028; border-radius: 5px; color: #4B5563; font-size: 11px; padding: 0 10px; }
        QPushButton#SmallBtn:hover { background-color: #1A1D25; color: #9CA3AF; }
        QListWidget#ScriptsList::item { padding: 9px 12px; border-radius: 6px; color: #9CA3AF; border-bottom: 1px solid #1A1D25; }
        QListWidget#ScriptsList::item:hover { background-color: #1A1D25; color: #E879F9; }
        QListWidget#ScriptsList::item:selected { background-color: #2A1535; color: #E879F9; border-left: 3px solid #E879F9; }
        QMenu { background-color: #151820; border: 1px solid #252933; border-radius: 8px; padding: 4px; }
        QMenu::item { padding: 8px 18px; border-radius: 5px; color: #9CA3AF; }
        QMenu::item:selected { background-color: #1C2333; color: #7EB8F7; }
        QMenu::separator { height: 1px; background: #1E2028; margin: 4px 8px; }
        """)

    # ── TAB HELPERS ───────────────────────────────────────────
    def _tab_header(self, layout, title, subtitle=""):
        hr = QHBoxLayout(); tl = QLabel(title)
        tl.setStyleSheet("font-size:20px;font-weight:bold;color:#E2E8F0;")
        hr.addWidget(tl); hr.addStretch()
        if subtitle:
            sl = QLabel(subtitle); sl.setStyleSheet("font-size:12px;color:#374151;"); hr.addWidget(sl)
        layout.addLayout(hr)

    def _sec(self, key):
        if not hasattr(self, "_sec_headers"): self._sec_headers = {}
        h = SectionHeader(tr(self._lang, key)); self._sec_headers[key] = h; return h

    # ── SISTEMA TAB ───────────────────────────────────────────
    def create_system_tab(self):
        L = self._lang; outer, layout = make_scroll_tab()
        self._tab_header(layout, tr(L,"tab_sistema"), tr(L,"tab_sistema_sub"))
        layout.addWidget(self._sec("sec_device"))
        grid = QGridLayout(); grid.setSpacing(12)
        for i in range(3): grid.setColumnStretch(i, 1)
        card_defs = [("card_modelo","🖥"),("card_android","🤖"),("card_serial","🔑"),
                     ("card_imei","📡"),("card_ram","💾"),("card_storage","🗄"),
                     ("card_battery","🔋"),("card_health","❤")]
        self.cards = {}; row = col = 0
        for key, icon in card_defs:
            pt_name = tr("pt", key); card = InfoCard(tr(L, key), icon)
            self.cards[pt_name] = card; grid.addWidget(card, row, col)
            col += 1
            if col == 3: col = 0; row += 1
        layout.addLayout(grid)
        btn_row = QHBoxLayout()
        refresh = QPushButton(tr(L,"btn_refresh")); refresh.setObjectName("PrimaryButton")
        refresh.setMinimumWidth(160); refresh.setMaximumWidth(220); refresh.clicked.connect(self.load_device_info)
        btn_row.addWidget(refresh); btn_row.addStretch(); layout.addLayout(btn_row); layout.addStretch()
        self.tabs.addTab(outer, "Sistema")

    def load_device_info(self):
        model   = run_adb_command(["shell","getprop","ro.product.model"]) or "—"
        android = run_adb_command(["shell","getprop","ro.build.version.release"]) or "—"
        serial  = run_adb_command(["get-serialno"]) or "—"
        imei    = run_adb_command(["shell","getprop","persist.radio.imei"])
        if not imei or "ERROR" in imei: imei = tr(self._lang, "restricted")
        meminfo = run_adb_command(["shell","cat","/proc/meminfo"])
        m = re.search(r'MemTotal:\s+(\d+)', meminfo)
        ram = round_ram_gb(int(m.group(1))) if m else "—"
        df = run_adb_command(["shell","df","/data"]); storage = "—"
        for line in df.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] not in ("Filesystem","tmpfs"):
                try:
                    gb = int(parts[1])/1024/1024
                    storage = f"{min([8,16,32,64,128,256,512,1024],key=lambda x:abs(x-gb))} GB"; break
                except: continue
        battery = run_adb_command(["shell","dumpsys","battery"])
        level   = re.search(r'level: (\d+)', battery)
        health  = re.search(r'health: (\d+)', battery)
        bat     = level.group(1)+"%" if level else "—"
        htext   = battery_health_text(health.group(1), self._lang) if health else "—"
        for key, value in zip(self.cards.keys(), [model,android,serial,imei,ram,storage,bat,htext]):
            self.cards[key].value.setText(value)

    # ── APPS TAB ──────────────────────────────────────────────
    def create_apps_tab(self):
        L = self._lang; outer, layout = make_scroll_tab()
        self._tab_header(layout, tr(L,"tab_apps"), tr(L,"tab_apps_sub"))
        layout.addWidget(self._sec("sec_install_apk"))
        f = QFrame(); f.setObjectName("InstallFrame"); fl = QVBoxLayout(); fl.setContentsMargins(16,14,16,14); fl.setSpacing(10)
        fr = QHBoxLayout(); self.apk_path_input = QLineEdit(); self.apk_path_input.setPlaceholderText(tr(L,"apk_placeholder")); self.apk_path_input.setReadOnly(True)
        bb = QPushButton(tr(L,"btn_browse")); bb.setMinimumWidth(100); bb.setMaximumWidth(140); bb.clicked.connect(self._browse_apk)
        fr.addWidget(self.apk_path_input, 1); fr.addWidget(bb); fl.addLayout(fr)
        ar = QHBoxLayout(); self.install_btn = QPushButton(tr(L,"btn_install")); self.install_btn.setObjectName("PrimaryButton"); self.install_btn.setMinimumWidth(180); self.install_btn.setMaximumWidth(260); self.install_btn.setEnabled(False); self.install_btn.clicked.connect(self._install_apk)
        self.install_status = QLabel(""); self.install_status.setStyleSheet("font-size:12px;color:#374151;"); self.install_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        ar.addWidget(self.install_btn); ar.addWidget(self.install_status); ar.addStretch(); fl.addLayout(ar); f.setLayout(fl); layout.addWidget(f)
        layout.addWidget(self._sec("sec_packages"))
        br = QHBoxLayout(); lb = QPushButton(tr(L,"btn_load_apps")); lb.setObjectName("PrimaryButton"); lb.setMinimumWidth(140); lb.setMaximumWidth(180); lb.clicked.connect(self.load_apps)
        self.app_count_label = QLabel(""); self.app_count_label.setStyleSheet("color:#374151;font-size:12px;")
        br.addWidget(lb); br.addWidget(self.app_count_label); br.addStretch(); layout.addLayout(br)
        self.apps_list = QListWidget(); self.apps_list.setMinimumHeight(160); self.apps_list.setContextMenuPolicy(Qt.CustomContextMenu); self.apps_list.customContextMenuRequested.connect(self.app_menu)
        layout.addWidget(self.apps_list)
        layout.addWidget(self._sec("sec_debloat"))
        df2 = QFrame(); df2.setObjectName("FlashFrame"); dl = QVBoxLayout(); dl.setContentsMargins(16,14,16,14); dl.setSpacing(10)
        hint = QLabel(tr(L,"debloat_hint")); hint.setStyleSheet("font-size:11px;color:#4B5563;"); hint.setWordWrap(True); dl.addWidget(hint)
        filterrow = QHBoxLayout(); self.debloat_filter = QLineEdit(); self.debloat_filter.setPlaceholderText(tr(L,"debloat_filter")); self.debloat_filter.textChanged.connect(self._debloat_filter_changed)
        lall = QPushButton(tr(L,"btn_load_all")); lall.setObjectName("PrimaryButton"); lall.setMinimumWidth(130); lall.setMaximumWidth(170); lall.clicked.connect(self.load_all_apps_debloat)
        filterrow.addWidget(self.debloat_filter, 1); filterrow.addWidget(lall); dl.addLayout(filterrow)
        selrow = QHBoxLayout(); self.debloat_count_label = QLabel(""); self.debloat_count_label.setStyleSheet("font-size:11px;color:#4B5563;")
        sa = QPushButton("Selecionar tudo"); sa.setObjectName("SmallBtn"); sa.setFixedHeight(26); sa.clicked.connect(self._debloat_check_all)
        da = QPushButton("Desmarcar tudo"); da.setObjectName("SmallBtn"); da.setFixedHeight(26); da.clicked.connect(self._debloat_uncheck_all)
        selrow.addWidget(self.debloat_count_label, 1); selrow.addWidget(sa); selrow.addWidget(da); dl.addLayout(selrow)
        self.debloat_list = QListWidget(); self.debloat_list.setObjectName("DebloatList"); self.debloat_list.setSelectionMode(QListWidget.NoSelection); self.debloat_list.itemChanged.connect(self._debloat_item_checked); self.debloat_list.setMinimumHeight(200); dl.addWidget(self.debloat_list)
        actrow = QHBoxLayout(); actrow.setSpacing(10)
        self.disable_btn = QPushButton(tr(L,"btn_disable")); self.disable_btn.setObjectName("DangerButton"); self.disable_btn.setFixedHeight(36); self.disable_btn.setMinimumWidth(160); self.disable_btn.setEnabled(False); self.disable_btn.clicked.connect(self._debloat_disable)
        self.enable_btn = QPushButton(tr(L,"btn_enable")); self.enable_btn.setObjectName("SuccessButton"); self.enable_btn.setFixedHeight(36); self.enable_btn.setMinimumWidth(150); self.enable_btn.setEnabled(False); self.enable_btn.clicked.connect(self._debloat_enable)
        self.debloat_status = QLabel(""); self.debloat_status.setStyleSheet("font-size:12px;color:#374151;"); self.debloat_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        actrow.addWidget(self.disable_btn); actrow.addWidget(self.enable_btn); actrow.addWidget(self.debloat_status); actrow.addStretch(); dl.addLayout(actrow); df2.setLayout(dl); layout.addWidget(df2)
        self._debloat_all_items = []; self.tabs.addTab(outer, "Apps")

    def _browse_apk(self):
        path, _ = QFileDialog.getOpenFileName(self,"Selecionar APK","","APK (*.apk);;Todos (*)")
        if path: self.apk_path_input.setText(path); self.install_btn.setEnabled(True); self.install_status.setText(f"  {os.path.basename(path)}")

    def _install_apk(self):
        path = self.apk_path_input.text().strip()
        if not path: return
        self.install_btn.setEnabled(False); self.install_status.setText("⏳  Instalando..."); self.install_status.setStyleSheet("font-size:12px;color:#F59E0B;"); QApplication.processEvents()
        out = run_command(f'adb install -r "{path}"')
        if "Success" in out: self.install_status.setText("✓  Instalado!"); self.install_status.setStyleSheet("font-size:12px;color:#4ADE80;"); self.load_apps()
        else:
            err = out.strip().splitlines()[-1] if out.strip() else "Erro"
            self.install_status.setText(f"✗  {err}"); self.install_status.setStyleSheet("font-size:12px;color:#F87171;")
        self.install_btn.setEnabled(True)

    def load_apps(self):
        self.apps_list.clear()
        out = run_command("adb shell pm list packages -3")
        pkgs = [p.replace("package:","").strip() for p in out.splitlines() if p.strip()]
        for pkg in sorted(pkgs):
            item = QListWidgetItem(f"  {pkg}"); item.setData(Qt.UserRole, pkg); self.apps_list.addItem(item)
        self.app_count_label.setText(tr(self._lang,"packages_found",n=len(pkgs)))

    def app_menu(self, position):
        item = self.apps_list.itemAt(position)
        if not item: return
        pkg = item.data(Qt.UserRole); menu = QMenu(); L = self._lang
        menu.addAction(tr(L,"menu_open"),    lambda: run_command(f"adb shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1"))
        menu.addAction(tr(L,"menu_backup"),  lambda: self._backup_apk(pkg))
        menu.addSeparator()
        menu.addAction(tr(L,"menu_clear"),   lambda: run_command(f"adb shell pm clear {pkg}"))
        menu.addAction(tr(L,"menu_uninstall"),lambda: self._uninstall_app(pkg, item))
        menu.exec(self.apps_list.mapToGlobal(position))

    def _backup_apk(self, pkg):
        p = run_command(f"adb shell pm path {pkg}").replace("package:","").strip()
        if p: run_command(f'adb pull "{p}"')

    def _uninstall_app(self, pkg, item):
        run_command(f"adb uninstall {pkg}"); self.apps_list.takeItem(self.apps_list.row(item))

    # ── DEBLOAT ───────────────────────────────────────────────
    def load_all_apps_debloat(self):
        self.debloat_list.blockSignals(True); self.debloat_list.clear(); self._debloat_all_items = []
        self.disable_btn.setEnabled(False); self.enable_btn.setEnabled(False)
        self.debloat_status.setText("⏳  Carregando..."); self.debloat_status.setStyleSheet("font-size:12px;color:#F59E0B;"); QApplication.processEvents()
        all_out = run_adb_command(["shell","pm","list","packages","-f"])
        dis_out = run_adb_command(["shell","pm","list","packages","-d"])
        sys_out = run_adb_command(["shell","pm","list","packages","-s"])
        dis_pkgs = set()
        for line in dis_out.splitlines():
            m = re.search(r'package:(.+)', line)
            if m:
                pkg = m.group(1).strip()
                if "=" in pkg: pkg = pkg.rsplit("=",1)[-1]
                dis_pkgs.add(pkg.strip())
        sys_pkgs = set()
        for line in sys_out.splitlines():
            m = re.search(r'package:(.+)', line)
            if m: sys_pkgs.add(m.group(1).strip())
        items = []
        for line in all_out.splitlines():
            m = re.search(r'package:(.+)=(.+)', line)
            if not m: continue
            apk, pkg = m.group(1).strip(), m.group(2).strip()
            is_sys = pkg in sys_pkgs or "/system/" in apk or "/product/" in apk
            items.append((pkg, is_sys, pkg in dis_pkgs))
        items.sort(key=lambda x: (not x[2], not x[1], x[0]))
        L = self._lang
        for pkg, is_sys, is_dis in items:
            tags = [tr(L,"tag_system") if is_sys else tr(L,"tag_user")]
            if is_dis: tags.append(tr(L,"tag_disabled"))
            item = QListWidgetItem(f" {pkg}  [" + " · ".join(tags) + "]")
            item.setData(Qt.UserRole, {"pkg":pkg,"sys":is_sys,"disabled":is_dis})
            item.setFlags(item.flags()|Qt.ItemIsUserCheckable); item.setCheckState(Qt.Unchecked)
            item.setForeground(QColor("#F87171" if is_dis else "#F59E0B" if is_sys else "#D8DEE9"))
            self.debloat_list.addItem(item); self._debloat_all_items.append(item)
        self.debloat_list.blockSignals(False); self._update_debloat_count(); self.debloat_status.setText("")

    def _debloat_check_all(self):
        self.debloat_list.blockSignals(True)
        for i in range(self.debloat_list.count()): self.debloat_list.item(i).setCheckState(Qt.Checked)
        self.debloat_list.blockSignals(False); self._update_debloat_count()

    def _debloat_uncheck_all(self):
        self.debloat_list.blockSignals(True)
        for i in range(self.debloat_list.count()): self.debloat_list.item(i).setCheckState(Qt.Unchecked)
        self.debloat_list.blockSignals(False); self._update_debloat_count()

    def _debloat_filter_changed(self, text):
        text = text.lower().strip(); self.debloat_list.blockSignals(True); self.debloat_list.clear()
        for item in self._debloat_all_items:
            if not text or text in item.data(Qt.UserRole)["pkg"].lower(): self.debloat_list.addItem(item)
        self.debloat_list.blockSignals(False); self._update_debloat_count()

    def _debloat_item_checked(self, _): self._update_debloat_count()

    def _checked_items(self):
        return [self.debloat_list.item(i) for i in range(self.debloat_list.count())
                if self.debloat_list.item(i).checkState() == Qt.Checked]

    def _update_debloat_count(self):
        total = self.debloat_list.count(); checked = len(self._checked_items())
        self.debloat_count_label.setText(tr(self._lang,"debloat_found",n=total,s=checked))
        self.disable_btn.setEnabled(checked > 0); self.enable_btn.setEnabled(checked > 0)

    def _msg_box(self, title, text, body, ok_text, cancel_text, hover_color):
        msg = QMessageBox(self); msg.setWindowTitle(title); msg.setIcon(QMessageBox.Warning)
        msg.setText(text); msg.setInformativeText(body); msg.setTextFormat(Qt.RichText)
        msg.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        msg.button(QMessageBox.Ok).setText(ok_text); msg.button(QMessageBox.Cancel).setText(cancel_text)
        msg.setStyleSheet(f"QMessageBox{{background:#111318;color:#D8DEE9;}}QMessageBox QLabel{{color:#D8DEE9;font-size:12px;min-width:400px;}}QPushButton{{background:#1A1D25;border:1px solid #252933;border-radius:6px;padding:6px 18px;color:#9CA3AF;}}QPushButton:hover{{background:#1A1A1A;color:{hover_color};}}")
        return msg.exec()

    def _debloat_disable(self):
        selected = self._checked_items()
        if not selected: return
        L = self._lang; pkgs = [it.data(Qt.UserRole)["pkg"] for it in selected]
        body = tr(L,"debloat_confirm_body")+"<br><br>"+"".join(f"&nbsp;&nbsp;• <code>{p}</code><br>" for p in pkgs[:15])
        if len(pkgs) > 15: body += f"&nbsp;&nbsp;... +{len(pkgs)-15}<br>"
        if self._msg_box(tr(L,"debloat_confirm",n=len(pkgs)),tr(L,"debloat_confirm",n=len(pkgs)),body,tr(L,"debloat_ok"),tr(L,"btn_cancel"),"#F87171") != QMessageBox.Ok: return
        self.disable_btn.setEnabled(False); self.enable_btn.setEnabled(False)
        self.debloat_status.setText(tr(L,"status_disabling",n=len(pkgs))); QApplication.processEvents()
        ok = err = 0
        for item in selected:
            pkg = item.data(Qt.UserRole)["pkg"]
            out = run_adb_command(["shell","pm","disable-user","--user","0",pkg])
            if "disabled" in out.lower() or "success" in out.lower():
                ok += 1
                for it in self._debloat_all_items:
                    d = it.data(Qt.UserRole)
                    if d and d["pkg"] == pkg:
                        d["disabled"] = True; it.setData(Qt.UserRole, d)
                        tags = [tr(self._lang,"tag_system") if d["sys"] else tr(self._lang,"tag_user"), tr(self._lang,"tag_disabled")]
                        it.setText(f" {pkg}  [" + " · ".join(tags) + "]"); it.setForeground(QColor("#F87171")); it.setCheckState(Qt.Unchecked); break
            else: err += 1
        self.debloat_status.setText(tr(L,"status_disabled_ok",ok=ok)+(tr(L,"status_disabled_err",err=err) if err else ""))
        self.debloat_status.setStyleSheet(f"font-size:12px;color:{'#4ADE80' if not err else '#F59E0B'};")

    def _debloat_enable(self):
        selected = self._checked_items()
        if not selected: return
        L = self._lang; pkgs = [it.data(Qt.UserRole)["pkg"] for it in selected]
        body = tr(L,"enable_confirm_body")+"<br><br>"+"".join(f"&nbsp;&nbsp;• <code>{p}</code><br>" for p in pkgs[:15])
        if len(pkgs) > 15: body += f"&nbsp;&nbsp;... +{len(pkgs)-15}<br>"
        if self._msg_box(tr(L,"enable_confirm",n=len(pkgs)),tr(L,"enable_confirm",n=len(pkgs)),body,tr(L,"enable_ok"),tr(L,"btn_cancel"),"#4ADE80") != QMessageBox.Ok: return
        self.disable_btn.setEnabled(False); self.enable_btn.setEnabled(False)
        self.debloat_status.setText(tr(L,"status_enabling",n=len(pkgs))); QApplication.processEvents()
        ok = err = 0
        for item in selected:
            pkg = item.data(Qt.UserRole)["pkg"]
            out = run_adb_command(["shell","pm","enable",pkg])
            if "enabled" in out.lower() or "success" in out.lower():
                ok += 1
                for it in self._debloat_all_items:
                    d = it.data(Qt.UserRole)
                    if d and d["pkg"] == pkg:
                        d["disabled"] = False; it.setData(Qt.UserRole, d)
                        tags = [tr(self._lang,"tag_system") if d["sys"] else tr(self._lang,"tag_user")]
                        it.setText(f" {pkg}  [" + " · ".join(tags) + "]"); it.setForeground(QColor("#F59E0B") if d["sys"] else QColor("#D8DEE9")); it.setCheckState(Qt.Unchecked); break
            else: err += 1
        self.debloat_status.setText(tr(L,"status_enabled_ok",ok=ok)+(tr(L,"status_disabled_err",err=err) if err else ""))
        self.debloat_status.setStyleSheet(f"font-size:12px;color:{'#4ADE80' if not err else '#F59E0B'};")

    # ── ADB TAB ───────────────────────────────────────────────
    def create_adb_tab(self):
        L = self._lang; outer = QWidget(); outer.setObjectName("TabOuter")
        ol = QVBoxLayout(outer); ol.setContentsMargins(28,28,28,28); ol.setSpacing(16)
        self._tab_header(ol, tr(L,"tab_adb"), tr(L,"tab_adb_sub")); ol.addWidget(self._sec("sec_command_adb"))
        ir = QHBoxLayout(); pfx = QLabel("adb"); pfx.setStyleSheet("color:#7EB8F7;font-weight:bold;font-size:14px;padding:0 4px;")
        self.adb_input = QLineEdit(); self.adb_input.setPlaceholderText(tr(L,"adb_placeholder")); self.adb_input.returnPressed.connect(self.run_adb)
        rb = QPushButton(tr(L,"btn_run")); rb.setObjectName("PrimaryButton"); rb.setMinimumWidth(90); rb.setMaximumWidth(120); rb.clicked.connect(self.run_adb)
        cb = QPushButton(tr(L,"btn_clear")); cb.setMinimumWidth(70); cb.setMaximumWidth(100); cb.clicked.connect(lambda: self.adb_output.clear())
        ir.addWidget(pfx); ir.addWidget(self.adb_input, 1); ir.addWidget(rb); ir.addWidget(cb); ol.addLayout(ir)
        ol.addWidget(self._sec("sec_output_adb"))
        self.adb_output = TerminalOutput("# ..."); self.adb_output.setMinimumHeight(200); ol.addWidget(self.adb_output, 1)
        self.tabs.addTab(outer, "ADB")

    def run_adb(self):
        sub = self.adb_input.text().strip()
        if not sub: return
        cmd = sub if sub.startswith("adb ") else f"adb {sub}"
        self.adb_output.append_line(f"$ {cmd}"); self.adb_output.append_line(run_command(cmd).rstrip() or "(no output)"); self.adb_output.append_line("─"*40)

    # ── FASTBOOT TAB ──────────────────────────────────────────
    FB_PARTITION_MAP = {
        "boot":"boot_ab","init_boot":"init_boot_ab","vendor_boot":"vendor_boot_ab",
        "recovery":"recovery","system":"system_ab","system_ext":"system_ext_ab",
        "vendor":"vendor_ab","product":"product_ab","odm":"odm_ab","dtbo":"dtbo_ab",
        "vbmeta":"vbmeta_ab","vbmeta_system":"vbmeta_system_ab","vbmeta_vendor":"vbmeta_vendor_ab",
        "super":"super","userdata":"userdata","metadata":"metadata","persist":"persist",
        "modem":"modem_ab","radio":"modem_ab","bluetooth":"bluetooth_ab","dsp":"dsp_ab",
        "xbl":"xbl_ab","abl":"abl_ab",
    }

    def _guess_partition(self, filename):
        name = os.path.splitext(os.path.basename(filename))[0].lower()
        if name in self.FB_PARTITION_MAP: return self.FB_PARTITION_MAP[name], True
        for key, part in self.FB_PARTITION_MAP.items():
            if name.startswith(key) or name.endswith(key): return part, True
        return None, False

    def create_fastboot_tab(self):
        L = self._lang; outer = QWidget(); outer.setObjectName("TabOuter")
        ol = QVBoxLayout(outer); ol.setContentsMargins(28,28,28,28); ol.setSpacing(16)
        self._tab_header(ol, tr(L,"tab_fastboot"), tr(L,"tab_fastboot_sub"))
        ol.addWidget(self._sec("sec_fb_file"))
        file_frame = QFrame(); file_frame.setObjectName("InstallFrame")
        ffl = QVBoxLayout(file_frame); ffl.setContentsMargins(16,14,16,14); ffl.setSpacing(12)
        file_row = QHBoxLayout()
        self.fb_file_input = QLineEdit(); self.fb_file_input.setPlaceholderText("Selecione um arquivo .img, .zip, .bin ..."); self.fb_file_input.setReadOnly(True)
        browse_btn = QPushButton("📂  Selecionar Arquivo"); browse_btn.setMinimumWidth(160); browse_btn.setMaximumWidth(200); browse_btn.clicked.connect(self._fb_browse_file)
        file_row.addWidget(self.fb_file_input, 1); file_row.addWidget(browse_btn); ffl.addLayout(file_row)
        self.fb_detect_label = QLabel(""); self.fb_detect_label.setStyleSheet("font-size:11px;color:#4B5563;padding:2px 0;"); ffl.addWidget(self.fb_detect_label)
        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet("background:#1E2028;"); ffl.addWidget(sep)
        cmd_lbl = QLabel("Comando fastboot:"); cmd_lbl.setStyleSheet("font-size:11px;color:#4B5563;letter-spacing:1px;"); ffl.addWidget(cmd_lbl)
        cmd_row = QHBoxLayout()
        pfx = QLabel("fastboot"); pfx.setStyleSheet("color:#F59E0B;font-weight:bold;font-size:13px;padding:0 4px;")
        self.fastboot_input = QLineEdit(); self.fastboot_input.setPlaceholderText("flash boot_ab \"/caminho/boot.img\""); self.fastboot_input.returnPressed.connect(self.run_fastboot)
        cmd_row.addWidget(pfx); cmd_row.addWidget(self.fastboot_input, 1); ffl.addLayout(cmd_row)
        action_row = QHBoxLayout(); action_row.setSpacing(10)
        self.fb_flash_btn = QPushButton("⚡  Executar Flash"); self.fb_flash_btn.setObjectName("SuccessButton"); self.fb_flash_btn.setFixedHeight(38); self.fb_flash_btn.setMinimumWidth(160); self.fb_flash_btn.clicked.connect(self.run_fastboot)
        clear_cmd_btn = QPushButton("✕  Limpar"); clear_cmd_btn.setFixedHeight(38); clear_cmd_btn.setMaximumWidth(100); clear_cmd_btn.clicked.connect(self._fb_clear_selection)
        action_row.addWidget(self.fb_flash_btn); action_row.addWidget(clear_cmd_btn); action_row.addStretch(); ffl.addLayout(action_row)
        ol.addWidget(file_frame)
        ol.addWidget(self._sec("sec_quick"))
        qr = QHBoxLayout(); qr.setSpacing(8)
        def qbtn(lbl, obj=None, fn=None):
            b = QPushButton(lbl); b.setFixedHeight(34); b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            if obj: b.setObjectName(obj)
            if fn: b.clicked.connect(fn)
            return b
        for b in [qbtn(tr(L,"btn_devices"),   fn=lambda: self._run_fb_cmd("fastboot devices")),
                  qbtn(tr(L,"btn_reboot"),     fn=lambda: self._run_fb_cmd("fastboot reboot")),
                  qbtn(tr(L,"btn_bootloader"), fn=lambda: self._run_fb_cmd("fastboot reboot-bootloader")),
                  qbtn(tr(L,"btn_recovery_warn"),"DangerButton",fn=lambda: self._run_fb_cmd("fastboot reboot recovery"))]:
            qr.addWidget(b)
        ol.addLayout(qr)
        ol.addWidget(self._sec("sec_output_fb"))
        self.fastboot_output = TerminalOutput("# ...")
        self.fastboot_output.setStyleSheet("QTextEdit#TerminalOutput{color:#F59E0B;background-color:#080A0D;border:1px solid #1A1D24;border-radius:10px;padding:14px;font-size:12px;}")
        ol.addWidget(self.fastboot_output, 1)
        self.tabs.addTab(outer, "Fastboot")

    def _fb_browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self,"Selecionar arquivo para flash","","Imagens & ZIPs (*.img *.bin *.zip);;Todos (*)")
        if not path: return
        self.fb_file_input.setText(path)
        fname = os.path.basename(path)
        partition, found = self._guess_partition(path)
        if found:
            cmd = f'flash {partition} "{path}"'
            self.fastboot_input.setText(cmd)
            self.fb_detect_label.setText(f"✓  Partição detectada:  <b style='color:#4ADE80'>{partition}</b>  →  <span style='color:#9CA3AF'>fastboot flash {partition} \"{fname}\"</span>")
            self.fb_detect_label.setTextFormat(Qt.RichText)
        else:
            self.fastboot_input.setText(f'flash <PARTIÇÃO> "{path}"'); self.fastboot_input.setFocus()
            start = self.fastboot_input.text().index("<"); end = self.fastboot_input.text().index(">") + 1
            self.fastboot_input.setSelection(start, end - start)
            self.fb_detect_label.setText(tr(L,"fb_partition_unknown",fname=fname))
            self.fb_detect_label.setTextFormat(Qt.RichText); self.fb_detect_label.setStyleSheet("font-size:11px;color:#F59E0B;padding:2px 0;")

    def _fb_clear_selection(self):
        self.fb_file_input.clear(); self.fastboot_input.clear(); self.fb_detect_label.setText("")
        self.fb_detect_label.setStyleSheet("font-size:11px;color:#4B5563;padding:2px 0;")

    def _run_fb_cmd(self, cmd):
        self.fastboot_output.append_line(f"$ {cmd}")
        self.thread = FastbootThread(cmd); self.thread.output_signal.connect(self.fastboot_output.append_line); self.thread.start()

    def run_fastboot(self):
        sub = self.fastboot_input.text().strip()
        if not sub: return
        full = sub if sub.startswith("fastboot ") else f"fastboot {sub}"
        self._run_fb_cmd(full)

    # ── FLASH AOSP TAB ────────────────────────────────────────
    def create_rom_tab(self):
        L = self._lang; outer, layout = make_scroll_tab()
        self._tab_header(layout, tr(L,"tab_aosp"), tr(L,"tab_aosp_sub"))

        # ── Passo 1: selecionar ROM ───────────────────────────
        layout.addWidget(self._sec("sec_step1"))
        f = QFrame(); f.setObjectName("InstallFrame"); fl = QVBoxLayout(); fl.setContentsMargins(16,14,16,14); fl.setSpacing(10)
        rfr = QHBoxLayout(); self.rom_path_input = QLineEdit(); self.rom_path_input.setPlaceholderText(tr(L,"rom_placeholder")); self.rom_path_input.setReadOnly(True)
        rbtn = QPushButton(tr(L,"btn_select_rom")); rbtn.setMinimumWidth(120); rbtn.setMaximumWidth(160); rbtn.clicked.connect(self._browse_rom)
        rfr.addWidget(self.rom_path_input, 1); rfr.addWidget(rbtn); fl.addLayout(rfr)
        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet("background:#1E2028;"); fl.addWidget(sep)
        dlr = QHBoxLayout()
        dt = QLabel(tr(L,"dumper_label")); dt.setStyleSheet("color:#6B7280;font-size:11px;")
        dh = QLabel(tr(L,"dumper_hint")); dh.setStyleSheet("color:#374151;font-size:11px;")
        dlr.addWidget(dt); dlr.addStretch(); dlr.addWidget(dh); fl.addLayout(dlr)
        dpr = QHBoxLayout(); self.dumper_path_input = QLineEdit(); self.dumper_path_input.setText("payload-dumper-go"); self.dumper_path_input.setPlaceholderText(tr(L,"dumper_placeholder"))
        db = QPushButton(tr(L,"btn_select_exe")); db.setMinimumWidth(160); db.setMaximumWidth(220); db.setFixedHeight(36); db.clicked.connect(self._browse_dumper)
        dpr.addWidget(self.dumper_path_input, 1); dpr.addWidget(db); fl.addLayout(dpr); f.setLayout(fl); layout.addWidget(f)

        # ── Passo 2: extrair payload ──────────────────────────
        layout.addWidget(self._sec("sec_step2"))
        ef = QFrame(); ef.setObjectName("InstallFrame"); el = QVBoxLayout(); el.setContentsMargins(16,14,16,14); el.setSpacing(10)
        pr = QHBoxLayout(); plbl = QLabel(tr(L,"partitions_label")); plbl.setStyleSheet("color:#4B5563;font-size:12px;"); plbl.setMinimumWidth(80)
        self.partitions_input = QLineEdit(); self.partitions_input.setText("boot,init_boot,vendor_boot")
        pr.addWidget(plbl); pr.addWidget(self.partitions_input, 1); el.addLayout(pr)
        ear = QHBoxLayout(); self.extract_btn = QPushButton(tr(L,"btn_extract")); self.extract_btn.setObjectName("PrimaryButton"); self.extract_btn.setMinimumWidth(160); self.extract_btn.setMaximumWidth(220); self.extract_btn.setEnabled(False); self.extract_btn.clicked.connect(self._start_extraction)
        self.extract_status = QLabel(tr(L,"extract_start_msg")); self.extract_status.setStyleSheet("font-size:12px;color:#374151;"); self.extract_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        ear.addWidget(self.extract_btn); ear.addWidget(self.extract_status, 1); el.addLayout(ear)
        self.extract_log = TerminalOutput("# ..."); self.extract_log.setMinimumHeight(100); self.extract_log.setMaximumHeight(160); el.addWidget(self.extract_log)
        self.extract_progress = QProgressBar(); self.extract_progress.setRange(0,100); self.extract_progress.setValue(0); self.extract_progress.setFixedHeight(6); self.extract_progress.setVisible(False); self.extract_progress.setTextVisible(False)
        el.addWidget(self.extract_progress); ef.setLayout(el); layout.addWidget(ef)

        # ── Passo 3: flash ────────────────────────────────────
        layout.addWidget(self._sec("sec_step3"))
        ff = QFrame(); ff.setObjectName("FlashFrame"); ffl = QVBoxLayout(); ffl.setContentsMargins(16,14,16,14); ffl.setSpacing(8)
        fi = QLabel(tr(L,"flash_info")); fi.setStyleSheet("color:#374151;font-size:12px;"); ffl.addWidget(fi)
        self.flash_commands_display = QTextEdit(); self.flash_commands_display.setObjectName("TerminalOutput"); self.flash_commands_display.setReadOnly(True); self.flash_commands_display.setMinimumHeight(80); self.flash_commands_display.setMaximumHeight(130); ffl.addWidget(self.flash_commands_display)
        fbr = QHBoxLayout(); fbr.setSpacing(8)
        def fbtn(lbl, obj=None, enabled=True):
            b = QPushButton(lbl); b.setMinimumWidth(110); b.setMaximumWidth(200); b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            if obj: b.setObjectName(obj)
            b.setEnabled(enabled); return b
        self.reboot_fb_btn  = fbtn(tr(L,"btn_reboot_fb"), "DangerButton"); self.reboot_fb_btn.clicked.connect(self._reboot_fastboot)
        self.flash_btn      = fbtn(tr(L,"btn_flash_now"), "PrimaryButton", enabled=False); self.flash_btn.clicked.connect(self._do_flash)
        self.reboot_rec_btn = fbtn(tr(L,"btn_reboot_rec"), "DangerButton", enabled=False); self.reboot_rec_btn.clicked.connect(self._reboot_recovery)
        self.cleanup_btn    = fbtn(tr(L,"btn_cleanup"), enabled=False); self.cleanup_btn.clicked.connect(self._cleanup_extracted)
        self.sideload_btn   = fbtn(tr(L,"btn_flash_rom"), "SuccessButton"); self.sideload_btn.clicked.connect(self._do_sideload)
        self.reboot_btn     = fbtn(tr(L,"btn_reboot_device"), "DangerButton"); self.reboot_btn.clicked.connect(self._reboot_device)
        for b in (self.reboot_fb_btn, self.flash_btn, self.reboot_rec_btn, self.cleanup_btn, self.sideload_btn, self.reboot_btn): fbr.addWidget(b)
        ffl.addLayout(fbr)
        self.flash_status = QLabel(""); self.flash_status.setStyleSheet("font-size:12px;color:#374151;"); ffl.addWidget(self.flash_status)
        self.sideload_notice = QLabel(tr(L,"sideload_notice")); self.sideload_notice.setObjectName("SideloadNotice"); self.sideload_notice.setVisible(False); self.sideload_notice.setWordWrap(True); ffl.addWidget(self.sideload_notice)
        self.flash_log = TerminalOutput("# ..."); self.flash_log.setMinimumHeight(140)
        self.flash_log.setStyleSheet("QTextEdit#TerminalOutput{color:#F59E0B;background-color:#080A0D;border:1px solid #1A1D24;border-radius:10px;padding:14px;font-size:12px;}")
        ffl.addWidget(self.flash_log)
        self.flash_progress = QProgressBar(); self.flash_progress.setRange(0,100); self.flash_progress.setValue(0); self.flash_progress.setFixedHeight(6); self.flash_progress.setVisible(False); self.flash_progress.setTextVisible(False)
        ffl.addWidget(self.flash_progress); ff.setLayout(ffl); layout.addWidget(ff)
        self._extracted_dir = None; self._extracted_files = {}
        self.tabs.addTab(outer, "Flash AOSP")

    def _browse_rom(self):
        path, _ = QFileDialog.getOpenFileName(self,"Selecionar ROM","","ZIP (*.zip);;Todos (*)")
        if path: self.rom_path_input.setText(path); self.extract_btn.setEnabled(True); self.extract_status.setText("ROM selecionada."); self.extract_status.setStyleSheet("font-size:12px;color:#9CA3AF;")

    def _browse_dumper(self):
        path, _ = QFileDialog.getOpenFileName(self,"Localizar payload-dumper-go","","Executáveis (*)")
        if path: self.dumper_path_input.setText(path)

    def _start_extraction(self):
        rom_path = self.rom_path_input.text().strip()
        if not rom_path or not os.path.isfile(rom_path): self.extract_status.setText(tr(L,"log_no_rom")); return
        dumper_exe = self.dumper_path_input.text().strip() or "payload-dumper-go"
        self.extract_btn.setEnabled(False); self.flash_btn.setEnabled(False)
        self.flash_commands_display.clear(); self.extract_log.clear(); self._extracted_files = {}
        self.extract_progress.setValue(0); self.extract_progress.setVisible(True)
        self.extract_status.setText("⏳  Extraindo..."); self.extract_status.setStyleSheet("font-size:12px;color:#F59E0B;"); QApplication.processEvents()
        work_dir = tempfile.mkdtemp(prefix="rom_manager_"); self._extracted_dir = work_dir
        self.extract_log.append_line(tr(L,"log_work_dir",path=work_dir)); QApplication.processEvents()
        payload_path = os.path.join(work_dir, "payload.bin")
        try:
            self.extract_log.append_line(tr(L,"log_opening_zip")); QApplication.processEvents()
            with zipfile.ZipFile(rom_path, "r") as z:
                entries = [n for n in z.namelist() if n.endswith("payload.bin")]
                if not entries:
                    self.extract_log.append_line(tr(L,"log_payload_not_found"))
                    self.extract_status.setText(tr(L,"extract_status_no_payload")); self.extract_status.setStyleSheet("font-size:12px;color:#F87171;")
                    self.extract_btn.setEnabled(True); self.extract_progress.setVisible(False); return
                entry = entries[0]; self.extract_log.append_line(f"✓  {entry}"); QApplication.processEvents()
                z.extract(entry, work_dir)
                extracted = os.path.join(work_dir, entry)
                if extracted != payload_path: shutil.move(extracted, payload_path)
            self.extract_log.append_line(tr(L,"log_payload_ok",size=os.path.getsize(payload_path)//1024//1024))
            self.extract_progress.setValue(15); QApplication.processEvents()
        except Exception as e:
            self.extract_log.append_line(f"✗  {e}"); self.extract_status.setText("✗  Erro ao extrair."); self.extract_status.setStyleSheet("font-size:12px;color:#F87171;")
            self.extract_btn.setEnabled(True); self.extract_progress.setVisible(False); return
        partitions = [p.strip() for p in self.partitions_input.text().split(",") if p.strip()]
        out_dir = os.path.join(work_dir, "extracted"); os.makedirs(out_dir, exist_ok=True)
        self._extract_thread = RomExtractThread(dumper_exe, out_dir, partitions, payload_path)
        self._extract_thread.log_signal.connect(self.extract_log.append_line)
        self._extract_thread.progress_signal.connect(lambda v: self.extract_progress.setValue(15+int(v*0.85)))
        self._extract_thread.done_signal.connect(self._on_extraction_done)
        self._extract_thread.start()

    def _on_extraction_done(self, found, error):
        self.extract_progress.setVisible(False)
        if error: self.extract_status.setText(tr(L,"extract_status_err")+f" {error}"); self.extract_status.setStyleSheet("font-size:12px;color:#F87171;"); self.extract_btn.setEnabled(True); return
        self._extracted_files = found
        if not found: self.extract_status.setText(tr(L,"extract_status_none")); self.extract_status.setStyleSheet("font-size:12px;color:#F59E0B;"); self.extract_btn.setEnabled(True); return
        self.extract_log.append_line(tr(L,"log_partitions_found",n=len(found)))
        for name, path in found.items(): self.extract_log.append_line(f"   • {name}.img  ({os.path.getsize(path)/1024/1024:.1f} MB)")
        self.extract_status.setText(tr(L,"extract_status_ok",n=len(found))); self.extract_status.setStyleSheet("font-size:12px;color:#4ADE80;")
        priority = ["init_boot","boot","vendor_boot"]
        ordered = [p for p in priority if p in found] + [p for p in found if p not in priority]
        self.flash_commands_display.setPlainText("\n".join(f'fastboot flash {p}_ab "{found[p]}"' for p in ordered))
        self.flash_btn.setEnabled(True); self.cleanup_btn.setEnabled(True); self.extract_btn.setEnabled(True)

    def _do_flash(self):
        if not self._extracted_files: return
        if not run_command("fastboot devices").strip():
            self.flash_log.append_line(tr(L,"log_no_fastboot_dev")); return
        self.flash_btn.setEnabled(False); self.flash_log.clear(); self.flash_progress.setValue(0); self.flash_progress.setVisible(True)
        self.flash_status.setText("⏳  Flash..."); self.flash_status.setStyleSheet("font-size:12px;color:#F59E0B;"); QApplication.processEvents()
        priority = ["init_boot","boot","vendor_boot"]
        ordered  = [p for p in priority if p in self._extracted_files] + [p for p in self._extracted_files if p not in priority]
        commands = [["fastboot","flash",f"{p}_ab",self._extracted_files[p]] for p in ordered]
        self._flash_thread = SequentialFastbootThread(commands)
        self._flash_thread.log_signal.connect(self.flash_log.append_line)
        self._flash_thread.progress_signal.connect(self.flash_progress.setValue)
        self._flash_thread.done_signal.connect(self._on_flash_done)
        self._flash_thread.start()

    def _on_flash_done(self, success):
        self.flash_progress.setVisible(False)
        if success: self.flash_status.setText("✓  Flash concluído!"); self.flash_status.setStyleSheet("font-size:12px;color:#4ADE80;"); self.reboot_rec_btn.setEnabled(True)
        else: self.flash_status.setText("✗  Erro durante flash."); self.flash_status.setStyleSheet("font-size:12px;color:#F87171;")
        self.flash_btn.setEnabled(True)

    def _reboot_fastboot(self): self.flash_log.append_line("\n$ adb reboot fastboot"); run_command("adb reboot fastboot"); self.flash_log.append_line("✓")
    def _reboot_recovery(self): self.flash_log.append_line("\n$ fastboot reboot recovery"); run_command("fastboot reboot recovery"); self.flash_log.append_line("✓")
    def _reboot_device(self):
        import subprocess
        result = subprocess.run(["fastboot", "reboot"], capture_output=True, text=True, errors="ignore")
        out = (result.stdout + result.stderr).strip()
        log = getattr(self, "flash_log", None) or getattr(self, "hyper_flash_log", None)
        if log: log.append_line("\n$ fastboot reboot"); log.append_line(out if out else "✓  Reboot enviado.")

    def _do_sideload(self):
        rom_path = self.rom_path_input.text().strip()
        if not rom_path or not os.path.isfile(rom_path): self.flash_log.append_line(tr(L,"log_no_rom_selected")); return
        L = self._lang; rom_name = os.path.basename(rom_path)
        msg = QMessageBox(self); msg.setWindowTitle(tr(L,"sideload_title")); msg.setIcon(QMessageBox.Warning)
        msg.setText(tr(L,"sideload_bold")); msg.setInformativeText(tr(L,"sideload_body")+f"<span style='color:#9CA3AF;'>ROM: {rom_name}</span>")
        msg.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        msg.button(QMessageBox.Ok).setText(tr(L,"btn_confirm_flash")); msg.button(QMessageBox.Cancel).setText(tr(L,"btn_cancel"))
        msg.setStyleSheet("QMessageBox{background:#111318;color:#D8DEE9;}QMessageBox QLabel{color:#D8DEE9;font-size:13px;min-width:380px;}QPushButton{background:#1A1D25;border:1px solid #252933;border-radius:8px;padding:8px 18px;color:#9CA3AF;font-size:12px;min-width:160px;}QPushButton:hover{background:#1E2330;color:#D8DEE9;}QPushButton:default{background:#0F2A1A;border-color:#1A5C32;color:#4ADE80;font-weight:bold;}")
        if msg.exec() != QMessageBox.Ok: return
        self.sideload_notice.setVisible(True); self.sideload_btn.setEnabled(False); QApplication.processEvents()
        self.flash_log.append_line(f"\n$ adb sideload \"{rom_path}\""); self.flash_log.append_line("⏳  Enviando..."); QApplication.processEvents()
        self._sideload_thread = FastbootThread(f'adb sideload "{rom_path}"')
        self._sideload_thread.output_signal.connect(self.flash_log.append_line)
        self._sideload_thread.finished.connect(lambda: (self.sideload_btn.setEnabled(True), self.flash_log.append_line(tr(L,"log_sideload_done"))))
        self._sideload_thread.start()

    def _cleanup_extracted(self):
        if self._extracted_dir and os.path.isdir(self._extracted_dir):
            try:
                shutil.rmtree(self._extracted_dir); self.extract_log.append_line(tr(L,"log_removed"))
                self._extracted_dir = None; self._extracted_files = {}
                self.flash_btn.setEnabled(False); self.cleanup_btn.setEnabled(False); self.reboot_rec_btn.setEnabled(False)
                self.flash_commands_display.clear(); self.flash_status.setText("🗑  Removido."); self.flash_status.setStyleSheet("font-size:12px;color:#9CA3AF;")
            except Exception as e: self.extract_log.append_line(tr(L,"log_extract_err",err=e))

    # ── HYPEROS TAB ───────────────────────────────────────────
    def create_hyperos_tab(self):
        L = self._lang; outer, layout = make_scroll_tab()
        self._tab_header(layout, tr(L,"tab_hyperos"), tr(L,"tab_hyperos_sub"))
        layout.addWidget(self._sec("sec_hyper_step1"))
        f = QFrame(); f.setObjectName("InstallFrame"); fl = QVBoxLayout(); fl.setContentsMargins(16,14,16,14); fl.setSpacing(10)
        rfr = QHBoxLayout(); self.hyper_rom_input = QLineEdit(); self.hyper_rom_input.setPlaceholderText(tr(L,"hyper_placeholder")); self.hyper_rom_input.setReadOnly(True)
        hb = QPushButton(tr(L,"btn_select_rom")); hb.setObjectName("PrimaryButton"); hb.setMinimumWidth(120); hb.setMaximumWidth(160); hb.clicked.connect(self._hyper_browse_rom)
        rfr.addWidget(self.hyper_rom_input, 1); rfr.addWidget(hb); fl.addLayout(rfr); f.setLayout(fl); layout.addWidget(f)
        layout.addWidget(self._sec("sec_hyper_step2"))
        ef = QFrame(); ef.setObjectName("InstallFrame"); el = QVBoxLayout(); el.setContentsMargins(16,14,16,14); el.setSpacing(10)
        ear = QHBoxLayout(); self.hyper_extract_btn = QPushButton(tr(L,"btn_hyper_extract")); self.hyper_extract_btn.setObjectName("PrimaryButton"); self.hyper_extract_btn.setMinimumWidth(150); self.hyper_extract_btn.setMaximumWidth(200); self.hyper_extract_btn.setEnabled(False); self.hyper_extract_btn.clicked.connect(self._hyper_extract)
        self.hyper_extract_status = QLabel(tr(L,"hyper_start_msg")); self.hyper_extract_status.setStyleSheet("font-size:12px;color:#374151;"); self.hyper_extract_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        ear.addWidget(self.hyper_extract_btn); ear.addWidget(self.hyper_extract_status, 1); el.addLayout(ear)
        self.hyper_extract_log = TerminalOutput("# ..."); self.hyper_extract_log.setMinimumHeight(80); self.hyper_extract_log.setMaximumHeight(120); el.addWidget(self.hyper_extract_log)
        self.hyper_extract_progress = QProgressBar(); self.hyper_extract_progress.setRange(0,0); self.hyper_extract_progress.setFixedHeight(6); self.hyper_extract_progress.setVisible(False); self.hyper_extract_progress.setTextVisible(False)
        el.addWidget(self.hyper_extract_progress); ef.setLayout(el); layout.addWidget(ef)
        layout.addWidget(self._sec("sec_hyper_step3"))
        sf = QFrame(); sf.setObjectName("InstallFrame"); sl = QVBoxLayout(); sl.setContentsMargins(16,14,16,14); sl.setSpacing(10)
        sh = QLabel(tr(L,"scripts_hint")); sh.setStyleSheet("font-size:11px;color:#4B5563;"); sh.setWordWrap(True); sl.addWidget(sh)
        self.hyper_scripts_list = QListWidget(); self.hyper_scripts_list.setObjectName("ScriptsList"); self.hyper_scripts_list.setMinimumHeight(100); self.hyper_scripts_list.setMaximumHeight(180); self.hyper_scripts_list.setSelectionMode(QListWidget.SingleSelection); self.hyper_scripts_list.itemClicked.connect(self._hyper_script_selected)
        sl.addWidget(self.hyper_scripts_list); sf.setLayout(sl); layout.addWidget(sf)
        layout.addWidget(self._sec("sec_hyper_step4"))
        ff = QFrame(); ff.setObjectName("FlashFrame"); ffl = QVBoxLayout(); ffl.setContentsMargins(16,14,16,14); ffl.setSpacing(10)
        self.hyper_selected_label = QLabel(tr(L,"no_script")); self.hyper_selected_label.setStyleSheet("font-size:12px;color:#4B5563;font-style:italic;"); ffl.addWidget(self.hyper_selected_label)
        fbr = QHBoxLayout(); fbr.setSpacing(10)
        self.hyper_flash_btn = QPushButton(tr(L,"btn_run_script")); self.hyper_flash_btn.setObjectName("PrimaryButton"); self.hyper_flash_btn.setMinimumWidth(150); self.hyper_flash_btn.setMaximumWidth(220); self.hyper_flash_btn.setEnabled(False); self.hyper_flash_btn.clicked.connect(self._hyper_run_flash)
        self.hyper_cleanup_btn = QPushButton(tr(L,"btn_cleanup")); self.hyper_cleanup_btn.setMinimumWidth(120); self.hyper_cleanup_btn.setMaximumWidth(170); self.hyper_cleanup_btn.setEnabled(False); self.hyper_cleanup_btn.clicked.connect(self._hyper_cleanup)
        self.hyper_reboot_btn = QPushButton(tr(L,"btn_reboot_device")); self.hyper_reboot_btn.setObjectName("DangerButton"); self.hyper_reboot_btn.setMinimumWidth(110); self.hyper_reboot_btn.setMaximumWidth(160); self.hyper_reboot_btn.clicked.connect(self._reboot_device)
        self.hyper_flash_status = QLabel(""); self.hyper_flash_status.setStyleSheet("font-size:12px;color:#374151;"); self.hyper_flash_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        fbr.addWidget(self.hyper_flash_btn); fbr.addWidget(self.hyper_cleanup_btn); fbr.addWidget(self.hyper_reboot_btn); fbr.addWidget(self.hyper_flash_status, 1); ffl.addLayout(fbr)
        self.hyper_flash_log = TerminalOutput("# ..."); self.hyper_flash_log.setMinimumHeight(160)
        self.hyper_flash_log.setStyleSheet("QTextEdit#TerminalOutput{color:#E879F9;background-color:#080A0D;border:1px solid #1A1D24;border-radius:10px;padding:14px;font-size:12px;}")
        ffl.addWidget(self.hyper_flash_log); ff.setLayout(ffl); layout.addWidget(ff)
        self._hyper_extract_dir = None; self._hyper_selected_script = None
        self.tabs.addTab(outer, "Flash HyperOS")

    def _hyper_browse_rom(self):
        path, _ = QFileDialog.getOpenFileName(self,"Selecionar ROM HyperOS","","ZIP (*.zip);;Todos (*)")
        if path:
            self.hyper_rom_input.setText(path); self.hyper_extract_btn.setEnabled(True)
            self.hyper_extract_status.setText("ROM selecionada."); self.hyper_extract_status.setStyleSheet("font-size:12px;color:#9CA3AF;")
            self.hyper_scripts_list.clear(); self.hyper_flash_btn.setEnabled(False)
            self.hyper_selected_label.setText(tr(self._lang,"no_script")); self._hyper_selected_script = None

    def _hyper_extract(self):
        rom_path = self.hyper_rom_input.text().strip()
        if not rom_path or not os.path.isfile(rom_path): return
        self.hyper_extract_btn.setEnabled(False); self.hyper_scripts_list.clear(); self.hyper_extract_log.clear()
        self.hyper_flash_btn.setEnabled(False); self._hyper_selected_script = None
        self.hyper_selected_label.setText(tr(self._lang,"no_script"))
        self.hyper_extract_progress.setRange(0,0); self.hyper_extract_progress.setVisible(True)
        self.hyper_extract_status.setText("⏳  Extraindo..."); self.hyper_extract_status.setStyleSheet("font-size:12px;color:#F59E0B;"); QApplication.processEvents()
        if self._hyper_extract_dir and os.path.isdir(self._hyper_extract_dir):
            shutil.rmtree(self._hyper_extract_dir, ignore_errors=True)
        work_dir = tempfile.mkdtemp(prefix="hyperos_"); self._hyper_extract_dir = work_dir
        self.hyper_extract_log.append_line(tr(L,"log_work_dir",path=work_dir)); QApplication.processEvents()
        try:
            with zipfile.ZipFile(rom_path, "r") as z:
                self.hyper_extract_log.append_line(tr(L,"hyper_files",n=len(z.namelist()))); QApplication.processEvents(); z.extractall(work_dir)
            self.hyper_extract_log.append_line(tr(L,"hyper_extract_done")); QApplication.processEvents()
            scripts = [os.path.join(r,f) for r,_,files in os.walk(work_dir) for f in files if f.lower().endswith((".bat",".sh"))]
            self.hyper_extract_progress.setVisible(False)
            if not scripts:
                self.hyper_extract_log.append_line("⚠  Nenhum script encontrado."); self.hyper_extract_status.setText("⚠  Nenhum script."); self.hyper_extract_status.setStyleSheet("font-size:12px;color:#F59E0B;"); self.hyper_extract_btn.setEnabled(True); return
            self.hyper_extract_log.append_line(tr(L,"hyper_scripts_found",n=len(scripts)))
            for sp in sorted(scripts):
                rel = os.path.relpath(sp, work_dir); self.hyper_extract_log.append_line(f"   • {rel}")
                item = QListWidgetItem(f"  {rel}"); item.setData(Qt.UserRole, sp); self.hyper_scripts_list.addItem(item)
            self.hyper_extract_status.setText(f"✓  {len(scripts)} script(s). Selecione um."); self.hyper_extract_status.setStyleSheet("font-size:12px;color:#4ADE80;"); self.hyper_cleanup_btn.setEnabled(True)
        except Exception as e:
            self.hyper_extract_progress.setVisible(False); self.hyper_extract_log.append_line(f"✗  {e}"); self.hyper_extract_status.setText("✗  Erro."); self.hyper_extract_status.setStyleSheet("font-size:12px;color:#F87171;")
        self.hyper_extract_btn.setEnabled(True)

    def _hyper_script_selected(self, item):
        sp = item.data(Qt.UserRole); self._hyper_selected_script = sp
        rel = os.path.relpath(sp, self._hyper_extract_dir or "")
        self.hyper_selected_label.setText(f"▶  {rel}"); self.hyper_selected_label.setStyleSheet("font-size:12px;color:#E879F9;font-style:normal;"); self.hyper_flash_btn.setEnabled(True)

    def _hyper_run_flash(self):
        if not self._hyper_selected_script or not os.path.isfile(self._hyper_selected_script):
            self.hyper_flash_status.setText(tr(L,"hyper_no_script")); return
        out = run_command("adb devices").strip()
        if not [l for l in out.splitlines() if l.strip() and "List of devices" not in l]:
            self.hyper_flash_log.append_line("✗  Nenhum dispositivo ADB!"); self.hyper_flash_status.setText("✗  Dispositivo não encontrado."); self.hyper_flash_status.setStyleSheet("font-size:12px;color:#F87171;"); return
        script = self._hyper_selected_script; sdir = os.path.dirname(script); sname = os.path.basename(script)
        if sname.lower().endswith(".bat"):
            cmd = f'cd /d "{sdir}" && "{sname}"' if sys.platform == "win32" else f'cd "{sdir}" && wine "{sname}"'
        else:
            cmd = f'cd "{sdir}" && bash "{sname}"'
        self.hyper_flash_log.clear(); self.hyper_flash_log.append_line(f"$ {cmd}\n")
        self.hyper_flash_btn.setEnabled(False); self.hyper_flash_status.setText("⏳  Executando..."); self.hyper_flash_status.setStyleSheet("font-size:12px;color:#F59E0B;"); QApplication.processEvents()
        self._hyper_flash_thread = FastbootThread(cmd)
        self._hyper_flash_thread.output_signal.connect(self.hyper_flash_log.append_line)
        self._hyper_flash_thread.finished.connect(lambda: (self.hyper_flash_btn.setEnabled(True), self.hyper_flash_status.setText("✓  Script finalizado."), self.hyper_flash_status.setStyleSheet("font-size:12px;color:#4ADE80;")))
        self._hyper_flash_thread.start()

    def _hyper_cleanup(self):
        if self._hyper_extract_dir and os.path.isdir(self._hyper_extract_dir):
            try:
                shutil.rmtree(self._hyper_extract_dir); self.hyper_extract_log.append_line(tr(L,"log_removed"))
                self._hyper_extract_dir = None; self._hyper_selected_script = None; self.hyper_scripts_list.clear()
                self.hyper_flash_btn.setEnabled(False); self.hyper_cleanup_btn.setEnabled(False)
                self.hyper_selected_label.setText(tr(self._lang,"no_script")); self.hyper_selected_label.setStyleSheet("font-size:12px;color:#4B5563;font-style:italic;")
                self.hyper_flash_status.setText("🗑  Removido."); self.hyper_flash_status.setStyleSheet("font-size:12px;color:#9CA3AF;")
            except Exception as e: self.hyper_extract_log.append_line(tr(L,"log_extract_err",err=e))


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(QPalette.Window,          QColor("#0C0E12"))
    palette.setColor(QPalette.WindowText,      QColor("#D8DEE9"))
    palette.setColor(QPalette.Base,            QColor("#111318"))
    palette.setColor(QPalette.AlternateBase,   QColor("#151820"))
    palette.setColor(QPalette.Text,            QColor("#D8DEE9"))
    palette.setColor(QPalette.Button,          QColor("#1A1D25"))
    palette.setColor(QPalette.ButtonText,      QColor("#9CA3AF"))
    palette.setColor(QPalette.Highlight,       QColor("#1C2E4A"))
    palette.setColor(QPalette.HighlightedText, QColor("#7EB8F7"))
    app.setPalette(palette)
    window = RomManager()
    window.show()
    sys.exit(app.exec())