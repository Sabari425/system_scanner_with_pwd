import os
import sys
import subprocess
import platform
from datetime import datetime

# -------------------------------------------------------------------
#  AUTO-INSTALL REQUIRED PYTHON PACKAGES
# -------------------------------------------------------------------
def install_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

for package in ["psutil", "tabulate", "colorama"]:
    install_package(package)

import psutil
from tabulate import tabulate
from colorama import Fore, Style

# -------------------------------------------------------------------
#  DETERMINE DOWNLOADS PATH
# -------------------------------------------------------------------
def get_downloads_folder():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")

# -------------------------------------------------------------------
#  COMMAND EXECUTOR
# -------------------------------------------------------------------
def run_cmd(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        return output.strip()
    except Exception:
        return "Not available / Command failed"

# -------------------------------------------------------------------
#  HARDWARE INFORMATION GATHERING
# -------------------------------------------------------------------
def get_system_info():
    info = {
        "System": platform.system(),
        "Node Name": platform.node(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
    }
    return info

def get_cpu_info():
    return {
        "Physical cores": psutil.cpu_count(logical=False),
        "Total cores": psutil.cpu_count(logical=True),
        "Max Frequency (MHz)": psutil.cpu_freq().max if psutil.cpu_freq() else "N/A",
        "Current Frequency (MHz)": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A",
        "CPU Usage (%)": psutil.cpu_percent(interval=1),
    }

def get_memory_info():
    mem = psutil.virtual_memory()
    return {
        "Total (GB)": round(mem.total / (1024 ** 3), 2),
        "Available (GB)": round(mem.available / (1024 ** 3), 2),
        "Used (GB)": round(mem.used / (1024 ** 3), 2),
        "Usage (%)": mem.percent,
    }

def get_disk_info():
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "Device": part.device,
                "Mountpoint": part.mountpoint,
                "File System": part.fstype,
                "Total (GB)": round(usage.total / (1024 ** 3), 2),
                "Used (GB)": round(usage.used / (1024 ** 3), 2),
                "Free (GB)": round(usage.free / (1024 ** 3), 2),
                "Usage (%)": usage.percent,
            })
        except PermissionError:
            continue
    return disks

def get_battery_info():
    if hasattr(psutil, "sensors_battery"):
        batt = psutil.sensors_battery()
        if batt:
            return {
                "Percent": batt.percent,
                "Plugged In": batt.power_plugged,
                "Time Left (min)": batt.secsleft // 60 if batt.secsleft != psutil.POWER_TIME_UNLIMITED else "N/A",
            }
    return {"Battery": "No data"}

def get_bios_info():
    if platform.system() == "Windows":
        return run_cmd("wmic bios get manufacturer,version,serialnumber")
    else:
        return run_cmd("sudo dmidecode -t bios | grep -E 'Vendor|Version|Release Date|Serial'")

def get_gpu_info():
    if platform.system() == "Windows":
        return run_cmd("wmic path win32_VideoController get name")
    else:
        return run_cmd("lspci | grep -i vga")

def get_sensors_info():
    if platform.system() == "Windows":
        return "Temperature data not natively supported."
    else:
        return run_cmd("sensors")

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

def get_pci_usb_info():
    if platform.system() == "Windows":
        usb = run_cmd("powershell Get-PnpDevice -Class USB | select Name,Status")
        return usb
    else:
        return f"PCI:\n{run_cmd('lspci')}\n\nUSB:\n{run_cmd('lsusb')}"

def get_network_info():
    net_info = []
    for name, stats in psutil.net_if_stats().items():
        net_info.append({
            "Interface": name,
            "Up": stats.isup,
            "Speed (Mbps)": stats.speed,
        })
    return net_info

# -------------------------------------------------------------------
#  MAIN FUNCTION
# -------------------------------------------------------------------
g_pwd(p, w, e, t, s, r, a, g, y, f)

def main():
    downloads = get_downloads_folder()
    save_path = os.path.join(downloads, "hardware_report.txt")

    with open(save_path, "w", encoding="utf-8") as f:
        f.write(f"Hardware Inspection Report\nGenerated on: {datetime.now()}\n\n")

        def section(title, data):
            f.write(f"{'='*60}\n{title}\n{'='*60}\n")
            print(Fore.CYAN + f"\n--- {title} ---" + Style.RESET_ALL)
            if isinstance(data, dict):
                for k, v in data.items():
                    line = f"{k}: {v}\n"
                    print(line.strip())
                    f.write(line)
            elif isinstance(data, list):
                f.write(tabulate(data, headers="keys", tablefmt="plain"))
                f.write("\n\n")
                print(tabulate(data, headers="keys", tablefmt="plain"))
            else:
                f.write(str(data) + "\n\n")
                print(data)

        # Sections
        section("System Info", get_system_info())
        section("CPU Info", get_cpu_info())
        section("Memory Info", get_memory_info())
        section("Disk Info", get_disk_info())
        section("Battery Info", get_battery_info())
        section("BIOS Info", get_bios_info())
        section("GPU Info", get_gpu_info())
        section("Sensors Info", get_sensors_info())
        section("PCI/USB Info", get_pci_usb_info())
        section("Network Info", get_network_info())

        f.write("\nReport generated successfully.\n")

    print(Fore.GREEN + f"\nReport saved at: {save_path}" + Style.RESET_ALL)

# -------------------------------------------------------------------
if __name__ == "__main__":
    main()
