import os
import subprocess
import platform
import stat
import re
from config import tr

# ===============================
# UTIL
# ===============================
def run_adb_command(args):
    try:
        result = subprocess.run(["adb"]+args, capture_output=True, text=True, errors="ignore", timeout=15)
        return (result.stdout + result.stderr).strip()
    except FileNotFoundError: return "ERROR: adb não encontrado"
    except subprocess.TimeoutExpired: return "ERROR: timeout"
    except Exception as e: return f"ERROR: {e}"

def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode(errors="ignore")
    except subprocess.CalledProcessError as e: return e.output.decode(errors="ignore")
    except Exception as e: return f"ERROR: {e}"

def check_all_dependencies():
    results = {}
    for tool in ("adb", "fastboot"):
        try:
            subprocess.run([tool, "--version"], capture_output=True, timeout=5)
            results[tool] = True
        except: results[tool] = False
    for variant in ("payload-dumper-go", "payload_dumper_go", "payload-dumper"):
        try:
            subprocess.run([variant, "--help"], capture_output=True, timeout=5)
            results["payload-dumper-go"] = True; break
        except: pass
    if "payload-dumper-go" not in results: results["payload-dumper-go"] = False
    return results

def round_ram_gb(kb):
    gb = kb/1024/1024
    return f"{min([1,2,3,4,6,8,10,12,16,24,32,48,64], key=lambda x:abs(x-gb))} GB"

def battery_health_text(code, lang="pt"):
    return tr(lang, {"1":"health_unknown","2":"health_good","3":"health_overheat","4":"health_dead",
                     "5":"health_over_volt","6":"health_failure","7":"health_cold"}.get(code,"health_unknown"))

def normalize_version(v):
    return v.strip().lstrip("vV")

def compare_versions(v1, v2):
    def parse(v):
        parts = []
        for x in re.split(r"[.\-]", normalize_version(v)):
            try: parts.append(int(x))
            except ValueError: pass
        return parts
    try:
        p1, p2 = parse(v1), parse(v2)
        for a, b in zip(p1, p2):
            if a > b: return 1
            if a < b: return -1
        if len(p1) > len(p2): return 1
        if len(p1) < len(p2): return -1
        return 0
    except: return 0

def _apply_chmod(path):
    """Aplica chmod +x em qualquer sistema não-Windows."""
    if platform.system().lower() != "windows" and os.path.isfile(path):
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)