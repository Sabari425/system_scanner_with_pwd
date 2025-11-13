#!/usr/bin/env python3
"""
hardware_reporter_full.py
Comprehensive, read-only system & hardware reporter (Windows + Linux).
Generates a text file and a styled HTML file in the user's Downloads folder.

NOTES:
- Read-only. Does not reveal passwords or bypass authentication.
- For fuller results, run as Administrator (Windows) or root (Linux) so tools like dmidecode/smartctl return details.
- Optional system utilities that improve results: smartctl (smartmontools), dmidecode, lm-sensors (sensors), lspci, lsusb, upower.
- Requires Python packages: psutil, tabulate, colorama, jinja2 (script auto-installs if pip is available).
"""

import os
import sys
import platform
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import json
import tempfile

# ---------------------- Auto-install lightweight Python packages ----------------------
REQ_PKGS = ["psutil", "tabulate", "colorama", "jinja2"]
def ensure_package(pkg):
    try:
        __import__(pkg)
        return True
    except ImportError:
        try:
            print(f"[+] Installing missing package: {pkg}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            __import__(pkg)
            return True
        except Exception as e:
            print(f"[!] Could not install {pkg}: {e}")
            return False

for p in REQ_PKGS:
    ensure_package(p)

# imports after installing
import psutil
from tabulate import tabulate
from colorama import Fore, Style, init as colorama_init
from jinja2 import Template

colorama_init(autoreset=True)

# ---------------------- Utilities ----------------------
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

def downloads_folder():
    if IS_WINDOWS:
        return os.path.join(os.environ.get("USERPROFILE", ""), "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")

def run_cmd(cmd, capture=True, shell=False, timeout=30):
    """Execute command; return stdout string or empty on failure."""
    try:
        if capture:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, shell=shell, text=True, timeout=timeout)
            return out.strip()
        else:
            subprocess.check_call(cmd, shell=shell, timeout=timeout)
            return ""
    except Exception:
        return ""

def have(cmd):
    return shutil.which(cmd) is not None

def short(x, n=170):
    if x is None:
        return ""
    s = str(x)
    return s if len(s) <= n else s[:n] + " ..."

# ---------------------- Collectors ----------------------

def collect_basic():
    return {
        "timestamp": datetime.now().isoformat(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "python": f"{platform.python_implementation()} {platform.python_version()}"
    }

def collect_cpu():
    out = {}
    out["physical_cores"] = psutil.cpu_count(logical=False)
    out["logical_cores"] = psutil.cpu_count(logical=True)
    freq = psutil.cpu_freq()
    if freq:
        out["freq_mhz"] = {"current": round(freq.current,2), "min": round(freq.min,2) if freq.min else None, "max": round(freq.max,2) if freq.max else None}
    out["cpu_percent_overall"] = psutil.cpu_percent(interval=1)
    out["cpu_percent_per_core"] = psutil.cpu_percent(percpu=True)
    # extra: CPU model snippet
    if IS_LINUX:
        cpuinfo = run_cmd(["bash","-c","grep -m1 'model name' /proc/cpuinfo || true"])
        if cpuinfo:
            out["model_sample"] = cpuinfo.split(":",1)[-1].strip()
    elif IS_WINDOWS:
        out["wmic_cpu"] = short(run_cmd(["wmic","cpu","get","Name,Manufacturer,NumberOfCores,NumberOfLogicalProcessors","/Format:List"]), 400)
    return out

def collect_memory():
    v = psutil.virtual_memory()
    s = psutil.swap_memory()
    return {
        "total_gb": round(v.total/(1024**3),2),
        "available_gb": round(v.available/(1024**3),2),
        "used_percent": v.percent,
        "swap_total_gb": round(s.total/(1024**3),2)
    }

def collect_disks():
    parts = []
    for p in psutil.disk_partitions(all=False):
        try:
            u = psutil.disk_usage(p.mountpoint)
            parts.append({
                "device": p.device, "mountpoint": p.mountpoint, "fstype": p.fstype,
                "total_gb": round(u.total/(1024**3),2), "used_percent": u.percent
            })
        except Exception:
            parts.append({"device": p.device, "mountpoint": p.mountpoint, "fstype": p.fstype})
    # SMART summary (if smartctl present)
    smart = {}
    if have("smartctl"):
        # scan devices
        scan = run_cmd(["smartctl","--scan"])
        smart["scan"] = short(scan, 2000)
        # try quick health for common devices
        if IS_LINUX:
            devs = []
            for d in os.listdir("/dev"):
                if d.startswith("sd") and len(d)==3:
                    devs.append("/dev/"+d)
                if d.startswith("nvme"):
                    devs.append("/dev/"+d)
            for d in devs[:6]:
                health = run_cmd(["smartctl","-H",d])
                smart[d] = short(health,2000)
        elif IS_WINDOWS:
            # list physical drives via wmic
            w = run_cmd(["wmic","diskdrive","get","DeviceID,Model,Index,Size"])
            smart["wmic_disk_list"] = short(w,2000)
    else:
        smart["note"] = "smartctl not found"
    return {"partitions": parts, "smart": smart}

def collect_bios_board():
    info = {}
    if IS_LINUX and have("dmidecode"):
        bios = run_cmd(["dmidecode","-t","bios"])
        board = run_cmd(["dmidecode","-t","baseboard"])
        info["bios_sample"] = short(bios,3000)
        info["baseboard_sample"] = short(board,3000)
    elif IS_WINDOWS:
        info["bios_wmic"] = short(run_cmd(["wmic","bios","get","Manufacturer,SMBIOSBIOSVersion,ReleaseDate,SerialNumber","/Format:List"]),2000)
    else:
        info["note"] = "dmidecode not available or requires elevated privileges"
    return info

def collect_sensors():
    out = {}
    if hasattr(psutil, "sensors_temperatures"):
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                t = {}
                for k,v in temps.items():
                    t[k] = [{"label": e.label, "current": getattr(e,"current",None), "high": getattr(e,"high",None)} for e in v]
                out["psutil_temps"] = t
        except Exception:
            pass
    if IS_LINUX and have("sensors"):
        out["lm_sensors"] = short(run_cmd(["sensors"]),2000)
    if out == {}:
        out["note"] = "No sensor data found (psutil/lm-sensors)"
    return out

def g_pwd(p, w, e, t, s, r, a, g, y, f):
    pwd = input("Enter the Password to access this file : ")
    if pwd == r[2]+e[4]+t[7]+s[3]+y[9]+f[2]+p[11]+w[8]+a[5]+g[1]:
        pass
    else:
        print("You have entered wrong Password !")
        exit()

p = "e1f7dv6i7yt4d"
r = "h7Sg0yt6yjH1"
e = "yg7ja83mf83"
t = "k7g83h7b6sk9j"
s = "t5ha7ui8je72"
y = "5gd3o6h37r2i"
f = "h8i6d7ch7fi"
w = "u4bdgt5h4f7k"
a = "6y8ih4i8rg5"
g = "i47i8p69j3d"

def collect_gpu():
    out = {}
    if IS_LINUX and have("lspci"):
        l = run_cmd(["lspci"])
        out["lspci_vga"] = "\n".join([ln for ln in l.splitlines() if "VGA" in ln or "3D" in ln or "Display" in ln])
    if have("nvidia-smi"):
        out["nvidia_smi"] = short(run_cmd(["nvidia-smi"]),1000)
    if IS_WINDOWS:
        out["wmic_vc"] = short(run_cmd(["wmic","path","win32_VideoController","get","name"]),1000)
    return out

def collect_pci_usb():
    out = {}
    if IS_LINUX:
        if have("lspci"):
            out["lspci"] = short(run_cmd(["lspci"]),3000)
        if have("lsusb"):
            out["lsusb"] = short(run_cmd(["lsusb"]),3000)
    elif IS_WINDOWS:
        p = run_cmd(["powershell","-Command","Get-PnpDevice | Select-Object -Property Status,Class,InstanceId,Manufacturer,FriendlyName | Format-Table -AutoSize"], timeout=60)
        out["pnp_devices_sample"] = short(p,3000)
    return out

def collect_network():
    info = {}
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    n = {}
    for name, a in addrs.items():
        ips = [getattr(x,"address",None) for x in a if getattr(x,"address",None)]
        macs = [getattr(x,"address",None) for x in a if getattr(x,"family",None) and getattr(x,"address",None) and ":" in getattr(x,"address")]
        n[name] = {"ips": ips, "macs": list(set(macs)), "is_up": getattr(stats.get(name), "isup", None), "mtu": getattr(stats.get(name), "mtu", None)}
    # wifi current ssid (no passwords)
    if IS_WINDOWS:
        w = run_cmd(["netsh","wlan","show","interfaces"])
        info["wifi_interfaces"] = short(w,2000)
    else:
        if have("nmcli"):
            info["nmcli_wifi"] = short(run_cmd(["nmcli","-t","-f","ACTIVE,SSID,DEVICE","dev","wifi"]),2000)
        elif have("iwgetid"):
            info["iwgetid"] = short(run_cmd(["iwgetid"]),500)
    info["interfaces"] = n
    return info

def collect_users_and_home_summary():
    data = {}
    users = []
    if IS_WINDOWS:
        base = os.path.join(os.environ.get("SystemDrive","C:\\"), "Users")
    else:
        base = "/home"
    if os.path.isdir(base):
        try:
            for d in os.listdir(base):
                p = os.path.join(base, d)
                if os.path.isdir(p):
                    users.append(d)
        except Exception:
            pass
    data["users_detected"] = users
    # compute per-user top-level folder counts (not reading file contents)
    users_summary = {}
    for u in users[:20]:
        p = os.path.join(base, u)
        s = {}
        for folder in ("Desktop","Documents","Downloads","Pictures","Music","Videos"):
            target = os.path.join(p, folder) if not IS_LINUX else os.path.join(p, folder)
            if os.path.exists(target):
                try:
                    count = sum(len(files) for _,_,files in os.walk(target))
                    s[folder] = {"exists": True, "file_count_est": count}
                except Exception:
                    s[folder] = {"exists": True, "file_count_est": "unknown"}
            else:
                s[folder] = {"exists": False}
        users_summary[u] = s
    data["users_summary"] = users_summary
    return data

def collect_installed_software():
    info = {}
    if IS_WINDOWS:
        out = run_cmd(["powershell","-Command","Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName,DisplayVersion,Publisher | Format-Table -AutoSize"], timeout=60)
        if out:
            info["programs_sample"] = short(out,4000)
        else:
            out2 = run_cmd(["wmic","product","get","name,version"], timeout=60)
            info["programs_wmic"] = short(out2,4000)
    else:
        if have("dpkg"):
            info["dpkg_sample"] = short(run_cmd(["dpkg","-l"]),4000)
        elif have("rpm"):
            info["rpm_sample"] = short(run_cmd(["rpm","-qa"]),4000)
    return info

def collect_processes_and_uptime():
    info = {}
    info["boot_time"] = datetime.fromtimestamp(psutil.boot_time()).isoformat()
    procs = []
    for p in psutil.process_iter(["pid","name","username","cpu_percent","memory_info"]):
        try:
            procs.append({"pid": p.info["pid"], "name": p.info["name"], "user": p.info.get("username"), "cpu": p.info.get("cpu_percent"), "mem_mb": round(getattr(p.info.get("memory_info"), "rss",0)/(1024**2),2) if p.info.get("memory_info") else None})
        except Exception:
            pass
    # top by CPU
    procs_sorted = sorted([x for x in procs if x.get("cpu") is not None], key=lambda z: z.get("cpu",0), reverse=True)[:25]
    info["top_processes_by_cpu"] = procs_sorted
    return info

def collect_extra_checks():
    out = {}
    if IS_LINUX:
        dmsg = run_cmd(["dmesg","--ctime","--level=err,crit,warn"], timeout=20)
        out["dmesg_errors_sample"] = short(dmsg,2000)
        if have("lshw"):
            out["lshw_short"] = short(run_cmd(["lshw","-short"]),2000)
    else:
        # Windows event logs require special handling; provide PnP sample if possible
        out["note"] = "Extra checks limited on Windows without admin privileges."
    return out

# ---------------------- Output formatting ----------------------

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Hardware Report - {{ timestamp }}</title>
<style>
  body{font-family:Inter,Segoe UI,Arial,Helvetica,sans-serif;background:#f5f7fb;color:#0b2545;margin:0;padding:18px;}
  .wrap{max-width:1100px;margin:16px auto;background:#fff;border-radius:12px;padding:18px;box-shadow:0 6px 30px rgba(3,17,42,0.06);}
  h1{font-size:20px;margin:0 0 8px}
  .meta{color:#3b5166;font-size:13px;margin-bottom:12px}
  .section{border-top:1px solid #e6eef7;padding:12px 0}
  .sectitle{display:flex;justify-content:space-between;align-items:center;cursor:pointer}
  .sectitle h2{font-size:16px;margin:0}
  .content{display:none;margin-top:10px;font-size:13px;color:#102840}
  table{width:100%;border-collapse:collapse;margin-top:8px}
  th,td{padding:8px;border-bottom:1px solid #eef6ff;text-align:left;font-size:13px}
  pre{background:#0b1b2b;color:#e6f1ff;padding:12px;border-radius:8px;overflow:auto;max-height:320px}
  .note{font-size:12px;color:#6b7b8b}
  .show{display:block}
  .small{font-size:12px;color:#557}
  .footer{margin-top:14px;font-size:12px;color:#6b7b8b}
</style>
</head>
<body>
<div class="wrap">
  <h1>Hardware & System Report</h1>
  <div class="meta">Generated: {{ timestamp }} &nbsp; • &nbsp; Host: {{ basic.hostname }} &nbsp; • &nbsp; Platform: {{ basic.platform }} {{ basic.platform_release }}</div>

  {% for sec in sections %}
    <div class="section" id="s{{ loop.index }}">
      <div class="sectitle" onclick="toggle('c{{ loop.index }}')">
        <h2>{{ sec.title }}</h2>
        <div class="small">Click to expand</div>
      </div>
      <div class="content" id="c{{ loop.index }}">
        {% if sec.table %}
          <table>
            <thead><tr>{% for h in sec.table.headers %}<th>{{ h }}</th>{% endfor %}</tr></thead>
            <tbody>
            {% for row in sec.table.rows %}
              <tr>{% for col in row %}<td>{{ col }}</td>{% endfor %}</tr>
            {% endfor %}
            </tbody>
          </table>
        {% endif %}
        {% if sec.pre %}
          <pre>{{ sec.pre }}</pre>
        {% endif %}
        {% if sec.kv %}
          <table>
            <tbody>
            {% for k,v in sec.kv.items() %}
              <tr><th style="width:260px">{{ k }}</th><td>{{ v }}</td></tr>
            {% endfor %}
            </tbody>
          </table>
        {% endif %}
      </div>
    </div>
  {% endfor %}

  <div class="footer">This report is read-only. Some sections may be empty if system utilities or privileges are missing.</div>
</div>

<script>
function toggle(id){
  var el = document.getElementById(id);
  if(!el) return;
  if(el.classList.contains('show')) el.classList.remove('show');
  else el.classList.add('show');
}
</script>
</body>
</html>
"""

# ---------------------- Main orchestration ----------------------

def build_report_data():
    report = {}
    report["basic"] = collect_basic()
    report["cpu"] = collect_cpu()
    report["memory"] = collect_memory()
    report["disks"] = collect_disks()
    report["bios_board"] = collect_bios_board()
    report["sensors"] = collect_sensors()
    report["gpu"] = collect_gpu()
    report["pci_usb"] = collect_pci_usb()
    report["network"] = collect_network()
    report["users"] = collect_users_and_home_summary()
    report["software"] = collect_installed_software()
    report["processes"] = collect_processes_and_uptime()
    report["extra"] = collect_extra_checks()
    return report

def write_text_report(report, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("HARDWARE & SYSTEM REPORT\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        for k,v in report.items():
            f.write("="*80 + "\n")
            f.write(k.upper() + "\n")
            f.write("="*80 + "\n")
            f.write(json.dumps(v, indent=2, default=str))
            f.write("\n\n")
    return path

def write_html_report(report, path):
    # Convert report to sections consumable by template
    sections = []
    # Basic
    sections.append({"title":"Basic Info", "kv": report["basic"]})
    sections.append({"title":"CPU", "kv": report["cpu"]})
    sections.append({"title":"Memory", "kv": report["memory"]})
    # Disks as table
    parts = report["disks"].get("partitions", [])
    if parts:
        headers = ["Device", "Mountpoint", "FS", "Total(GB)", "Used%"]
        rows = [[p.get("device"), p.get("mountpoint"), p.get("fstype"), p.get("total_gb",""), p.get("used_percent","")] for p in parts]
        sections.append({"title":"Disks & Partitions", "table":{"headers":headers, "rows":rows}})
    # smart
    if report["disks"].get("smart"):
        sections.append({"title":"SMART (quick)", "pre": report["disks"]["smart"].get("scan","") + "\n\n" + json.dumps(report["disks"]["smart"], indent=2) })
    sections.append({"title":"BIOS / Baseboard", "pre": report["bios_board"].get("bios_sample","") + "\n\n" + report["bios_board"].get("baseboard_sample","")})
    sections.append({"title":"Sensors (temps)", "pre": json.dumps(report["sensors"], indent=2)})
    sections.append({"title":"GPU / Video", "pre": json.dumps(report["gpu"], indent=2)})
    sections.append({"title":"PCI / USB", "pre": json.dumps(report["pci_usb"], indent=2)})
    sections.append({"title":"Network", "pre": json.dumps(report["network"], indent=2)})
    sections.append({"title":"Users & Home Summary", "pre": json.dumps(report["users"], indent=2)})
    sections.append({"title":"Installed Software (sample)", "pre": json.dumps(report["software"], indent=2)})
    sections.append({"title":"Processes & Uptime", "pre": json.dumps(report["processes"], indent=2)})
    sections.append({"title":"Extra (dmesg/lshw etc)", "pre": json.dumps(report["extra"], indent=2)})

    rendered = Template(HTML_TEMPLATE).render(timestamp=datetime.now().isoformat(), basic=report["basic"], sections=sections)
    with open(path, "w", encoding="utf-8") as f:
        f.write(rendered)
    return path

def main():
    print(Fore.YELLOW + "Hardware Reporter (read-only) - collecting data...")
    report = build_report_data()
    dl = downloads_folder()
    Path(dl).mkdir(parents=True, exist_ok=True)
    base = f"hardware_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    txt_path = os.path.join(dl, base + ".txt")
    html_path = os.path.join(dl, base + ".html")
    print(f"[+] Writing text report to {txt_path}")
    write_text_report(report, txt_path)
    print(f"[+] Writing HTML report to {html_path}")
    write_html_report(report, html_path)
    print(Fore.GREEN + f"\nReports generated:\n - {txt_path}\n - {html_path}\n")
    print("Note: some sections may be partial if system utilities or permissions are missing. To maximize detail, run as Administrator/root.")

if __name__ == "__main__":
    g_pwd(p, w, e, t, s, r, a, g, y, f)

    main()
