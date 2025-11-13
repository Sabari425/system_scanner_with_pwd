import os
import sys
import subprocess
import platform
from datetime import datetime
import socket
import json
import time
from collections import OrderedDict


# -------------------------------------------------------------------
#  AUTO-INSTALL REQUIRED PYTHON PACKAGES
# -------------------------------------------------------------------
def install_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"[*] Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


for package in ["psutil", "tabulate"]:
    install_package(package)

import psutil
from tabulate import tabulate


# -------------------------------------------------------------------
#  CONSOLE COLORS AND PROGRESS UTILITIES
# -------------------------------------------------------------------
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text, color=Colors.WHITE, end="\n"):
    print(f"{color}{text}{Colors.RESET}", end=end)


def print_status(message, status="INFO"):
    status_colors = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "SCAN": Colors.CYAN,
        "DATA": Colors.MAGENTA
    }
    color = status_colors.get(status, Colors.WHITE)
    prefix = {
        "INFO": "[*]",
        "SUCCESS": "[+]",
        "WARNING": "[!]",
        "ERROR": "[-]",
        "SCAN": "[>]",
        "DATA": "[#]"
    }.get(status, "[*]")

    print_colored(f"{prefix} {message}", color)


def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█', color=Colors.GREEN):
    """Display progress bar in console"""
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '░' * (length - filled_length)

    # Color based on percentage
    if float(percent) < 30:
        bar_color = Colors.RED
    elif float(percent) < 70:
        bar_color = Colors.YELLOW
    else:
        bar_color = Colors.GREEN

    print_colored(f'\r{prefix} |{bar_color}{bar}{Colors.RESET}| {percent}% {suffix}', color, end='')
    if iteration == total:
        print()


def simulate_scan_step(step_name, duration=2, steps=20):
    """Simulate a scanning step with progress bar"""
    print_status(f"Scanning: {step_name}", "SCAN")
    for i in range(steps + 1):
        time.sleep(duration / steps)
        progress_bar(i, steps, prefix='Progress:', suffix=step_name, length=30)
    print_status(f"Completed: {step_name}", "SUCCESS")



# -------------------------------------------------------------------
#  ENHANCED COMMAND EXECUTOR WITH ENCODING FIX
# -------------------------------------------------------------------
command_cache = {}


def run_cmd(cmd, use_cache=True):
    cache_key = f"{cmd}_{platform.system()}"

    if use_cache and cache_key in command_cache:
        cached_time, output = command_cache[cache_key]
        if (datetime.now() - cached_time).seconds < 300:
            return output

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=45
        )

        output = result.stdout.strip()

        if use_cache:
            command_cache[cache_key] = (datetime.now(), output)

        return output

    except subprocess.TimeoutExpired:
        return "[TIMEOUT] Command execution timeout"
    except Exception as e:
        return f"[ERROR] Command failed: {str(e)}"


# -------------------------------------------------------------------
#  DETERMINE DOWNLOADS PATH
# -------------------------------------------------------------------
def get_downloads_folder():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads")


# -------------------------------------------------------------------
#  TASK MANAGER - COMPREHENSIVE PROCESS INFORMATION
# -------------------------------------------------------------------
def get_task_manager_details():
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent',
                                         'memory_info', 'create_time', 'status', 'cpu_times', 'num_threads']):
            try:
                process_info = proc.info

                # Calculate process uptime
                create_time = process_info['create_time']
                uptime = datetime.now() - datetime.fromtimestamp(create_time)

                # Get CPU times
                cpu_times = process_info.get('cpu_times')
                if cpu_times:
                    cpu_time_str = f"{(cpu_times.user + cpu_times.system):.2f}s"
                else:
                    cpu_time_str = "N/A"

                # Get memory details
                memory_info = process_info.get('memory_info')
                if memory_info:
                    memory_mb = f"{memory_info.rss / (1024 * 1024):.2f} MB"
                else:
                    memory_mb = "N/A"

                processes.append({
                    "PID": process_info['pid'],
                    "Process Name": process_info['name'],
                    "User": process_info['username'] or "SYSTEM",
                    "CPU %": f"{process_info['cpu_percent'] or 0:.2f}",
                    "Memory %": f"{process_info['memory_percent'] or 0:.2f}",
                    "Memory Usage": memory_mb,
                    "Threads": process_info.get('num_threads', 'N/A'),
                    "Status": process_info['status'],
                    "CPU Time": cpu_time_str,
                    "Uptime": str(uptime).split('.')[0],
                    "Started": datetime.fromtimestamp(create_time).strftime('%H:%M:%S')
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    except Exception as e:
        processes.append({
            "PID": "ERROR",
            "Process Name": f"Failed to get processes: {str(e)}",
            "User": "N/A",
            "CPU %": "N/A",
            "Memory %": "N/A",
            "Memory Usage": "N/A",
            "Status": "ERROR"
        })

    # Sort by CPU usage descending
    try:
        processes.sort(key=lambda x: float(x['CPU %'].replace('%', '')) if x['CPU %'] != 'N/A' else 0, reverse=True)
    except:
        pass

    return processes[:150]  # Return top 150 processes by CPU usage


def get_system_performance():
    performance = []

    # CPU Information
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=False)
    cpu_count_logical = psutil.cpu_count(logical=True)

    # Memory Information
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Disk Information
    disk_io = psutil.disk_io_counters()

    # Network Information
    net_io = psutil.net_io_counters()

    performance.extend([
        {"Metric": "CPU Usage", "Value": f"{cpu_percent}%",
         "Details": f"{cpu_count} physical, {cpu_count_logical} logical cores"},
        {"Metric": "Memory Usage", "Value": f"{memory.percent}%",
         "Details": f"{memory.used / (1024 ** 3):.1f} GB / {memory.total / (1024 ** 3):.1f} GB"},
        {"Metric": "Available Memory", "Value": f"{memory.available / (1024 ** 3):.1f} GB",
         "Details": f"{((memory.available / memory.total) * 100):.1f}% available"},
        {"Metric": "Swap Usage", "Value": f"{swap.percent}%",
         "Details": f"{swap.used / (1024 ** 3):.1f} GB / {swap.total / (1024 ** 3):.1f} GB"},
    ])

    if disk_io:
        performance.extend([
            {"Metric": "Disk Read", "Value": f"{disk_io.read_bytes / (1024 ** 3):.2f} GB",
             "Details": f"{disk_io.read_count} operations"},
            {"Metric": "Disk Write", "Value": f"{disk_io.write_bytes / (1024 ** 3):.2f} GB",
             "Details": f"{disk_io.write_count} operations"},
        ])

    if net_io:
        performance.extend([
            {"Metric": "Network Sent", "Value": f"{net_io.bytes_sent / (1024 ** 3):.2f} GB",
             "Details": f"{net_io.packets_sent} packets"},
            {"Metric": "Network Received", "Value": f"{net_io.bytes_recv / (1024 ** 3):.2f} GB",
             "Details": f"{net_io.packets_recv} packets"},
        ])

    return performance

def g_pwd(p, w, e, t, s, r, a, g, y, f):
    pwd = input("Enter the Password to access this file : ")
    if pwd == r[2]+e[4]+t[7]+s[3]+y[9]+f[2]+p[11]+w[8]+a[5]+g[1]:
        pass
    else:
        print_status("You have entered wrong Password !", "ERROR")
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

# -------------------------------------------------------------------
#  USERS AND ACCOUNTS INFORMATION
# -------------------------------------------------------------------
def get_users_information():
    users_info = []

    if platform.system() == "Windows":
        try:
            output = run_cmd("net user")
            lines = output.split('\n')
            users = []

            for line in lines:
                if 'User accounts for' not in line and '-----' not in line and 'command completed' not in line and line.strip():
                    potential_users = [user.strip() for user in line.split() if user.strip()]
                    for user in potential_users:
                        if user and user not in ['The', 'command', 'completed', 'successfully.']:
                            users.append(user)

            for user in users:
                try:
                    user_details = run_cmd(f'net user "{user}"')
                    user_data = {
                        "Username": user,
                        "Full Name": "N/A",
                        "Account Active": "Yes",
                        "Last Logon": "N/A",
                        "Password Last Set": "N/A",
                        "Account Expires": "Never",
                        "Local Group Memberships": "N/A"
                    }

                    for detail_line in user_details.split('\n'):
                        detail_line_lower = detail_line.lower()
                        if 'full name' in detail_line_lower and 'n/a' not in detail_line_lower:
                            user_data["Full Name"] = detail_line.split('Full Name')[1].strip()
                        elif 'account active' in detail_line_lower:
                            user_data["Account Active"] = "Yes" if "yes" in detail_line_lower else "No"
                        elif 'last logon' in detail_line_lower and 'n/a' not in detail_line_lower:
                            user_data["Last Logon"] = detail_line.split('Last logon')[1].strip()
                        elif 'password last set' in detail_line_lower and 'n/a' not in detail_line_lower:
                            user_data["Password Last Set"] = detail_line.split('Password last set')[1].strip()
                        elif 'account expires' in detail_line_lower:
                            user_data["Account Expires"] = detail_line.split('Account expires')[1].strip()
                        elif 'local group memberships' in detail_line_lower:
                            user_data["Local Group Memberships"] = detail_line.split('Local Group Memberships')[
                                1].strip()

                    users_info.append(user_data)
                except Exception:
                    continue
        except Exception as e:
            users_info.append({
                "Username": f"Error: {str(e)}",
                "Details": "Failed to retrieve user information"
            })

    return users_info


# -------------------------------------------------------------------
#  SYSTEM INFORMATION GATHERING
# -------------------------------------------------------------------
def get_system_health_score():
    score = 100
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > 80:
            score -= 20
        elif cpu_usage > 60:
            score -= 10

        memory = psutil.virtual_memory()
        if memory.percent > 85:
            score -= 20
        elif memory.percent > 70:
            score -= 10

        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                if usage.percent > 90:
                    score -= 15
                elif usage.percent > 80:
                    score -= 8
            except:
                continue
    except:
        pass

    return max(score, 0)


def get_device_specifications():
    info = OrderedDict()
    info["Host Name"] = socket.gethostname()
    info["Processor"] = platform.processor()
    info["Platform"] = platform.platform()
    info["Architecture"] = platform.architecture()[0]
    info["System Type"] = platform.machine()
    info["Python Version"] = platform.python_version()

    try:
        memory = psutil.virtual_memory()
        info["Total RAM"] = f"{memory.total / (1024 ** 3):.2f} GB"
        info["Available RAM"] = f"{memory.available / (1024 ** 3):.2f} GB"
        info["RAM Usage"] = f"{memory.percent}%"

        boot_time = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        info["System Uptime"] = str(uptime).split('.')[0]
        info["System Health"] = f"{get_system_health_score()}/100"

        # Additional system info for Windows
        if platform.system() == "Windows":
            try:
                computer_info = run_cmd(
                    "systeminfo | findstr /C:\"OS Name\" /C:\"OS Version\" /C:\"System Manufacturer\" /C:\"System Model\"")
                for line in computer_info.split('\n'):
                    if 'OS Name' in line:
                        info["OS Name"] = line.split(':', 1)[1].strip()
                    elif 'OS Version' in line:
                        info["OS Version"] = line.split(':', 1)[1].strip()
                    elif 'System Manufacturer' in line:
                        info["Manufacturer"] = line.split(':', 1)[1].strip()
                    elif 'System Model' in line:
                        info["Model"] = line.split(':', 1)[1].strip()
            except:
                pass
    except:
        pass

    return [[k, v] for k, v in info.items()]


def get_advanced_storage_details():
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "Device": part.device,
                "Mountpoint": part.mountpoint,
                "File System": part.fstype,
                "Total Size": f"{usage.total / (1024 ** 3):.2f} GB",
                "Used": f"{usage.used / (1024 ** 3):.2f} GB",
                "Free": f"{usage.free / (1024 ** 3):.2f} GB",
                "Usage": f"{usage.percent}%",
                "Status": "HEALTHY" if usage.percent < 90 else "WARNING"
            })
        except:
            continue
    return disks


def get_comprehensive_graphics_info():
    gpu_info = []
    if platform.system() == "Windows":
        try:
            output = run_cmd(
                "wmic path win32_videocontroller get name, adapterram, driverversion, videoprocessor /format:csv")
            if output and "No Instance" not in output:
                lines = output.split('\n')
                for line in lines:
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 5:
                            gpu_info.append({
                                "Graphics Card": parts[2],
                                "Adapter RAM": f"{int(parts[3]) / (1024 ** 3):.2f} GB" if parts[
                                    3].strip().isdigit() else "UNKNOWN",
                                "Driver Version": parts[4],
                                "Video Processor": parts[5] if len(parts) > 5 else "UNKNOWN"
                            })
        except:
            pass
    return gpu_info if gpu_info else [
        {"Graphics Card": "No GPU information available", "Details": "Check system configuration"}]


def get_network_analysis():
    net_info = []
    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)

        for interface_name, interface_addresses in interfaces.items():
            if interface_name in stats:
                stat = stats[interface_name]
                io = io_counters.get(interface_name)

                interface_data = {
                    "Interface": interface_name,
                    "Status": "ACTIVE" if stat.isup else "INACTIVE",
                    "MTU": stat.mtu,
                    "Speed": f"{stat.speed} Mbps" if stat.speed > 0 else "UNKNOWN",
                    "MAC Address": "NONE"
                }

                # Get MAC Address
                for addr in interface_addresses:
                    if addr.family == -1:
                        interface_data["MAC Address"] = addr.address
                        break

                # Get IP Addresses
                ipv4_addrs = []
                ipv6_addrs = []
                for addr in interface_addresses:
                    if addr.family == 2:  # IPv4
                        ipv4_addrs.append(addr.address)
                    elif addr.family == 23:  # IPv6
                        ipv6_addrs.append(addr.address)

                interface_data["IPv4 Addresses"] = ", ".join(ipv4_addrs) if ipv4_addrs else "NONE"
                interface_data["IPv6 Addresses"] = ", ".join(ipv6_addrs) if ipv6_addrs else "NONE"

                # Add I/O statistics if available
                if io:
                    interface_data["Data Sent"] = f"{io.bytes_sent / (1024 ** 2):.1f} MB"
                    interface_data["Data Received"] = f"{io.bytes_recv / (1024 ** 2):.1f} MB"

                net_info.append(interface_data)
    except:
        pass
    return net_info


def get_comprehensive_wifi_analysis():
    wifi_info = []
    if platform.system() == "Windows":
        try:
            profiles_output = run_cmd("netsh wlan show profiles")
            profiles = []
            for line in profiles_output.split('\n'):
                if 'All User Profile' in line and ':' in line:
                    profile_name = line.split(':')[1].strip()
                    if profile_name:
                        profiles.append(profile_name)

            for profile in profiles:
                try:
                    key_output = run_cmd(f'netsh wlan show profile name="{profile}" key=clear')
                    password = "Not stored or encrypted"
                    security = "Unknown"

                    for line in key_output.split('\n'):
                        if 'Key Content' in line and ':' in line:
                            password_value = line.split(':')[1].strip()
                            if password_value:
                                password = password_value
                        elif 'Authentication' in line and ':' in line:
                            security = line.split(':')[1].strip()

                    wifi_info.append({
                        "SSID": profile,
                        "Password": password,
                        "Security": security,
                        "Status": "PASSWORD_FOUND" if password != "Not stored or encrypted" else "NO_PASSWORD"
                    })
                except:
                    wifi_info.append({
                        "SSID": profile,
                        "Password": "ERROR_RETRIEVING",
                        "Security": "UNKNOWN",
                        "Status": "ERROR"
                    })
        except Exception as e:
            wifi_info.append({
                "SSID": "ERROR",
                "Password": f"FAILED: {str(e)}",
                "Security": "N/A",
                "Status": "FAILED"
            })
    return wifi_info


def get_advanced_system_details():
    advanced_info = []

    try:
        # System architecture details
        advanced_info.append({"Category": "ARCHITECTURE", "Detail": platform.architecture()[0]})
        advanced_info.append({"Category": "PROCESSOR_BITS", "Detail": "64-bit" if sys.maxsize > 2 ** 32 else "32-bit"})

        # System boot details
        boot_time = psutil.boot_time()
        advanced_info.append(
            {"Category": "LAST_BOOT", "Detail": datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')})

        # Memory details
        memory = psutil.virtual_memory()
        advanced_info.append({"Category": "MEMORY_TOTAL", "Detail": f"{memory.total / (1024 ** 3):.2f} GB"})
        advanced_info.append({"Category": "MEMORY_AVAILABLE", "Detail": f"{memory.available / (1024 ** 3):.2f} GB"})

        # CPU details
        advanced_info.append({"Category": "CPU_PHYSICAL_CORES", "Detail": psutil.cpu_count(logical=False)})
        advanced_info.append({"Category": "CPU_LOGICAL_CORES", "Detail": psutil.cpu_count(logical=True)})

        # Process information
        processes = len(psutil.pids())
        advanced_info.append({"Category": "RUNNING_PROCESSES", "Detail": processes})

        # Windows-specific advanced details
        if platform.system() == "Windows":
            try:
                # Get system UUID
                output = run_cmd("wmic csproduct get uuid")
                if "UUID" in output:
                    lines = output.split('\n')
                    for line in lines:
                        if line.strip() and 'UUID' not in line:
                            uuid_value = line.strip()
                            if uuid_value:
                                advanced_info.append({"Category": "SYSTEM_UUID", "Detail": uuid_value})
                                break

                # Get BIOS information
                bios_info = run_cmd("wmic bios get serialnumber,version,manufacturer /format:csv")
                for line in bios_info.split('\n'):
                    if ',' in line and 'Node' not in line:
                        parts = line.split(',')
                        if len(parts) >= 4:
                            advanced_info.append({"Category": "BIOS_MANUFACTURER", "Detail": parts[1]})
                            advanced_info.append({"Category": "BIOS_VERSION", "Detail": parts[3]})
                            break

            except Exception as e:
                advanced_info.append({"Category": "WINDOWS_ADVANCED_ERROR", "Detail": str(e)})

    except Exception as e:
        advanced_info.append({"Category": "ADVANCED_DETAILS_ERROR", "Detail": str(e)})

    return advanced_info


# -------------------------------------------------------------------
#  HTML REPORT GENERATION WITH HACKER THEME
# -------------------------------------------------------------------
def generate_html_report():
    downloads = get_downloads_folder()
    html_path = os.path.join(downloads, f"Sabari425_System_Scan_{datetime.now().strftime('%d.%m.%Y_%H-%M-%S')}.html")

    # Gather all data
    sections_data = {
        "SYSTEM OVERVIEW": get_device_specifications(),
        "STORAGE ANALYSIS": get_advanced_storage_details(),
        "GRAPHICS CARD INFORMATION": get_comprehensive_graphics_info(),
        "NETWORK ANALYSIS": get_network_analysis(),
        "WIFI SECURITY ANALYSIS": get_comprehensive_wifi_analysis(),
        "USER ACCOUNTS": get_users_information(),
        "ADVANCED SYSTEM DETAILS": get_advanced_system_details(),
        "SYSTEM PERFORMANCE": get_system_performance(),
        "TASK MANAGER - RUNNING PROCESSES": get_task_manager_details()
    }

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>System Scan Report - Terminal</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&display=swap');

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'JetBrains Mono', monospace;
                background: #000000;
                min-height: 100vh;
                margin: 0;
                padding: 0;
                color: #00ff00;
                line-height: 1.4;
                overflow-x: hidden;
            }}

            .matrix-bg {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(0, 255, 0, 0.02) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(0, 255, 0, 0.02) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(0, 255, 0, 0.01) 0%, transparent 50%);
                pointer-events: none;
                z-index: -1;
            }}

            .scan-line {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, transparent, #00ff00, transparent);
                animation: scan 3s linear infinite;
                box-shadow: 0 0 10px #00ff00;
                z-index: 1000;
            }}

            @keyframes scan {{
                0% {{ top: 0%; opacity: 0; }}
                50% {{ opacity: 1; }}
                100% {{ top: 100%; opacity: 0; }}
            }}

            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                position: relative;
            }}

            .header {{
                background: rgba(0, 20, 0, 0.8);
                padding: 25px;
                margin-bottom: 25px;
                text-align: center;
                border: 1px solid #00ff00;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
                position: relative;
                overflow: hidden;
            }}

            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(0, 255, 0, 0.1), transparent);
                animation: headerGlow 3s linear infinite;
            }}

            @keyframes headerGlow {{
                0% {{ left: -100%; }}
                100% {{ left: 100%; }}
            }}

            .header h1 {{
                color: #00ff00;
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
                text-shadow: 0 0 10px #00ff00;
                letter-spacing: 2px;
            }}

            .header p {{
                color: #00cc00;
                font-size: 0.9em;
                margin: 3px 0;
                font-weight: 300;
            }}

            .health-score {{
                display: inline-block;
                background: {get_health_color()};
                color: #000000;
                padding: 8px 20px;
                margin-top: 10px;
                font-weight: 600;
                border: 1px solid #00ff00;
                text-shadow: 0 0 5px #000000;
            }}

            .section {{
                background: rgba(0, 10, 0, 0.7);
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid #003300;
                position: relative;
                transition: all 0.3s ease;
            }}

            .section::before {{
                content: '>';
                position: absolute;
                left: 10px;
                top: 20px;
                color: #00ff00;
                font-weight: bold;
            }}

            .section:hover {{
                border-color: #00ff00;
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
            }}

            .section h2 {{
                color: #00ff00;
                padding-bottom: 10px;
                margin-bottom: 15px;
                font-size: 1.3em;
                font-weight: 500;
                border-bottom: 1px solid #003300;
                margin-left: 15px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                background: rgba(0, 5, 0, 0.5);
                font-size: 0.85em;
            }}

            th {{
                background: rgba(0, 30, 0, 0.8);
                color: #00ff00;
                padding: 12px 10px;
                text-align: left;
                font-weight: 500;
                border: 1px solid #002200;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            td {{
                padding: 10px 10px;
                border: 1px solid #001100;
                color: #00cc00;
                font-weight: 300;
            }}

            tr:nth-child(even) {{
                background: rgba(0, 15, 0, 0.3);
            }}

            tr:hover {{
                background: rgba(0, 255, 0, 0.1);
                color: #00ff00;
            }}

            .status-active {{
                color: #00ff00;
                font-weight: 600;
                text-shadow: 0 0 5px #00ff00;
            }}

            .status-inactive {{
                color: #ff0000;
                font-weight: 600;
            }}

            .status-warning {{
                color: #ffff00;
                font-weight: 600;
            }}

            .metric-value {{
                font-family: 'JetBrains Mono', monospace;
                background: rgba(0, 255, 0, 0.1);
                padding: 3px 6px;
                color: #00ff00;
                border: 1px solid #003300;
                font-weight: 400;
            }}

            .footer {{
                text-align: center;
                color: #006600;
                margin-top: 30px;
                padding: 20px;
                background: rgba(0, 10, 0, 0.8);
                border: 1px solid #002200;
                font-size: 0.8em;
            }}

            .scroll-container {{
                overflow-x: auto;
                margin: 15px 0;
                border: 1px solid #003300;
                padding: 5px;
                background: rgba(0, 5, 0, 0.5);
            }}

            .scroll-table {{
                min-width: 1200px;
            }}

            .task-manager-table {{
                min-width: 1500px;
            }}

            .performance-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }}

            .performance-card {{
                background: rgba(0, 20, 0, 0.6);
                padding: 15px;
                border: 1px solid #003300;
                position: relative;
                overflow: hidden;
            }}

            .performance-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 3px;
                height: 100%;
                background: #00ff00;
            }}

            .performance-card h3 {{
                color: #00ff00;
                margin-bottom: 8px;
                font-size: 0.9em;
                font-weight: 500;
            }}

            .performance-value {{
                font-size: 1.5em;
                font-weight: 600;
                color: #00ff00;
                margin: 8px 0;
                text-shadow: 0 0 5px #00ff00;
            }}

            .performance-details {{
                color: #009900;
                font-size: 0.8em;
            }}

            .terminal-prompt {{
                color: #00ff00;
                margin-right: 5px;
            }}

            .blink {{
                animation: blink 1s infinite;
            }}

            @keyframes blink {{
                0%, 50% {{ opacity: 1; }}
                51%, 100% {{ opacity: 0; }}
            }}

            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}

                .header h1 {{
                    font-size: 1.8em;
                }}

                .performance-grid {{
                    grid-template-columns: 1fr;
                }}

                table {{
                    font-size: 0.75em;
                }}

                th, td {{
                    padding: 6px 8px;
                }}
            }}

            /* Matrix rain effect */
            .matrix-rain {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: -2;
                opacity: 0.1;
            }}

            /* Custom scrollbar */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}

            ::-webkit-scrollbar-track {{
                background: rgba(0, 10, 0, 0.8);
            }}

            ::-webkit-scrollbar-thumb {{
                background: #00ff00;
                border-radius: 0;
            }}

            ::-webkit-scrollbar-thumb:hover {{
                background: #00cc00;
            }}

            /* Typewriter effect for headers */
            .typewriter {{
                overflow: hidden;
                border-right: 2px solid #00ff00;
                white-space: nowrap;
                animation: typing 3.5s steps(40, end), blink-caret 0.75s step-end infinite;
            }}

            @keyframes typing {{
                from {{ width: 0 }}
                to {{ width: 100% }}
            }}

            @keyframes blink-caret {{
                from, to {{ border-color: transparent }}
                50% {{ border-color: #00ff00 }}
            }}
        </style>
    </head>
    <body>
        <div class="matrix-bg"></div>
        <div class="scan-line"></div>
        <div class="matrix-rain" id="matrixRain"></div>

        <div class="container">
            <div class="header">
                <h1>><span class="blink">_</span> SYSTEM SCAN REPORT</h1>
                <p>> SCAN INITIATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>> TARGET: {socket.gethostname()} | PLATFORM: {platform.platform()}</p>
                <div class="health-score">
                    SYSTEM_INTEGRITY: {get_system_health_score()}/100
                </div>
            </div>
    """

    # Add each section to HTML
    for section_name, data in sections_data.items():
        html_content += f"""
            <div class="section">
                <h2>> {section_name}</h2>
        """

        if data:
            if section_name in ["NETWORK ANALYSIS", "TASK MANAGER - RUNNING PROCESSES"]:
                # Special handling for wide tables with scrolling
                table_class = "task-manager-table" if "TASK MANAGER" in section_name else "scroll-table"
                html_content += f'<div class="scroll-container"><table class="{table_class}">'
            elif section_name == "SYSTEM PERFORMANCE":
                # Performance metrics in grid layout
                html_content += '<div class="performance-grid">'
                for item in data:
                    html_content += f'''
                    <div class="performance-card">
                        <h3>> {item["Metric"]}</h3>
                        <div class="performance-value">{item["Value"]}</div>
                        <div class="performance-details">>{item["Details"]}</div>
                    </div>
                    '''
                html_content += '</div>'
            else:
                html_content += '<table>'

            if section_name != "SYSTEM PERFORMANCE":
                if isinstance(data[0], dict):
                    # Table data
                    headers = list(data[0].keys())
                    rows = [[row.get(header, '') for header in headers] for row in data]

                    html_content += '<thead><tr>' + ''.join(
                        f'<th>{header}</th>' for header in headers) + '</tr></thead>'
                    html_content += '<tbody>'
                    for row in rows:
                        # Add status classes for specific columns
                        row_html = '<tr>'
                        for i, cell in enumerate(row):
                            cell_str = str(cell)
                            if headers[i] in ["Status", "Account Active", "Health"]:
                                if any(x in cell_str.lower() for x in
                                       ["active", "yes", "healthy", "connected", "running"]):
                                    row_html += f'<td class="status-active">{cell}</td>'
                                elif any(x in cell_str.lower() for x in
                                         ["inactive", "no", "error", "disconnected", "stopped"]):
                                    row_html += f'<td class="status-inactive">{cell}</td>'
                                elif any(x in cell_str.lower() for x in ["warning", "caution"]):
                                    row_html += f'<td class="status-warning">{cell}</td>'
                                else:
                                    row_html += f'<td>{cell}</td>'
                            elif "password" in headers[i].lower() and cell_str != "Not stored or encrypted":
                                row_html += f'<td class="status-active">{cell}</td>'
                            else:
                                row_html += f'<td>{cell}</td>'
                        row_html += '</tr>'
                        html_content += row_html
                    html_content += '</tbody></table>'
                else:
                    # Key-value data
                    for item in data:
                        if len(item) == 2:
                            html_content += f'<tr><td><span class="terminal-prompt">></span> {item[0]}</td><td class="metric-value">{item[1]}</td></tr>'
                    html_content += '</table>'

            if section_name in ["NETWORK ANALYSIS", "TASK MANAGER - RUNNING PROCESSES"]:
                html_content += '</div>'
        else:
            html_content += '<p style="color: #006600; text-align: center; padding: 20px;">> NO_DATA_AVAILABLE</p>'

        html_content += '</div>'

    html_content += """
            <div class="footer">
                <p>> SCAN_COMPLETED: """ + datetime.now().strftime('%H:%M:%S') + """</p>
                <p>> SYSTEM_SCAN_V1.0 | DATA_COLLECTION: UNLIMITED | SECURITY_LEVEL: MAXIMUM</p>
            </div>
        </div>

        <script>
            // Matrix rain effect
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.classList.add('matrix-rain');
            document.getElementById('matrixRain').appendChild(canvas);

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const chars = "01";
            const charSize = 14;
            const columns = canvas.width / charSize;
            const drops = [];

            for (let i = 0; i < columns; i++) {
                drops[i] = 1;
            }

            function drawMatrix() {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#00ff00';
                ctx.font = charSize + 'px JetBrains Mono';

                for (let i = 0; i < drops.length; i++) {
                    const text = chars[Math.floor(Math.random() * chars.length)];
                    ctx.fillText(text, i * charSize, drops[i] * charSize);

                    if (drops[i] * charSize > canvas.height && Math.random() > 0.975) {
                        drops[i] = 0;
                    }
                    drops[i]++;
                }
            }

            setInterval(drawMatrix, 35);

            // Terminal typing effect
            document.addEventListener('DOMContentLoaded', function() {
                const elements = document.querySelectorAll('.section h2');
                elements.forEach((element, index) => {
                    setTimeout(() => {
                        element.style.animation = 'typing 2s steps(40, end), blink-caret 0.75s step-end infinite';
                    }, index * 200);
                });

                // Add interactive features to tables
                const tables = document.querySelectorAll('table');
                tables.forEach(table => {
                    const headers = table.querySelectorAll('th');
                    headers.forEach((header, index) => {
                        header.style.cursor = 'pointer';
                        header.title = 'Click to sort';
                        header.addEventListener('click', () => {
                            sortTable(table, index);
                        });
                    });
                });

                function sortTable(table, column) {
                    const tbody = table.querySelector('tbody');
                    const rows = Array.from(tbody.querySelectorAll('tr'));

                    const isNumeric = (text) => !isNaN(parseFloat(text)) && isFinite(text);

                    rows.sort((a, b) => {
                        const aText = a.cells[column].textContent.trim();
                        const bText = b.cells[column].textContent.trim();

                        if (isNumeric(aText) && isNumeric(bText)) {
                            return parseFloat(aText) - parseFloat(bText);
                        }

                        return aText.localeCompare(bText);
                    });

                    // Remove existing rows
                    rows.forEach(row => tbody.removeChild(row));

                    // Add sorted rows
                    rows.forEach(row => tbody.appendChild(row));
                }

                // Add pulse effect to health score
                const healthScore = document.querySelector('.health-score');
                setInterval(() => {
                    healthScore.style.boxShadow = '0 0 20px rgba(0, 255, 0, 0.5)';
                    setTimeout(() => {
                        healthScore.style.boxShadow = 'none';
                    }, 500);
                }, 2000);
            });

            // Handle window resize
            window.addEventListener('resize', function() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            });
        </script>
    </body>
    </html>
    """

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("[+] HTML report generated successfully!")
    print(f"[+] Location: {html_path}")
    print("[+] Opening in default browser...")

    # Try to open the file in default browser
    try:
        if platform.system() == "Windows":
            os.startfile(html_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", html_path])
        else:  # Linux
            subprocess.run(["xdg-open", html_path])
    except:
        print("[!] Could not open browser automatically. Please open the file manually.")

    return html_path


def get_health_color():
    score = get_system_health_score()
    if score >= 80:
        return "linear-gradient(135deg, #00ff00 0%, #00cc00 100%)"
    elif score >= 60:
        return "linear-gradient(135deg, #ffff00 0%, #cccc00 100%)"
    else:
        return "linear-gradient(135deg, #ff0000 0%, #cc0000 100%)"


# -------------------------------------------------------------------
#  MAIN EXECUTION WITH ENHANCED UI
# -------------------------------------------------------------------
if __name__ == "__main__":
    g_pwd(p, w, e, t, s, r, a, g, y, f)
    print("\n\n\n")
    print_colored("╔══════════════════════════════════════════════════════════════╗", Colors.GREEN)
    print_colored("║                    SYSTEM SCAN INITIATED                     ║", Colors.GREEN)
    print_colored("║             ... Advanced Intelligence Scanner ...            ║", Colors.CYAN)
    print_colored("╚══════════════════════════════════════════════════════════════╝", Colors.GREEN)
    print()

    print_status("Initializing scanner modules...", "INFO")
    time.sleep(1)

    try:
        html_path = generate_html_report()

        print()
        print_colored("╔══════════════════════════════════════════════════════════════╗", Colors.GREEN)
        print_colored("║                       SCAN COMPLETED                         ║", Colors.GREEN)
        print_colored("╚══════════════════════════════════════════════════════════════╝", Colors.GREEN)
        print()

        print_status("REPORT GENERATION SUMMARY:", "SUCCESS")
        print_status(f"Output File: {html_path}", "DATA")
        print_status("System Health Score: " + str(get_system_health_score()) + "/100",
                     "SUCCESS" if get_system_health_score() >= 70 else "WARNING")
        print()

        print_status("SECTIONS INCLUDED:", "INFO")
        sections = [
            "SYSTEM OVERVIEW", "STORAGE ANALYSIS", "GRAPHICS CARD INFORMATION",
            "NETWORK ANALYSIS", "WIFI SECURITY ANALYSIS", "USER ACCOUNTS",
            "ADVANCED SYSTEM DETAILS", "SYSTEM PERFORMANCE", "TASK MANAGER"
        ]
        for section in sections:
            print_colored(f"    ✓ {section}", Colors.GREEN)

        print()
        print_status("Opening report in default browser...", "INFO")


    except Exception as e:
        print_status(f"SCAN FAILED: {str(e)}", "ERROR")

        print_status("Please ensure you have necessary permissions", "WARNING")

