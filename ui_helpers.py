from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QHBoxLayout,
    QLabel, QSizePolicy, QGraphicsDropShadowEffect, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

# ===============================
# HELPERS
# ===============================
def make_scroll_tab():
    outer = QWidget(); outer.setObjectName("TabOuter")
    ol = QVBoxLayout(outer); ol.setContentsMargins(0,0,0,0); ol.setSpacing(0)
    scroll = QScrollArea(); scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setFrameShape(QFrame.NoFrame); scroll.setObjectName("TabScrollArea")
    inner = QWidget(); inner.setObjectName("TabInner")
    il = QVBoxLayout(inner); il.setContentsMargins(28,28,28,28); il.setSpacing(20)
    scroll.setWidget(inner); ol.addWidget(scroll)
    return outer, il

class InfoCard(QFrame):
    def __init__(self, title, icon=""):
        super().__init__(); self.setObjectName("InfoCard")
        self.setMinimumHeight(90); self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(); layout.setContentsMargins(16,14,16,14); layout.setSpacing(6)
        header = QHBoxLayout()
        if icon:
            il = QLabel(icon); il.setObjectName("cardIcon"); header.addWidget(il)
        tl = QLabel(title.upper()); tl.setObjectName("cardTitle"); header.addWidget(tl); header.addStretch()
        self.value = QLabel("—"); self.value.setObjectName("cardValue"); self.value.setWordWrap(True)
        layout.addLayout(header); layout.addWidget(self.value); layout.addStretch(); self.setLayout(layout)
        sh = QGraphicsDropShadowEffect(); sh.setBlurRadius(20); sh.setOffset(0,4); sh.setColor(QColor(0,0,0,80))
        self.setGraphicsEffect(sh)

class TerminalOutput(QTextEdit):
    def __init__(self, placeholder=""):
        super().__init__(); self.setReadOnly(True); self.setObjectName("TerminalOutput")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if placeholder: self.setPlaceholderText(placeholder)
    def append_line(self, text):
        self.append(text.rstrip()); self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

class SectionHeader(QLabel):
    def __init__(self, text): super().__init__(text); self.setObjectName("SectionHeader")