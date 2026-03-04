import platform
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFrame, QTextEdit,
    QProgressBar, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from config import APP_VERSION
from threads import (
    InstallPayloadDumperThread,
    InstallPlatformToolsThread
)

# ===============================
# DIALOG BASE (helper interno)
# ===============================
class _BaseInstallDialog(QDialog):
    """Base reutilizável para dialogs de instalação automática."""
    def __init__(self, parent, title, header_text, header_color, desc_html,
                 manual_url, thread_class, log_color="#7EB8F7", bar_colors=("#7EB8F7","#4ADE80"),
                 btn_color=("#0F2A1A","#1A5C32","#4ADE80","#153520")):
        super().__init__(parent)
        self.setWindowTitle(title); self.setMinimumWidth(560); self.setModal(True)
        self._exe_path = None
        self._thread_class = thread_class

        layout = QVBoxLayout(self); layout.setSpacing(14); layout.setContentsMargins(28,24,28,24)

        hdr = QLabel(header_text)
        hdr.setStyleSheet(f"font-size:15px;font-weight:bold;color:{header_color};")
        layout.addWidget(hdr)

        desc = QLabel(desc_html); desc.setWordWrap(True)
        desc.setStyleSheet("font-size:13px;color:#9CA3AF;line-height:1.6;")
        desc.setTextFormat(Qt.RichText); layout.addWidget(desc)

        sys_lbl = QLabel(f"Sistema detectado:  <b>{platform.system()} {platform.machine()}</b>")
        sys_lbl.setStyleSheet("font-size:11px;color:#4B5563;"); sys_lbl.setTextFormat(Qt.RichText)
        layout.addWidget(sys_lbl)

        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet("background:#1E2028;")
        layout.addWidget(sep)

        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(160)
        self.log.setVisible(False)
        self.log.setStyleSheet(f"QTextEdit{{background:#080A0D;border:1px solid #1A1D24;border-radius:8px;padding:10px;color:{log_color};font-size:12px;font-family:'Consolas','Courier New',monospace;}}")
        layout.addWidget(self.log)

        self.progress = QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0)
        self.progress.setFixedHeight(6); self.progress.setVisible(False); self.progress.setTextVisible(False)
        c1, c2 = bar_colors
        self.progress.setStyleSheet(f"QProgressBar{{background:#1A1D25;border:none;border-radius:3px;}}QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {c1},stop:1 {c2});border-radius:3px;}}")
        layout.addWidget(self.progress)

        self.status_lbl = QLabel(""); self.status_lbl.setStyleSheet("font-size:12px;color:#4B5563;")
        layout.addWidget(self.status_lbl)

        btn_row = QHBoxLayout(); btn_row.setSpacing(10)
        self.skip_btn = QPushButton("Pular por enquanto")
        self.skip_btn.setStyleSheet("QPushButton{background:#1A1D25;border:1px solid #252933;border-radius:8px;padding:9px 20px;color:#6B7280;font-size:12px;}QPushButton:hover{background:#1E2330;color:#D8DEE9;}")
        self.skip_btn.clicked.connect(self.reject)

        self.manual_btn = QPushButton("📥  Instalar manualmente")
        self.manual_btn.setStyleSheet("QPushButton{background:#1A1D25;border:1px solid #2B4778;border-radius:8px;padding:9px 20px;color:#7EB8F7;font-size:12px;}QPushButton:hover{background:#1E2330;border-color:#3B6BAA;}")
        self.manual_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(manual_url)))

        bg, border, fg, hover_bg = btn_color
        self.install_btn = QPushButton("⚡  Instalar Automaticamente")
        self.install_btn.setStyleSheet(f"QPushButton{{background:{bg};border:1px solid {border};border-radius:8px;padding:9px 22px;color:{fg};font-size:13px;font-weight:bold;}}QPushButton:hover{{background:{hover_bg};}}QPushButton:disabled{{background:#111318;border-color:#1E2028;color:#374151;}}")
        self.install_btn.clicked.connect(self._start_install)

        btn_row.addWidget(self.skip_btn); btn_row.addWidget(self.manual_btn)
        btn_row.addStretch(); btn_row.addWidget(self.install_btn)
        layout.addLayout(btn_row)
        self.setStyleSheet("QDialog{background:#111318;color:#D8DEE9;}QLabel{color:#D8DEE9;font-family:'Consolas','Courier New',monospace;}")
        self._fg = fg; self._bg = bg; self._border = border; self._hover_bg = hover_bg

    def _start_install(self):
        self.install_btn.setEnabled(False); self.skip_btn.setEnabled(False); self.manual_btn.setEnabled(False)
        self.log.setVisible(True); self.progress.setVisible(True)
        self.status_lbl.setText("⏳  Iniciando instalação...")
        self._thread = self._thread_class()
        self._thread.log_signal.connect(lambda t: (self.log.append(t), self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())))
        self._thread.progress_signal.connect(self.progress.setValue)
        self._thread.done_signal.connect(self._on_done)
        self._thread.start()

    def _on_done(self, success, exe_path):
        self._exe_path = exe_path
        if success:
            self.status_lbl.setText("✅  Instalado com sucesso!")
            self.status_lbl.setStyleSheet("font-size:12px;color:#4ADE80;")
            close_btn = QPushButton("✓  Fechar e continuar")
            close_btn.setStyleSheet(f"QPushButton{{background:{self._bg};border:1px solid {self._border};border-radius:8px;padding:9px 22px;color:{self._fg};font-size:13px;font-weight:bold;}}QPushButton:hover{{background:{self._hover_bg};}}")
            close_btn.clicked.connect(self.accept)
            self.layout().addWidget(close_btn)
        else:
            self.status_lbl.setText("✗  Falha. Tente instalar manualmente.")
            self.status_lbl.setStyleSheet("font-size:12px;color:#F87171;")
            self.skip_btn.setEnabled(True); self.manual_btn.setEnabled(True)

    def get_exe_path(self): return self._exe_path


# ===============================
# DIALOG: INSTALL PAYLOAD-DUMPER-GO
# ===============================
class InstallPayloadDumperDialog(_BaseInstallDialog):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="🗜  payload-dumper-go não encontrado",
            header_text="🗜  payload-dumper-go não encontrado",
            header_color="#F87171",
            desc_html="O <b>payload-dumper-go</b> é necessário para extrair partições de ROMs AOSP.<br><br>"
                      "Clique em <b style='color:#4ADE80'>Instalar Automaticamente</b> para baixar "
                      "a versão mais recente direto do GitHub (<i>ssut/payload-dumper-go</i>).",
            manual_url="https://github.com/ssut/payload-dumper-go/releases",
            thread_class=InstallPayloadDumperThread,
            log_color="#7EB8F7",
            bar_colors=("#7EB8F7","#4ADE80"),
            btn_color=("#0F2A1A","#1A5C32","#4ADE80","#153520"),
        )


# ===============================
# DIALOG: INSTALL MAGISKBOOT
# ===============================
# ===============================
# DIALOG: UPDATE
# ===============================
class UpdateDialog(QDialog):
    def __init__(self, parent, version, url, notes):
        super().__init__(parent)
        self.url = url
        self.setWindowTitle("⚡ Nova versão disponível"); self.setMinimumWidth(500); self.setModal(True)
        layout = QVBoxLayout(self); layout.setSpacing(16); layout.setContentsMargins(28,24,28,24)

        title = QLabel(f"🎉  Versão <b style='color:#7EB8F7'>{version}</b> disponível!")
        title.setStyleSheet("font-size:16px;color:#E2E8F0;"); title.setTextFormat(Qt.RichText)
        layout.addWidget(title)

        cur = QLabel(f"Versão atual:  <span style='color:#4B5563'>{APP_VERSION}</span>")
        cur.setStyleSheet("font-size:12px;color:#6B7280;"); cur.setTextFormat(Qt.RichText)
        layout.addWidget(cur)

        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet("background:#1E2028;")
        layout.addWidget(sep)

        if notes.strip():
            notes_lbl = QLabel("📋  O que há de novo:")
            notes_lbl.setStyleSheet("font-size:11px;color:#4B5563;letter-spacing:1px;")
            layout.addWidget(notes_lbl)
            notes_box = QTextEdit(); notes_box.setReadOnly(True); notes_box.setPlainText(notes)
            notes_box.setMaximumHeight(130)
            notes_box.setStyleSheet("QTextEdit{background:#080A0D;border:1px solid #1A1D24;border-radius:8px;padding:10px;color:#9CA3AF;font-size:12px;}")
            layout.addWidget(notes_box)

        btn_row = QHBoxLayout(); btn_row.setSpacing(10)
        later = QPushButton("Lembrar depois")
        later.setStyleSheet("QPushButton{background:#1A1D25;border:1px solid #252933;border-radius:8px;padding:9px 20px;color:#6B7280;font-size:12px;}QPushButton:hover{background:#1E2330;color:#D8DEE9;}")
        later.clicked.connect(self.reject)
        open_btn = QPushButton("🔗  Abrir no GitHub")
        open_btn.setStyleSheet("QPushButton{background:#1C2E4A;border:1px solid #2B4778;border-radius:8px;padding:9px 20px;color:#7EB8F7;font-size:12px;font-weight:bold;}QPushButton:hover{background:#1F3457;border-color:#3B6BAA;color:#A8D0F8;}")
        open_btn.clicked.connect(lambda: (QDesktopServices.openUrl(QUrl(self.url)), self.accept()))
        btn_row.addWidget(later); btn_row.addStretch(); btn_row.addWidget(open_btn)
        layout.addLayout(btn_row)
        self.setStyleSheet("QDialog{background:#111318;color:#D8DEE9;}QLabel{color:#D8DEE9;font-family:'Consolas','Courier New',monospace;}")


# ===============================
# DIALOG: INSTALL PLATFORM TOOLS
# ===============================
class InstallToolsDialog(QDialog):
    def __init__(self, parent, missing):
        super().__init__(parent)
        self.setWindowTitle("⚠  Ferramentas não encontradas"); self.setMinimumWidth(560); self.setModal(True)
        self._install_dir = None
        layout = QVBoxLayout(self); layout.setSpacing(14); layout.setContentsMargins(28,24,28,24)

        header = QLabel("🔧  Android Platform Tools não encontrado")
        header.setStyleSheet("font-size:15px;font-weight:bold;color:#F87171;")
        layout.addWidget(header)

        desc = QLabel("As ferramentas <b>adb</b> e <b>fastboot</b> são necessárias para o ROM Manager Pro funcionar.<br><br>"
                      "Clique em <b style='color:#4ADE80'>Instalar Automaticamente</b> para baixar direto do servidor oficial do Google.")
        desc.setWordWrap(True); desc.setStyleSheet("font-size:13px;color:#9CA3AF;line-height:1.6;")
        desc.setTextFormat(Qt.RichText); layout.addWidget(desc)

        miss_frame = QFrame(); miss_frame.setStyleSheet("QFrame{background:#0D0F14;border:1px solid #2A1A1A;border-radius:8px;}")
        ml = QVBoxLayout(miss_frame); ml.setContentsMargins(12,10,12,10); ml.setSpacing(4)
        for tool in missing:
            lbl = QLabel(f"  ✗  <code>{tool}</code>  —  não encontrado")
            lbl.setStyleSheet("font-size:12px;color:#F87171;"); lbl.setTextFormat(Qt.RichText)
            ml.addWidget(lbl)
        layout.addWidget(miss_frame)

        sys_lbl = QLabel(f"Sistema detectado:  <b>{platform.system()} {platform.machine()}</b>")
        sys_lbl.setStyleSheet("font-size:11px;color:#4B5563;"); sys_lbl.setTextFormat(Qt.RichText)
        layout.addWidget(sys_lbl)

        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet("background:#1E2028;")
        layout.addWidget(sep)

        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(160); self.log.setVisible(False)
        self.log.setStyleSheet("QTextEdit{background:#080A0D;border:1px solid #1A1D24;border-radius:8px;padding:10px;color:#7EB8F7;font-size:12px;font-family:'Consolas','Courier New',monospace;}")
        layout.addWidget(self.log)

        self.progress = QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0)
        self.progress.setFixedHeight(6); self.progress.setVisible(False); self.progress.setTextVisible(False)
        self.progress.setStyleSheet("QProgressBar{background:#1A1D25;border:none;border-radius:3px;}QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #7EB8F7,stop:1 #4ADE80);border-radius:3px;}")
        layout.addWidget(self.progress)

        self.status_lbl = QLabel(""); self.status_lbl.setStyleSheet("font-size:12px;color:#4B5563;")
        layout.addWidget(self.status_lbl)

        btn_row = QHBoxLayout(); btn_row.setSpacing(10)
        self.skip_btn = QPushButton("Pular por enquanto")
        self.skip_btn.setStyleSheet("QPushButton{background:#1A1D25;border:1px solid #252933;border-radius:8px;padding:9px 20px;color:#6B7280;font-size:12px;}QPushButton:hover{background:#1E2330;color:#D8DEE9;}")
        self.skip_btn.clicked.connect(self.reject)
        self.manual_btn = QPushButton("📥  Instalar manualmente")
        self.manual_btn.setStyleSheet("QPushButton{background:#1A1D25;border:1px solid #2B4778;border-radius:8px;padding:9px 20px;color:#7EB8F7;font-size:12px;}QPushButton:hover{background:#1E2330;border-color:#3B6BAA;}")
        self.manual_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://developer.android.com/tools/releases/platform-tools")))
        self.install_btn = QPushButton("⚡  Instalar Automaticamente")
        self.install_btn.setStyleSheet("QPushButton{background:#0F2A1A;border:1px solid #1A5C32;border-radius:8px;padding:9px 22px;color:#4ADE80;font-size:13px;font-weight:bold;}QPushButton:hover{background:#153520;border-color:#22A355;color:#6EF0A0;}QPushButton:disabled{background:#111318;border-color:#1E2028;color:#374151;}")
        self.install_btn.clicked.connect(self._start_install)
        btn_row.addWidget(self.skip_btn); btn_row.addWidget(self.manual_btn)
        btn_row.addStretch(); btn_row.addWidget(self.install_btn)
        layout.addLayout(btn_row)
        self.setStyleSheet("QDialog{background:#111318;color:#D8DEE9;}QLabel{color:#D8DEE9;font-family:'Consolas','Courier New',monospace;}")

    def _start_install(self):
        self.install_btn.setEnabled(False); self.skip_btn.setEnabled(False); self.manual_btn.setEnabled(False)
        self.log.setVisible(True); self.progress.setVisible(True)
        self.status_lbl.setText("⏳  Iniciando instalação...")
        self._thread = InstallPlatformToolsThread()
        self._thread.log_signal.connect(lambda t: (self.log.append(t), self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())))
        self._thread.progress_signal.connect(self.progress.setValue)
        self._thread.done_signal.connect(self._on_done)
        self._thread.start()

    def _on_done(self, success, install_dir):
        self._install_dir = install_dir
        if success:
            self.status_lbl.setText("✅  Instalação concluída! ADB e Fastboot prontos.")
            self.status_lbl.setStyleSheet("font-size:12px;color:#4ADE80;")
            close_btn = QPushButton("✓  Fechar e continuar")
            close_btn.setStyleSheet("QPushButton{background:#0F2A1A;border:1px solid #1A5C32;border-radius:8px;padding:9px 22px;color:#4ADE80;font-size:13px;font-weight:bold;}QPushButton:hover{background:#153520;}")
            close_btn.clicked.connect(self.accept)
            self.layout().addWidget(close_btn)
        else:
            self.status_lbl.setText("✗  Falha. Tente instalar manualmente.")
            self.status_lbl.setStyleSheet("font-size:12px;color:#F87171;")
            self.skip_btn.setEnabled(True); self.manual_btn.setEnabled(True)

    def get_install_dir(self): return self._install_dir