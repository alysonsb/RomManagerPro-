import sys
import os
import subprocess
import platform
import urllib.request
import json
import zipfile
import tempfile
import shutil
import stat
import tarfile
import shlex
import re
from PySide6.QtCore import QThread, Signal

from config import (
    APP_VERSION, GITHUB_API_URL, GITHUB_RELEASES,
    MAGISK_API, PAYLOAD_DUMPER_RELEASES_API,
    PAYLOAD_DUMPER_ASSET_PATTERNS, PLATFORM_TOOLS_URLS
)
from utils import _apply_chmod

# ===============================
# THREAD: CHECK FOR UPDATES
# ===============================
class UpdateCheckerThread(QThread):
    result_signal = Signal(dict)
    def run(self):
        try:
            req = urllib.request.Request(GITHUB_API_URL, headers={"User-Agent": f"RomManagerPro/{APP_VERSION}"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            tag = data.get("tag_name", "").strip()
            if not tag: self.result_signal.emit({}); return
            self.result_signal.emit({"version": tag, "url": data.get("html_url", GITHUB_RELEASES), "notes": data.get("body", "")[:600]})
        except urllib.error.HTTPError as e:
            print(f"[UpdateChecker] HTTP {e.code}: {e.reason}"); self.result_signal.emit({})
        except Exception as e:
            print(f"[UpdateChecker] Erro: {e}"); self.result_signal.emit({})



# ===============================
# THREAD: INSTALL PAYLOAD-DUMPER-GO
# ===============================
class InstallPayloadDumperThread(QThread):
    log_signal      = Signal(str)
    progress_signal = Signal(int)
    done_signal     = Signal(bool, str)

    def run(self):
        system = platform.system().lower()
        pattern = PAYLOAD_DUMPER_ASSET_PATTERNS.get(system)
        if not pattern:
            self.log_signal.emit(f"✗  Sistema não suportado: {system}")
            self.done_signal.emit(False, ""); return

        try:
            self.log_signal.emit("🔍  Buscando última versão no GitHub (ssut/payload-dumper-go)...")
            req = urllib.request.Request(PAYLOAD_DUMPER_RELEASES_API, headers={"User-Agent": f"RomManagerPro/{APP_VERSION}"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                release = json.loads(resp.read().decode())
        except Exception as e:
            self.log_signal.emit(f"✗  Erro ao consultar GitHub: {e}")
            self.done_signal.emit(False, ""); return

        tag    = release.get("tag_name", "?")
        assets = release.get("assets", [])
        asset  = next((a for a in assets if pattern in a["name"] and a["name"].endswith(".tar.gz")), None)
        if not asset: asset = next((a for a in assets if pattern in a["name"]), None)
        if not asset:
            self.log_signal.emit(f"✗  Nenhum asset encontrado para '{pattern}'.")
            self.log_signal.emit(f"   Assets disponíveis: {[a['name'] for a in assets]}")
            self.done_signal.emit(False, ""); return

        url  = asset["browser_download_url"]
        name = asset["name"]
        self.log_signal.emit(f"✓  Versão: {tag}   Asset: {name}")
        self.log_signal.emit(f"⬇  Baixando...\n   {url}\n")
        self.progress_signal.emit(5)

        if system == "windows":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            base = os.path.join(os.path.expanduser("~"), ".local")
        install_dir = os.path.join(base, "payload-dumper-go")
        os.makedirs(install_dir, exist_ok=True)
        tmp_file = os.path.join(tempfile.gettempdir(), name)

        try:
            def _hook(c, b, t):
                if t > 0: self.progress_signal.emit(5 + min(int(c*b/t*70), 70))
            urllib.request.urlretrieve(url, tmp_file, reporthook=_hook)
            self.log_signal.emit("✓  Download concluído.")
            self.progress_signal.emit(76)

            self.log_signal.emit(f"📦  Extraindo para: {install_dir}")
            if name.endswith(".tar.gz") or name.endswith(".tgz"):
                with tarfile.open(tmp_file, "r:gz") as tar:
                    members = tar.getmembers()
                    for i, m in enumerate(members):
                        tar.extract(m, install_dir)
                        self.progress_signal.emit(76 + int(i/len(members)*18))
            elif name.endswith(".zip"):
                with zipfile.ZipFile(tmp_file, "r") as z:
                    members = z.namelist()
                    for i, m in enumerate(members):
                        z.extract(m, install_dir)
                        self.progress_signal.emit(76 + int(i/len(members)*18))

            self.progress_signal.emit(95)
            exe_name = "payload-dumper-go.exe" if system == "windows" else "payload-dumper-go"
            exe_path = None
            for root, _, files in os.walk(install_dir):
                for f in files:
                    if f == exe_name or f.startswith("payload-dumper-go"):
                        exe_path = os.path.join(root, f); break
                if exe_path: break

            if not exe_path:
                self.log_signal.emit("✗  Executável não encontrado após extração.")
                self.done_signal.emit(False, ""); return

            _apply_chmod(exe_path)
            exe_dir = os.path.dirname(exe_path)
            current = os.environ.get("PATH", "")
            if exe_dir not in current:
                os.environ["PATH"] = exe_dir + os.pathsep + current
                self.log_signal.emit(f"✓  PATH atualizado:\n   {exe_dir}")

            self.progress_signal.emit(100)
            self.log_signal.emit(f"\n✅  payload-dumper-go instalado com sucesso!\n   {exe_path}")
            self.done_signal.emit(True, exe_path)
        except Exception as e:
            self.log_signal.emit(f"\n✗  Erro: {e}"); self.done_signal.emit(False, "")
        finally:
            if os.path.isfile(tmp_file): os.remove(tmp_file)


# ===============================
# THREAD: INSTALL PLATFORM TOOLS
# ===============================
class InstallPlatformToolsThread(QThread):
    log_signal      = Signal(str)
    progress_signal = Signal(int)
    done_signal     = Signal(bool, str)

    def run(self):
        system = platform.system().lower()
        url = PLATFORM_TOOLS_URLS.get(system)
        if not url:
            self.log_signal.emit(f"✗  Sistema não suportado: {system}")
            self.done_signal.emit(False, ""); return

        if system == "windows":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        else:
            base = os.path.join(os.path.expanduser("~"), ".local")

        install_dir = os.path.join(base, "android-platform-tools")
        zip_path    = os.path.join(tempfile.gettempdir(), "platform-tools.zip")

        try:
            self.log_signal.emit(f"⬇  Baixando Platform Tools...\n   {url}\n")
            self.progress_signal.emit(5)

            def _hook(c, b, t):
                if t > 0: self.progress_signal.emit(5 + min(int(c*b/t*70), 70))
            urllib.request.urlretrieve(url, zip_path, reporthook=_hook)
            self.log_signal.emit("✓  Download concluído.")
            self.progress_signal.emit(76)

            self.log_signal.emit(f"📦  Extraindo para: {install_dir}")
            if os.path.isdir(install_dir): shutil.rmtree(install_dir)
            os.makedirs(install_dir, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as z:
                members = z.namelist()
                for i, m in enumerate(members):
                    z.extract(m, install_dir)
                    self.progress_signal.emit(76 + int(i/len(members)*18))

            sub = os.path.join(install_dir, "platform-tools")
            if os.path.isdir(sub):
                for item in os.listdir(sub): shutil.move(os.path.join(sub, item), install_dir)
                os.rmdir(sub)

            self.log_signal.emit("✓  Extração concluída.")
            self.progress_signal.emit(95)

            if system in ("linux", "darwin"):
                for binary in ("adb", "fastboot"):
                    _apply_chmod(os.path.join(install_dir, binary))

            current = os.environ.get("PATH", "")
            if install_dir not in current:
                os.environ["PATH"] = install_dir + os.pathsep + current
                self.log_signal.emit(f"✓  PATH atualizado:\n   {install_dir}")

            self.progress_signal.emit(100)
            self.log_signal.emit("\n✅  Platform Tools instalado com sucesso!\n   Reinicie o app para garantir que tudo funcione.")
            self.done_signal.emit(True, install_dir)
        except Exception as e:
            self.log_signal.emit(f"\n✗  Erro: {e}"); self.done_signal.emit(False, "")
        finally:
            if os.path.isfile(zip_path): os.remove(zip_path)


# ===============================
# THREAD: FASTBOOT
# ===============================
class FastbootThread(QThread):
    output_signal = Signal(str)
    def __init__(self, command):
        super().__init__()
        self.command = command if isinstance(command, list) else shlex.split(command)
    def run(self):
        try:
            process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in iter(process.stdout.readline, b''):
                if not line: break
                self.output_signal.emit(line.decode(errors="ignore").rstrip())
            process.wait()
        except FileNotFoundError: self.output_signal.emit(f"✗  '{self.command[0]}' não encontrado.")
        except Exception as e: self.output_signal.emit(f"✗  {e}")
        self.output_signal.emit("\n─── Finalizado ───")


# ===============================
# THREAD: ROM EXTRACTION
# ===============================
class RomExtractThread(QThread):
    log_signal      = Signal(str)
    progress_signal = Signal(int)
    done_signal     = Signal(dict, str)

    def __init__(self, dumper_exe, out_dir, partitions, payload_path):
        super().__init__()
        self.dumper_exe = dumper_exe; self.out_dir = out_dir
        self.partitions = partitions; self.payload_path = payload_path

    def run(self):
        cmd = [self.dumper_exe, "-p", ",".join(self.partitions), "-o", self.out_dir, self.payload_path]
        self.log_signal.emit(f"$ {' '.join(shlex.quote(c) for c in cmd)}\n")
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            total = len(self.partitions); current = 0
            for raw in iter(process.stdout.readline, b''):
                if not raw: break
                line = raw.decode(errors="ignore").rstrip(); self.log_signal.emit(line)
                if "extracting" in line.lower() or "writing" in line.lower():
                    current = min(current+1, total)
                    self.progress_signal.emit(int(current/total*90) if total else 50)
            process.wait()
            if process.returncode not in (0, None):
                self.done_signal.emit({}, f"Código {process.returncode}"); return
            found = {os.path.splitext(f)[0]: os.path.join(self.out_dir, f)
                     for f in os.listdir(self.out_dir) if f.endswith(".img")}
            self.progress_signal.emit(100); self.done_signal.emit(found, "")
        except FileNotFoundError: self.done_signal.emit({}, "payload-dumper-go não encontrado.")
        except Exception as e: self.done_signal.emit({}, str(e))


# ===============================
# THREAD: SEQUENTIAL FLASH
# ===============================
class SequentialFastbootThread(QThread):
    log_signal      = Signal(str)
    progress_signal = Signal(int)
    done_signal     = Signal(bool)

    def __init__(self, commands):
        super().__init__(); self.commands = commands

    def run(self):
        total = len(self.commands); success = True
        for idx, cmd in enumerate(self.commands):
            cmd_str = " ".join(shlex.quote(c) for c in cmd) if isinstance(cmd, list) else cmd
            self.log_signal.emit(f"\n$ {cmd_str}")
            try:
                args = cmd if isinstance(cmd, list) else shlex.split(cmd)
                process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in iter(process.stdout.readline, b''):
                    if not line: break
                    self.log_signal.emit(line.decode(errors="ignore").rstrip())
                process.wait()
                if process.returncode != 0:
                    self.log_signal.emit(f"✗  Erro (código {process.returncode})")
                    success = False; break
                self.log_signal.emit("✓  OK")
                self.progress_signal.emit(int((idx+1)/total*100))
            except FileNotFoundError: self.log_signal.emit("✗  não encontrado."); success = False; break
            except Exception as e: self.log_signal.emit(f"✗  {e}"); success = False; break
        self.done_signal.emit(success)